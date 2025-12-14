"""
API routes for Atom operations
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
import logging

from src.api.models import AtomCreate, AtomResponse, PaginatedResponse, ErrorResponse
from src.kg.database import Neo4jDatabase
from src.utils.exceptions import ResourceNotFoundError, ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=AtomResponse, status_code=201)
async def create_atom(atom: AtomCreate, request: Request):
    """
    Create a new atom

    Args:
        atom: Atom data
        request: FastAPI request object

    Returns:
        Created atom
    """
    try:
        db: Neo4jDatabase = request.app.state.db

        # Convert Pydantic model to dict
        atom_data = atom.model_dump()

        # Create atom in Knowledge Graph
        query = """
        CREATE (a:Atom $props)
        RETURN a
        """

        result = await db.execute_write_query(
            query,
            {"props": atom_data}
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create atom")

        logger.info(f"Created atom: {atom.id}")
        return AtomResponse(**result[0]["a"])

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating atom: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[AtomResponse])
async def list_atoms(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    owner: Optional[str] = None,
    tags: Optional[str] = None
):
    """
    List all atoms with optional filtering

    Args:
        request: FastAPI request object
        skip: Number of records to skip
        limit: Maximum number of records to return
        owner: Filter by owner email
        tags: Comma-separated list of tags

    Returns:
        List of atoms
    """
    try:
        db: Neo4jDatabase = request.app.state.db

        # Build query with filters
        where_clauses = []
        params = {"skip": skip, "limit": limit}

        if owner:
            where_clauses.append("a.owner = $owner")
            params["owner"] = owner

        if tags:
            tag_list = tags.split(",")
            where_clauses.append("ANY(tag IN $tags WHERE tag IN a.tags)")
            params["tags"] = tag_list

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"""
        MATCH (a:Atom)
        WHERE {where_clause}
        RETURN a
        ORDER BY a.created_at DESC
        SKIP $skip
        LIMIT $limit
        """

        results = await db.execute_query(query, params)

        atoms = [AtomResponse(**r["a"]) for r in results]
        return atoms

    except Exception as e:
        logger.error(f"Error listing atoms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{atom_id}", response_model=AtomResponse)
async def get_atom(atom_id: str, request: Request):
    """
    Get a specific atom by ID

    Args:
        atom_id: Atom identifier
        request: FastAPI request object

    Returns:
        Atom data
    """
    try:
        db: Neo4jDatabase = request.app.state.db
        atom = await db.get_atom(atom_id)

        if not atom:
            raise HTTPException(status_code=404, detail=f"Atom {atom_id} not found")

        return AtomResponse(**atom)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting atom {atom_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{atom_id}", response_model=AtomResponse)
async def update_atom(atom_id: str, atom: AtomCreate, request: Request):
    """
    Update an existing atom

    Args:
        atom_id: Atom identifier
        atom: Updated atom data
        request: FastAPI request object

    Returns:
        Updated atom
    """
    try:
        db: Neo4jDatabase = request.app.state.db

        # Check if atom exists
        existing = await db.get_atom(atom_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Atom {atom_id} not found")

        # Update atom
        atom_data = atom.model_dump()

        query = """
        MATCH (a:Atom {id: $atom_id})
        SET a += $props
        RETURN a
        """

        result = await db.execute_write_query(
            query,
            {"atom_id": atom_id, "props": atom_data}
        )

        logger.info(f"Updated atom: {atom_id}")
        return AtomResponse(**result[0]["a"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating atom {atom_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{atom_id}", status_code=204)
async def delete_atom(atom_id: str, request: Request):
    """
    Delete an atom

    Args:
        atom_id: Atom identifier
        request: FastAPI request object
    """
    try:
        db: Neo4jDatabase = request.app.state.db

        # Check if atom exists
        existing = await db.get_atom(atom_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Atom {atom_id} not found")

        # Check if atom is used in molecules or workflows
        check_query = """
        MATCH (m:Molecule)-[:COMPOSES]->(a:Atom {id: $atom_id})
        RETURN count(m) as molecule_count
        UNION
        MATCH (w:Workflow)-[:COMPOSES]->(a:Atom {id: $atom_id})
        RETURN count(w) as workflow_count
        """

        usage_results = await db.execute_query(check_query, {"atom_id": atom_id})
        if usage_results and any(r.get("molecule_count", 0) > 0 or r.get("workflow_count", 0) > 0 for r in usage_results):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete atom: it is used in molecules or workflows"
            )

        # Delete atom
        delete_query = """
        MATCH (a:Atom {id: $atom_id})
        DETACH DELETE a
        """

        await db.execute_write_query(delete_query, {"atom_id": atom_id})

        logger.info(f"Deleted atom: {atom_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting atom {atom_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{atom_id}/dependencies", response_model=dict)
async def get_atom_dependencies(atom_id: str, request: Request):
    """
    Get all molecules and workflows that depend on this atom

    Args:
        atom_id: Atom identifier
        request: FastAPI request object

    Returns:
        Dictionary with molecules and workflows
    """
    try:
        db: Neo4jDatabase = request.app.state.db

        query = """
        MATCH (a:Atom {id: $atom_id})
        OPTIONAL MATCH (m:Molecule)-[:COMPOSES]->(a)
        OPTIONAL MATCH (w:Workflow)-[:COMPOSES]->(a)
        RETURN a,
               collect(DISTINCT m) as molecules,
               collect(DISTINCT w) as workflows
        """

        result = await db.execute_query(query, {"atom_id": atom_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Atom {atom_id} not found")

        return {
            "atom_id": atom_id,
            "molecules": [m.get("id") for m in result[0]["molecules"] if m],
            "workflows": [w.get("id") for w in result[0]["workflows"] if w]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dependencies for atom {atom_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
