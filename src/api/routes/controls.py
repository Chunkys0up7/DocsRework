"""
API routes for Control operations
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from datetime import datetime

from ..models import ControlCreate, ControlResponse, ControlType
from ...kg.database import Neo4jDatabase

router = APIRouter()


@router.post("/", response_model=ControlResponse, status_code=201)
async def create_control(control: ControlCreate, request: Request):
    """Create a new control"""
    db: Neo4jDatabase = request.app.state.db

    # Convert to dict and add metadata
    control_data = control.model_dump()
    control_data["created_at"] = datetime.utcnow().isoformat()
    control_data["updated_at"] = datetime.utcnow().isoformat()

    # Create control node
    query = """
    CREATE (c:Control $props)
    RETURN c
    """

    try:
        result = await db.execute_write_query(query, {"props": control_data})
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create control")

        return ControlResponse(**result[0]["c"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ControlResponse])
async def list_controls(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    owner: Optional[str] = None,
    control_type: Optional[ControlType] = None,
    min_effectiveness: Optional[int] = None
):
    """List all controls with optional filtering"""
    db: Neo4jDatabase = request.app.state.db

    # Build query with filters
    where_clauses = []
    params = {"skip": skip, "limit": limit}

    if owner:
        where_clauses.append("c.owner = $owner")
        params["owner"] = owner

    if control_type:
        where_clauses.append("c.controlType = $controlType")
        params["controlType"] = control_type.value

    if min_effectiveness is not None:
        where_clauses.append("c.effectiveness.rating >= $minEffectiveness")
        params["minEffectiveness"] = min_effectiveness

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = f"""
    MATCH (c:Control)
    WHERE {where_clause}
    RETURN c
    ORDER BY c.effectiveness.rating DESC, c.created_at DESC
    SKIP $skip
    LIMIT $limit
    """

    try:
        result = await db.execute_read_query(query, params)
        return [ControlResponse(**record["c"]) for record in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{control_id}", response_model=ControlResponse)
async def get_control(control_id: str, request: Request):
    """Get a specific control by ID"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (c:Control {id: $id})
    RETURN c
    """

    try:
        result = await db.execute_read_query(query, {"id": control_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Control {control_id} not found")

        return ControlResponse(**result[0]["c"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{control_id}", response_model=ControlResponse)
async def update_control(control_id: str, control: ControlCreate, request: Request):
    """Update an existing control"""
    db: Neo4jDatabase = request.app.state.db

    # Check if control exists
    check_query = "MATCH (c:Control {id: $id}) RETURN c"
    existing = await db.execute_read_query(check_query, {"id": control_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")

    # Update control
    control_data = control.model_dump()
    control_data["updated_at"] = datetime.utcnow().isoformat()

    query = """
    MATCH (c:Control {id: $id})
    SET c += $props
    RETURN c
    """

    try:
        result = await db.execute_write_query(query, {"id": control_id, "props": control_data})
        return ControlResponse(**result[0]["c"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{control_id}", status_code=204)
async def delete_control(control_id: str, request: Request):
    """Delete a control"""
    db: Neo4jDatabase = request.app.state.db

    # Check if control exists
    check_query = "MATCH (c:Control {id: $id}) RETURN c"
    existing = await db.execute_read_query(check_query, {"id": control_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")

    # Check if control is referenced by any artifacts
    usage_query = """
    MATCH (n)-[:HAS_CONTROL]->(c:Control {id: $id})
    RETURN labels(n)[0] as type, count(n) as count
    """
    usage = await db.execute_read_query(usage_query, {"id": control_id})

    if usage and any(u["count"] > 0 for u in usage):
        references = ", ".join([f"{u['count']} {u['type']}(s)" for u in usage if u["count"] > 0])
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete control {control_id}: referenced by {references}"
        )

    # Delete control and its relationships
    query = """
    MATCH (c:Control {id: $id})
    DETACH DELETE c
    """

    try:
        await db.execute_write_query(query, {"id": control_id})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{control_id}/mitigated-risks", response_model=dict)
async def get_mitigated_risks(control_id: str, request: Request):
    """Get all risks mitigated by this control"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (c:Control {id: $id})
    OPTIONAL MATCH (c)-[:MITIGATES]->(r:Risk)
    RETURN c,
           collect(DISTINCT r) as risks
    """

    try:
        result = await db.execute_read_query(query, {"id": control_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Control {control_id} not found")

        record = result[0]
        return {
            "control": record["c"],
            "mitigatedRisks": record["risks"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{control_id}/applied-processes", response_model=dict)
async def get_applied_processes(control_id: str, request: Request):
    """Get all processes where this control is applied"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (c:Control {id: $id})
    OPTIONAL MATCH (a:Atom)-[:HAS_CONTROL]->(c)
    OPTIONAL MATCH (m:Molecule)-[:HAS_CONTROL]->(c)
    OPTIONAL MATCH (w:Workflow)-[:HAS_CONTROL]->(c)
    RETURN c,
           collect(DISTINCT a.id) as atoms,
           collect(DISTINCT m.id) as molecules,
           collect(DISTINCT w.id) as workflows
    """

    try:
        result = await db.execute_read_query(query, {"id": control_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Control {control_id} not found")

        record = result[0]
        return {
            "control": record["c"],
            "appliedAtoms": [a for a in record["atoms"] if a],
            "appliedMolecules": [m for m in record["molecules"] if m],
            "appliedWorkflows": [w for w in record["workflows"] if w]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
