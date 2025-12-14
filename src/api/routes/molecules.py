"""
API routes for Molecule operations
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from datetime import datetime

from ..models import MoleculeCreate, MoleculeResponse
from ...kg.database import Neo4jDatabase

router = APIRouter()


@router.post("/", response_model=MoleculeResponse, status_code=201)
async def create_molecule(molecule: MoleculeCreate, request: Request):
    """Create a new molecule"""
    db: Neo4jDatabase = request.app.state.db

    # Convert to dict and add metadata
    molecule_data = molecule.model_dump()
    molecule_data["created_at"] = datetime.utcnow().isoformat()
    molecule_data["updated_at"] = datetime.utcnow().isoformat()

    # Create molecule node
    query = """
    CREATE (m:Molecule $props)
    RETURN m
    """

    try:
        result = await db.execute_write_query(query, {"props": molecule_data})
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create molecule")

        return MoleculeResponse(**result[0]["m"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[MoleculeResponse])
async def list_molecules(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    owner: Optional[str] = None,
    tag: Optional[str] = None
):
    """List all molecules with optional filtering"""
    db: Neo4jDatabase = request.app.state.db

    # Build query with filters
    where_clauses = []
    params = {"skip": skip, "limit": limit}

    if owner:
        where_clauses.append("m.owner = $owner")
        params["owner"] = owner

    if tag:
        where_clauses.append("$tag IN m.tags")
        params["tag"] = tag

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = f"""
    MATCH (m:Molecule)
    WHERE {where_clause}
    RETURN m
    ORDER BY m.created_at DESC
    SKIP $skip
    LIMIT $limit
    """

    try:
        result = await db.execute_read_query(query, params)
        return [MoleculeResponse(**record["m"]) for record in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{molecule_id}", response_model=MoleculeResponse)
async def get_molecule(molecule_id: str, request: Request):
    """Get a specific molecule by ID"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (m:Molecule {id: $id})
    RETURN m
    """

    try:
        result = await db.execute_read_query(query, {"id": molecule_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Molecule {molecule_id} not found")

        return MoleculeResponse(**result[0]["m"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{molecule_id}", response_model=MoleculeResponse)
async def update_molecule(molecule_id: str, molecule: MoleculeCreate, request: Request):
    """Update an existing molecule"""
    db: Neo4jDatabase = request.app.state.db

    # Check if molecule exists
    check_query = "MATCH (m:Molecule {id: $id}) RETURN m"
    existing = await db.execute_read_query(check_query, {"id": molecule_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Molecule {molecule_id} not found")

    # Update molecule
    molecule_data = molecule.model_dump()
    molecule_data["updated_at"] = datetime.utcnow().isoformat()

    query = """
    MATCH (m:Molecule {id: $id})
    SET m += $props
    RETURN m
    """

    try:
        result = await db.execute_write_query(query, {"id": molecule_id, "props": molecule_data})
        return MoleculeResponse(**result[0]["m"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{molecule_id}", status_code=204)
async def delete_molecule(molecule_id: str, request: Request):
    """Delete a molecule"""
    db: Neo4jDatabase = request.app.state.db

    # Check if molecule exists
    check_query = "MATCH (m:Molecule {id: $id}) RETURN m"
    existing = await db.execute_read_query(check_query, {"id": molecule_id})

    if not existing:
        raise HTTPException(status_code=404, detail=f"Molecule {molecule_id} not found")

    # Check if molecule is used in any workflows
    usage_query = """
    MATCH (w:Workflow)-[:COMPOSES]->(m:Molecule {id: $id})
    RETURN count(w) as workflow_count
    """
    usage = await db.execute_read_query(usage_query, {"id": molecule_id})

    if usage and usage[0]["workflow_count"] > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete molecule {molecule_id}: used in {usage[0]['workflow_count']} workflow(s)"
        )

    # Delete molecule and its relationships
    query = """
    MATCH (m:Molecule {id: $id})
    DETACH DELETE m
    """

    try:
        await db.execute_write_query(query, {"id": molecule_id})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{molecule_id}/dependencies", response_model=dict)
async def get_molecule_dependencies(molecule_id: str, request: Request):
    """Get molecule dependencies (atoms, risks, controls)"""
    db: Neo4jDatabase = request.app.state.db

    query = """
    MATCH (m:Molecule {id: $id})
    OPTIONAL MATCH (m)-[:USES_ATOM]->(a:Atom)
    OPTIONAL MATCH (m)-[:HAS_RISK]->(r:Risk)
    OPTIONAL MATCH (m)-[:HAS_CONTROL]->(c:Control)
    OPTIONAL MATCH (m)-[:COMPLIES_WITH]->(reg:Regulation)
    RETURN m,
           collect(DISTINCT a) as atoms,
           collect(DISTINCT r) as risks,
           collect(DISTINCT c) as controls,
           collect(DISTINCT reg) as regulations
    """

    try:
        result = await db.execute_read_query(query, {"id": molecule_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Molecule {molecule_id} not found")

        record = result[0]
        return {
            "molecule": record["m"],
            "atoms": record["atoms"],
            "risks": record["risks"],
            "controls": record["controls"],
            "regulations": record["regulations"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
