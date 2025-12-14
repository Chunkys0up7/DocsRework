"""
API routes for Risk operations
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from datetime import datetime

from ..models import RiskCreate, RiskResponse, RiskLevel
from ...kg.database import Neo4jDatabase
from ...risk_engine.calculator import RiskCalculator

router = APIRouter()


@router.post("/", response_model=RiskResponse, status_code=201)
async def create_risk(risk: RiskCreate, request: Request):
    """Create a new risk"""
    db: Neo4jDatabase = request.app.state.db

    # Convert to dict and add metadata
    risk_data = risk.model_dump()
    risk_data["created_at"] = datetime.utcnow().isoformat()
    risk_data["updated_at"] = datetime.utcnow().isoformat()

    # Calculate risk scores using Risk Engine
    inherent_score, inherent_level = RiskCalculator.calculate_inherent_risk(
        risk.likelihood.score,
        risk.impact.score
    )
    risk_data["inherentRisk"] = {
        "score": inherent_score,
        "level": inherent_level.value
    }

    # Calculate residual risk if controls are provided
    if risk.controls:
        residual_score, residual_level = RiskCalculator.calculate_residual_risk(
            inherent_score,
            risk.controls
        )
        risk_data["residualRisk"] = {
            "score": residual_score,
            "level": residual_level.value
        }

    # Create risk node
    query = """
    CREATE (r:Risk $props)
    RETURN r
    """

    try:
        result = await db.execute_write_query(query, {"props": risk_data})
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create risk")

        return RiskResponse(**result[0]["r"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[RiskResponse])
async def list_risks(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    owner: Optional[str] = None,
    level: Optional[RiskLevel] = None,
    category: Optional[str] = None
):
    """List all risks with optional filtering"""
    db: Neo4jDatabase = request.app.state.db

    # Build query with filters
    where_clauses = []
    params = {"skip": skip, "limit": limit}

    if owner:
        where_clauses.append("r.owner = $owner")
        params["owner"] = owner

    if level:
        where_clauses.append("r.inherentRisk.level = $level")
        params["level"] = level.value

    if category:
        where_clauses.append("r.category = $category")
        params["category"] = category

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = f"""
    MATCH (r:Risk)
    WHERE {where_clause}
    RETURN r
    ORDER BY r.inherentRisk.score DESC, r.created_at DESC
    SKIP $skip
    LIMIT $limit
    """

    try:
        result = await db.execute_read_query(query, params)
        return [RiskResponse(**record["r"]) for record in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(risk_id: str, request: Request):
    """Get a specific risk by ID"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (r:Risk {id: $id})
    RETURN r
    """

    try:
        result = await db.execute_read_query(query, {"id": risk_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

        return RiskResponse(**result[0]["r"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(risk_id: str, risk: RiskCreate, request: Request):
    """Update an existing risk"""
    db: Neo4jDatabase = request.app.state.db

    # Check if risk exists
    check_query = "MATCH (r:Risk {id: $id}) RETURN r"
    existing = await db.execute_read_query(check_query, {"id": risk_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    # Update risk
    risk_data = risk.model_dump()
    risk_data["updated_at"] = datetime.utcnow().isoformat()

    # Recalculate risk scores
    inherent_score, inherent_level = RiskCalculator.calculate_inherent_risk(
        risk.likelihood.score,
        risk.impact.score
    )
    risk_data["inherentRisk"] = {
        "score": inherent_score,
        "level": inherent_level.value
    }

    if risk.controls:
        residual_score, residual_level = RiskCalculator.calculate_residual_risk(
            inherent_score,
            risk.controls
        )
        risk_data["residualRisk"] = {
            "score": residual_score,
            "level": residual_level.value
        }

    query = """
    MATCH (r:Risk {id: $id})
    SET r += $props
    RETURN r
    """

    try:
        result = await db.execute_write_query(query, {"id": risk_id, "props": risk_data})
        return RiskResponse(**result[0]["r"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{risk_id}", status_code=204)
async def delete_risk(risk_id: str, request: Request):
    """Delete a risk"""
    db: Neo4jDatabase = request.app.state.db

    # Check if risk exists
    check_query = "MATCH (r:Risk {id: $id}) RETURN r"
    existing = await db.execute_read_query(check_query, {"id": risk_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    # Check if risk is referenced by any atoms/molecules/workflows
    usage_query = """
    MATCH (n)-[:HAS_RISK]->(r:Risk {id: $id})
    RETURN labels(n)[0] as type, count(n) as count
    """
    usage = await db.execute_read_query(usage_query, {"id": risk_id})

    if usage and any(u["count"] > 0 for u in usage):
        references = ", ".join([f"{u['count']} {u['type']}(s)" for u in usage if u["count"] > 0])
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete risk {risk_id}: referenced by {references}"
        )

    # Delete risk and its relationships
    query = """
    MATCH (r:Risk {id: $id})
    DETACH DELETE r
    """

    try:
        await db.execute_write_query(query, {"id": risk_id})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{risk_id}/affected-processes", response_model=dict)
async def get_affected_processes(risk_id: str, request: Request):
    """Get all processes affected by this risk"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (r:Risk {id: $id})
    OPTIONAL MATCH (a:Atom)-[:HAS_RISK]->(r)
    OPTIONAL MATCH (m:Molecule)-[:HAS_RISK]->(r)
    OPTIONAL MATCH (w:Workflow)-[:HAS_RISK]->(r)
    RETURN r,
           collect(DISTINCT a.id) as atoms,
           collect(DISTINCT m.id) as molecules,
           collect(DISTINCT w.id) as workflows
    """

    try:
        result = await db.execute_read_query(query, {"id": risk_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

        record = result[0]
        return {
            "risk": record["r"],
            "affectedAtoms": [a for a in record["atoms"] if a],
            "affectedMolecules": [m for m in record["molecules"] if m],
            "affectedWorkflows": [w for w in record["workflows"] if w]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{risk_id}/controls", response_model=dict)
async def get_risk_controls(risk_id: str, request: Request):
    """Get all controls mitigating this risk"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (r:Risk {id: $id})
    OPTIONAL MATCH (c:Control)-[:MITIGATES]->(r)
    RETURN r,
           collect(DISTINCT c) as controls
    """

    try:
        result = await db.execute_read_query(query, {"id": risk_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

        record = result[0]

        # Calculate control adequacy
        adequacy = RiskCalculator.calculate_control_adequacy(
            record["r"]["inherentRisk"]["score"],
            RiskLevel(record["r"]["inherentRisk"]["level"]),
            record["controls"]
        )

        return {
            "risk": record["r"],
            "controls": record["controls"],
            "adequacy": adequacy
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
