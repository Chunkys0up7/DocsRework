"""
API routes for Workflow operations
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
import logging

from src.api.models import WorkflowCreate, WorkflowResponse
from src.kg.database import Neo4jDatabase

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(workflow: WorkflowCreate, request: Request):
    """Create a new workflow"""
    try:
        db: Neo4jDatabase = request.app.state.db
        workflow_data = workflow.model_dump()

        query = """
        CREATE (w:Workflow $props)
        SET w.created_at = datetime(),
            w.updated_at = datetime()
        RETURN w
        """

        result = await db.execute_write_query(query, {"props": workflow_data})
        logger.info(f"Created workflow: {workflow.id}")
        return WorkflowResponse(**result[0]["w"])

    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    owner: Optional[str] = None
):
    """List all workflows with optional filtering"""
    try:
        db: Neo4jDatabase = request.app.state.db

        where_clauses = []
        params = {"skip": skip, "limit": limit}

        if owner:
            where_clauses.append("w.owner = $owner")
            params["owner"] = owner

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"""
        MATCH (w:Workflow)
        WHERE {where_clause}
        RETURN w
        ORDER BY w.created_at DESC
        SKIP $skip
        LIMIT $limit
        """

        results = await db.execute_query(query, params)
        return [WorkflowResponse(**r["w"]) for r in results]

    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, request: Request):
    """Get a specific workflow by ID"""
    try:
        db: Neo4jDatabase = request.app.state.db
        workflow = await db.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        return WorkflowResponse(**workflow)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, workflow: WorkflowCreate, request: Request):
    """Update an existing workflow"""
    try:
        db: Neo4jDatabase = request.app.state.db

        existing = await db.get_workflow(workflow_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        workflow_data = workflow.model_dump()

        query = """
        MATCH (w:Workflow {id: $workflow_id})
        SET w += $props,
            w.updated_at = datetime()
        RETURN w
        """

        result = await db.execute_write_query(
            query,
            {"workflow_id": workflow_id, "props": workflow_data}
        )

        logger.info(f"Updated workflow: {workflow_id}")
        return WorkflowResponse(**result[0]["w"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str, request: Request):
    """Delete a workflow"""
    try:
        db: Neo4jDatabase = request.app.state.db

        existing = await db.get_workflow(workflow_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        query = """
        MATCH (w:Workflow {id: $workflow_id})
        DETACH DELETE w
        """

        await db.execute_write_query(query, {"workflow_id": workflow_id})
        logger.info(f"Deleted workflow: {workflow_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
