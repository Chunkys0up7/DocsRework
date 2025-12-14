"""
API routes for Regulation operations
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from datetime import datetime

from ..models import RegulationCreate, RegulationResponse
from ...kg.database import Neo4jDatabase

router = APIRouter()


@router.post("/", response_model=RegulationResponse, status_code=201)
async def create_regulation(regulation: RegulationCreate, request: Request):
    """Create a new regulation"""
    db: Neo4jDatabase = request.app.state.db

    # Convert to dict and add metadata
    regulation_data = regulation.model_dump()
    regulation_data["created_at"] = datetime.utcnow().isoformat()
    regulation_data["updated_at"] = datetime.utcnow().isoformat()

    # Create regulation node
    query = """
    CREATE (r:Regulation $props)
    RETURN r
    """

    try:
        result = await db.execute_write_query(query, {"props": regulation_data})
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create regulation")

        return RegulationResponse(**result[0]["r"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[RegulationResponse])
async def list_regulations(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    owner: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    category: Optional[str] = None
):
    """List all regulations with optional filtering"""
    db: Neo4jDatabase = request.app.state.db

    # Build query with filters
    where_clauses = []
    params = {"skip": skip, "limit": limit}

    if owner:
        where_clauses.append("r.owner = $owner")
        params["owner"] = owner

    if jurisdiction:
        where_clauses.append("$jurisdiction IN r.jurisdiction")
        params["jurisdiction"] = jurisdiction

    if category:
        where_clauses.append("r.category = $category")
        params["category"] = category

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = f"""
    MATCH (r:Regulation)
    WHERE {where_clause}
    RETURN r
    ORDER BY r.effectiveDate DESC, r.created_at DESC
    SKIP $skip
    LIMIT $limit
    """

    try:
        result = await db.execute_read_query(query, params)
        return [RegulationResponse(**record["r"]) for record in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{regulation_id}", response_model=RegulationResponse)
async def get_regulation(regulation_id: str, request: Request):
    """Get a specific regulation by ID"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (r:Regulation {id: $id})
    RETURN r
    """

    try:
        result = await db.execute_read_query(query, {"id": regulation_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Regulation {regulation_id} not found")

        return RegulationResponse(**result[0]["r"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{regulation_id}", response_model=RegulationResponse)
async def update_regulation(regulation_id: str, regulation: RegulationCreate, request: Request):
    """Update an existing regulation"""
    db: Neo4jDatabase = request.app.state.db

    # Check if regulation exists
    check_query = "MATCH (r:Regulation {id: $id}) RETURN r"
    existing = await db.execute_read_query(check_query, {"id": regulation_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Regulation {regulation_id} not found")

    # Update regulation
    regulation_data = regulation.model_dump()
    regulation_data["updated_at"] = datetime.utcnow().isoformat()

    query = """
    MATCH (r:Regulation {id: $id})
    SET r += $props
    RETURN r
    """

    try:
        result = await db.execute_write_query(query, {"id": regulation_id, "props": regulation_data})
        return RegulationResponse(**result[0]["r"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{regulation_id}", status_code=204)
async def delete_regulation(regulation_id: str, request: Request):
    """Delete a regulation"""
    db: Neo4jDatabase = request.app.state.db

    # Check if regulation exists
    check_query = "MATCH (r:Regulation {id: $id}) RETURN r"
    existing = await db.execute_read_query(check_query, {"id": regulation_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Regulation {regulation_id} not found")

    # Check if regulation is referenced by any artifacts
    usage_query = """
    MATCH (n)-[:COMPLIES_WITH]->(r:Regulation {id: $id})
    RETURN labels(n)[0] as type, count(n) as count
    """
    usage = await db.execute_read_query(usage_query, {"id": regulation_id})

    if usage and any(u["count"] > 0 for u in usage):
        references = ", ".join([f"{u['count']} {u['type']}(s)" for u in usage if u["count"] > 0])
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete regulation {regulation_id}: referenced by {references}"
        )

    # Delete regulation and its relationships
    query = """
    MATCH (r:Regulation {id: $id})
    DETACH DELETE r
    """

    try:
        await db.execute_write_query(query, {"id": regulation_id})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{regulation_id}/affected-processes", response_model=dict)
async def get_affected_processes(regulation_id: str, request: Request):
    """Get all processes affected by this regulation"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (r:Regulation {id: $id})
    OPTIONAL MATCH (a:Atom)-[:COMPLIES_WITH]->(r)
    OPTIONAL MATCH (m:Molecule)-[:COMPLIES_WITH]->(r)
    OPTIONAL MATCH (w:Workflow)-[:COMPLIES_WITH]->(r)
    RETURN r,
           collect(DISTINCT a.id) as atoms,
           collect(DISTINCT m.id) as molecules,
           collect(DISTINCT w.id) as workflows
    """

    try:
        result = await db.execute_read_query(query, {"id": regulation_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Regulation {regulation_id} not found")

        record = result[0]
        return {
            "regulation": record["r"],
            "affectedAtoms": [a for a in record["atoms"] if a],
            "affectedMolecules": [m for m in record["molecules"] if m],
            "affectedWorkflows": [w for w in record["workflows"] if w]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{regulation_id}/controls", response_model=dict)
async def get_regulation_controls(regulation_id: str, request: Request):
    """Get all controls implementing this regulation"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (r:Regulation {id: $id})
    OPTIONAL MATCH (c:Control)-[:IMPLEMENTS]->(r)
    RETURN r,
           collect(DISTINCT c) as controls
    """

    try:
        result = await db.execute_read_query(query, {"id": regulation_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Regulation {regulation_id} not found")

        record = result[0]

        # Calculate compliance coverage
        total_requirements = len(record["r"].get("requirements", []))
        implemented_controls = len(record["controls"])

        coverage = {
            "totalRequirements": total_requirements,
            "implementedControls": implemented_controls,
            "coveragePercentage": (implemented_controls / total_requirements * 100) if total_requirements > 0 else 0
        }

        return {
            "regulation": record["r"],
            "controls": record["controls"],
            "coverage": coverage
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{regulation_id}/risks", response_model=dict)
async def get_regulation_risks(regulation_id: str, request: Request):
    """Get all risks related to this regulation"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (r:Regulation {id: $id})
    OPTIONAL MATCH (risk:Risk)-[:GOVERNED_BY]->(r)
    RETURN r,
           collect(DISTINCT risk) as risks
    """

    try:
        result = await db.execute_read_query(query, {"id": regulation_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Regulation {regulation_id} not found")

        record = result[0]
        return {
            "regulation": record["r"],
            "relatedRisks": record["risks"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
