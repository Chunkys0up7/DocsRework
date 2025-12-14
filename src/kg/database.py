"""
Neo4j Knowledge Graph Database Connection and Management
"""

from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import Dict, List, Any, Optional
import logging
from src.config import settings

logger = logging.getLogger(__name__)


class Neo4jDatabase:
    """Neo4j database connection manager"""

    def __init__(self):
        self.driver: Optional[AsyncDriver] = None
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE

    async def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=settings.NEO4J_MAX_CONNECTION_LIFETIME,
                max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
                connection_acquisition_timeout=settings.NEO4J_CONNECTION_ACQUISITION_TIMEOUT
            )
            await self.verify_connection()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

    async def verify_connection(self):
        """Verify Neo4j connection is working"""
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run("RETURN 1 as num")
                await result.single()
        except Exception as e:
            logger.error(f"Neo4j connection verification failed: {e}")
            raise

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result dictionaries
        """
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, parameters or {})
            return [dict(record) async for record in result]

    async def execute_write_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a write query in a transaction

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result dictionaries
        """
        async with self.driver.session(database=self.database) as session:
            async def _execute_write(tx):
                result = await tx.run(query, parameters or {})
                return [dict(record) async for record in result]

            return await session.execute_write(_execute_write)

    async def initialize_schema(self):
        """Initialize Knowledge Graph schema with constraints and indexes"""
        logger.info("Initializing Neo4j schema...")

        constraints = [
            # Unique constraints
            "CREATE CONSTRAINT atom_id IF NOT EXISTS FOR (a:Atom) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT molecule_id IF NOT EXISTS FOR (m:Molecule) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT workflow_id IF NOT EXISTS FOR (w:Workflow) REQUIRE w.id IS UNIQUE",
            "CREATE CONSTRAINT risk_id IF NOT EXISTS FOR (r:Risk) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT control_id IF NOT EXISTS FOR (c:Control) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT regulation_id IF NOT EXISTS FOR (reg:Regulation) REQUIRE reg.id IS UNIQUE",
            "CREATE CONSTRAINT actor_email IF NOT EXISTS FOR (a:Actor) REQUIRE a.email IS UNIQUE",

            # Indexes for performance
            "CREATE INDEX atom_version IF NOT EXISTS FOR (a:Atom) ON (a.version)",
            "CREATE INDEX atom_owner IF NOT EXISTS FOR (a:Atom) ON (a.owner)",
            "CREATE INDEX atom_name IF NOT EXISTS FOR (a:Atom) ON (a.name)",
            "CREATE INDEX molecule_version IF NOT EXISTS FOR (m:Molecule) ON (m.version)",
            "CREATE INDEX molecule_owner IF NOT EXISTS FOR (m:Molecule) ON (m.owner)",
            "CREATE INDEX workflow_version IF NOT EXISTS FOR (w:Workflow) ON (w.version)",
            "CREATE INDEX workflow_owner IF NOT EXISTS FOR (w:Workflow) ON (w.owner)",
            "CREATE INDEX risk_category IF NOT EXISTS FOR (r:Risk) ON (r.category)",
            "CREATE INDEX risk_level IF NOT EXISTS FOR (r:Risk) ON (r.inherentRisk.level)",
            "CREATE INDEX control_type IF NOT EXISTS FOR (c:Control) ON (c.controlType)",
            "CREATE INDEX control_effectiveness IF NOT EXISTS FOR (c:Control) ON (c.effectiveness.rating)",
            "CREATE INDEX regulation_jurisdiction IF NOT EXISTS FOR (reg:Regulation) ON (reg.jurisdiction)",
        ]

        for constraint in constraints:
            try:
                await self.execute_write_query(constraint)
                logger.info(f"Created: {constraint[:50]}...")
            except Exception as e:
                logger.warning(f"Constraint may already exist: {e}")

        logger.info("Schema initialization complete")

    async def get_atom(self, atom_id: str) -> Optional[Dict[str, Any]]:
        """Get atom by ID"""
        query = """
        MATCH (a:Atom {id: $atom_id})
        RETURN a
        """
        results = await self.execute_query(query, {"atom_id": atom_id})
        return results[0]["a"] if results else None

    async def get_molecule(self, molecule_id: str) -> Optional[Dict[str, Any]]:
        """Get molecule by ID"""
        query = """
        MATCH (m:Molecule {id: $molecule_id})
        RETURN m
        """
        results = await self.execute_query(query, {"molecule_id": molecule_id})
        return results[0]["m"] if results else None

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        query = """
        MATCH (w:Workflow {id: $workflow_id})
        RETURN w
        """
        results = await self.execute_query(query, {"workflow_id": workflow_id})
        return results[0]["w"] if results else None

    async def get_workflow_with_components(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow with all components and relationships"""
        query = """
        MATCH (w:Workflow {id: $workflow_id})
        OPTIONAL MATCH (w)-[r:COMPOSES]->(component)
        OPTIONAL MATCH (w)-[:HAS_RISK]->(risk:Risk)
        OPTIONAL MATCH (w)-[:HAS_CONTROL]->(control:Control)
        RETURN w, collect(DISTINCT component) as components,
               collect(DISTINCT risk) as risks,
               collect(DISTINCT control) as controls
        """
        results = await self.execute_query(query, {"workflow_id": workflow_id})
        return results[0] if results else None

    async def calculate_workflow_risk_score(self, workflow_id: str) -> float:
        """Calculate aggregate risk score for a workflow"""
        query = """
        MATCH (w:Workflow {id: $workflow_id})-[:HAS_RISK]->(r:Risk)
        RETURN sum(r.residualRisk.score) as total_risk_score
        """
        results = await self.execute_query(query, {"workflow_id": workflow_id})
        return results[0]["total_risk_score"] if results else 0.0

    async def find_circular_dependencies(self, entity_type: str) -> List[List[str]]:
        """Find circular dependencies in workflows, molecules, or atoms"""
        query = f"""
        MATCH path = (n:{entity_type})-[:DEPENDS_ON|COMPOSES*]->(n)
        RETURN [node in nodes(path) | node.id] as cycle
        """
        results = await self.execute_query(query)
        return [r["cycle"] for r in results]

    async def get_unmitigated_risks(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Find high risks without adequate controls"""
        query = """
        MATCH (r:Risk)
        WHERE r.residualRisk.score >= $threshold
        AND NOT (r)<-[:MITIGATES]-(:Control)
        RETURN r
        """
        results = await self.execute_query(query, {"threshold": threshold})
        return [r["r"] for r in results]

    async def get_compliance_coverage(self, regulation_id: str) -> Dict[str, Any]:
        """Calculate compliance coverage for a regulation"""
        query = """
        MATCH (reg:Regulation {id: $regulation_id})
        WITH reg, size(reg.requirements) as total_requirements
        MATCH (reg)<-[a:ADDRESSES]-(c:Control)
        WITH reg, total_requirements, count(DISTINCT c) as covered_controls,
             avg(a.coverage) as avg_coverage
        RETURN reg.id as regulation_id,
               total_requirements,
               covered_controls,
               avg_coverage as coverage_percentage
        """
        results = await self.execute_query(query, {"regulation_id": regulation_id})
        return results[0] if results else {}
