"""
FastAPI Main Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import logging
import time

from src.api.routes import atoms, molecules, workflows, risks, controls, regulations
from src.api.routes import ingestion, validation, deployment, analytics
from src.config import settings
from src.kg.database import Neo4jDatabase
from src.utils.logging import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")

    # Initialize Neo4j connection
    db = Neo4jDatabase()
    await db.connect()
    app.state.db = db

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application")
    await db.close()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Ontology-driven Docs-as-Code platform for banking documentation",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers
app.include_router(atoms.router, prefix="/api/v1/atoms", tags=["Atoms"])
app.include_router(molecules.router, prefix="/api/v1/molecules", tags=["Molecules"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(risks.router, prefix="/api/v1/risks", tags=["Risks"])
app.include_router(controls.router, prefix="/api/v1/controls", tags=["Controls"])
app.include_router(regulations.router, prefix="/api/v1/regulations", tags=["Regulations"])
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
app.include_router(deployment.router, prefix="/api/v1/deployment", tags=["Deployment"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


# Prometheus metrics endpoint
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.APP_ENV
    }


@app.get("/ready")
async def readiness_check(request: Request):
    """Readiness probe for Kubernetes"""
    try:
        # Check Neo4j connection
        db: Neo4jDatabase = request.app.state.db
        await db.verify_connection()

        return {
            "status": "ready",
            "checks": {
                "database": "ok"
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        workers=settings.API_WORKERS if not settings.API_RELOAD else 1,
        log_level=settings.LOG_LEVEL.lower()
    )
