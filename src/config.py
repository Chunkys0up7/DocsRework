"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Banking Docs-as-Code"
    VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    API_RELOAD: bool = Field(default=False, env="API_RELOAD")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )

    # Neo4j Configuration
    NEO4J_URI: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", env="NEO4J_PASSWORD")
    NEO4J_DATABASE: str = Field(default="banking-docs", env="NEO4J_DATABASE")
    NEO4J_MAX_CONNECTION_LIFETIME: int = Field(default=3600, env="NEO4J_MAX_CONNECTION_LIFETIME")
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=50, env="NEO4J_MAX_CONNECTION_POOL_SIZE")
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT: int = Field(default=60, env="NEO4J_CONNECTION_ACQUISITION_TIMEOUT")

    # Redis Configuration
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field(default="", env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_SSL: bool = Field(default=False, env="REDIS_SSL")

    # RabbitMQ Configuration
    RABBITMQ_HOST: str = Field(default="localhost", env="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(default=5672, env="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field(default="guest", env="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field(default="guest", env="RABBITMQ_PASSWORD")
    RABBITMQ_VHOST: str = Field(default="/", env="RABBITMQ_VHOST")

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="change-me-in-production", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_MINUTES: int = Field(default=30, env="JWT_EXPIRATION_MINUTES")
    ENCRYPTION_KEY: str = Field(default="change-me-32-bytes-key-here", env="ENCRYPTION_KEY")

    # Authentication
    ENABLE_AUTH: bool = Field(default=True, env="ENABLE_AUTH")
    AUTH_PROVIDER: str = Field(default="internal", env="AUTH_PROVIDER")

    # NLP Services
    NLP_MODEL_PATH: str = Field(default="./models/", env="NLP_MODEL_PATH")
    SPACY_MODEL: str = Field(default="en_core_web_lg", env="SPACY_MODEL")
    TRANSFORMER_MODEL: str = Field(default="bert-base-uncased", env="TRANSFORMER_MODEL")

    # OCR Services
    TESSERACT_CMD: str = Field(default="/usr/bin/tesseract", env="TESSERACT_CMD")
    OCR_LANGUAGE: str = Field(default="eng", env="OCR_LANGUAGE")

    # LLM Services
    LLM_PROVIDER: str = Field(default="anthropic", env="LLM_PROVIDER")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    LLM_MODEL: str = Field(default="claude-3-sonnet-20240229", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.0, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=4096, env="LLM_MAX_TOKENS")

    # Storage
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    TEMP_DIR: str = Field(default="./tmp", env="TEMP_DIR")
    DOCUMENT_STORAGE_PATH: str = Field(default="./documents", env="DOCUMENT_STORAGE_PATH")
    MAX_UPLOAD_SIZE: int = Field(default=52428800, env="MAX_UPLOAD_SIZE")  # 50MB

    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    ENABLE_TRACING: bool = Field(default=False, env="ENABLE_TRACING")

    # Risk Engine
    RISK_CALCULATION_INTERVAL: int = Field(default=3600, env="RISK_CALCULATION_INTERVAL")
    RISK_THRESHOLD_CRITICAL: int = Field(default=17, env="RISK_THRESHOLD_CRITICAL")
    RISK_THRESHOLD_HIGH: int = Field(default=10, env="RISK_THRESHOLD_HIGH")
    RISK_THRESHOLD_MEDIUM: int = Field(default=5, env="RISK_THRESHOLD_MEDIUM")

    # Compliance
    COMPLIANCE_CHECK_FREQUENCY: str = Field(default="daily", env="COMPLIANCE_CHECK_FREQUENCY")
    MIN_CONTROL_EFFECTIVENESS: int = Field(default=70, env="MIN_CONTROL_EFFECTIVENESS")
    MIN_REGULATION_COVERAGE: int = Field(default=95, env="MIN_REGULATION_COVERAGE")

    # Workflow Execution
    MAX_WORKFLOW_DURATION: int = Field(default=7200, env="MAX_WORKFLOW_DURATION")
    WORKFLOW_TIMEOUT_CHECK_INTERVAL: int = Field(default=60, env="WORKFLOW_TIMEOUT_CHECK_INTERVAL")
    ENABLE_PARALLEL_EXECUTION: bool = Field(default=True, env="ENABLE_PARALLEL_EXECUTION")
    MAX_PARALLEL_TASKS: int = Field(default=10, env="MAX_PARALLEL_TASKS")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.DOCUMENT_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.NLP_MODEL_PATH, exist_ok=True)
