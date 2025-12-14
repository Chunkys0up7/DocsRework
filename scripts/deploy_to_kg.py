#!/usr/bin/env python3
"""
Deploy validated artifacts to Neo4j Knowledge Graph
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

import yaml
from neo4j import AsyncGraphDatabase

from utils.logging import setup_logger
from utils.exceptions import ValidationError

logger = setup_logger(__name__)


class KnowledgeGraphDeployer:
    """Deploy artifacts to Neo4j Knowledge Graph"""

    def __init__(self, uri: str, username: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
        self.deployment_stats = {
            "atoms": {"deployed": 0, "failed": 0},
            "molecules": {"deployed": 0, "failed": 0},
            "workflows": {"deployed": 0, "failed": 0},
            "risks": {"deployed": 0, "failed": 0},
            "controls": {"deployed": 0, "failed": 0},
            "regulations": {"deployed": 0, "failed": 0},
        }

    async def close(self):
        await self.driver.close()

    async def deploy_atom(self, atom_data: Dict) -> bool:
        """Deploy atom to KG"""
        try:
            async with self.driver.session() as session:
                # Create or update atom node
                query = """
                MERGE (a:Atom {id: $id})
                SET a += $props
                RETURN a
                """
                await session.run(query, {
                    "id": atom_data["id"],
                    "props": atom_data
                })

                # Create relationships to risks
                for risk_id in atom_data.get("risks", []):
                    risk_query = """
                    MATCH (a:Atom {id: $atom_id})
                    MERGE (r:Risk {id: $risk_id})
                    MERGE (a)-[:HAS_RISK]->(r)
                    """
                    await session.run(risk_query, {
                        "atom_id": atom_data["id"],
                        "risk_id": risk_id
                    })

                # Create relationships to controls
                for control_id in atom_data.get("controls", []):
                    control_query = """
                    MATCH (a:Atom {id: $atom_id})
                    MERGE (c:Control {id: $control_id})
                    MERGE (a)-[:HAS_CONTROL]->(c)
                    """
                    await session.run(control_query, {
                        "atom_id": atom_data["id"],
                        "control_id": control_id
                    })

                logger.info(f"Deployed atom: {atom_data['id']}")
                return True

        except Exception as e:
            logger.error(f"Failed to deploy atom {atom_data.get('id')}: {e}")
            return False

    async def deploy_molecule(self, molecule_data: Dict) -> bool:
        """Deploy molecule to KG"""
        try:
            async with self.driver.session() as session:
                # Create or update molecule node
                query = """
                MERGE (m:Molecule {id: $id})
                SET m += $props
                RETURN m
                """
                await session.run(query, {
                    "id": molecule_data["id"],
                    "props": {k: v for k, v in molecule_data.items() if k != "steps"}
                })

                # Create step relationships
                for idx, step in enumerate(molecule_data.get("steps", [])):
                    step_query = """
                    MATCH (m:Molecule {id: $mol_id})
                    MERGE (a:Atom {id: $atom_id})
                    CREATE (m)-[:HAS_STEP {order: $order, stepId: $step_id}]->(a)
                    """
                    await session.run(step_query, {
                        "mol_id": molecule_data["id"],
                        "atom_id": step["atomId"],
                        "order": idx + 1,
                        "step_id": step["id"]
                    })

                logger.info(f"Deployed molecule: {molecule_data['id']}")
                return True

        except Exception as e:
            logger.error(f"Failed to deploy molecule {molecule_data.get('id')}: {e}")
            return False

    async def deploy_workflow(self, workflow_data: Dict) -> bool:
        """Deploy workflow to KG"""
        try:
            async with self.driver.session() as session:
                # Create or update workflow node
                query = """
                MERGE (w:Workflow {id: $id})
                SET w += $props
                RETURN w
                """
                await session.run(query, {
                    "id": workflow_data["id"],
                    "props": {k: v for k, v in workflow_data.items() if k != "phases"}
                })

                # Create phase relationships
                for idx, phase in enumerate(workflow_data.get("phases", [])):
                    for mol_id in phase.get("molecules", []):
                        phase_query = """
                        MATCH (w:Workflow {id: $wf_id})
                        MERGE (m:Molecule {id: $mol_id})
                        CREATE (w)-[:HAS_PHASE {order: $order, phaseId: $phase_id}]->(m)
                        """
                        await session.run(phase_query, {
                            "wf_id": workflow_data["id"],
                            "mol_id": mol_id,
                            "order": idx + 1,
                            "phase_id": phase["id"]
                        })

                logger.info(f"Deployed workflow: {workflow_data['id']}")
                return True

        except Exception as e:
            logger.error(f"Failed to deploy workflow {workflow_data.get('id')}: {e}")
            return False

    async def deploy_artifacts(self, artifact_dir: Path) -> Dict[str, Any]:
        """Deploy all artifacts from directory"""

        # Deploy atoms first
        atoms_dir = artifact_dir / "atoms"
        if atoms_dir.exists():
            for atom_file in atoms_dir.glob("*.atom.yml"):
                with open(atom_file) as f:
                    atom_data = yaml.safe_load(f)
                success = await self.deploy_atom(atom_data)
                if success:
                    self.deployment_stats["atoms"]["deployed"] += 1
                else:
                    self.deployment_stats["atoms"]["failed"] += 1

        # Deploy molecules
        molecules_dir = artifact_dir / "molecules"
        if molecules_dir.exists():
            for mol_file in molecules_dir.glob("*.molecule.yml"):
                with open(mol_file) as f:
                    mol_data = yaml.safe_load(f)
                success = await self.deploy_molecule(mol_data)
                if success:
                    self.deployment_stats["molecules"]["deployed"] += 1
                else:
                    self.deployment_stats["molecules"]["failed"] += 1

        # Deploy workflows
        workflows_dir = artifact_dir / "workflows"
        if workflows_dir.exists():
            for wf_file in workflows_dir.glob("*.workflow.yml"):
                with open(wf_file) as f:
                    wf_data = yaml.safe_load(f)
                success = await self.deploy_workflow(wf_data)
                if success:
                    self.deployment_stats["workflows"]["deployed"] += 1
                else:
                    self.deployment_stats["workflows"]["failed"] += 1

        return self.deployment_stats


async def main():
    """Main deployment function"""
    import os

    # Neo4j connection
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "banking_secure_password")

    deployer = KnowledgeGraphDeployer(neo4j_uri, neo4j_user, neo4j_password)

    try:
        # Deploy artifacts
        artifact_dir = Path(__file__).parent.parent
        stats = await deployer.deploy_artifacts(artifact_dir)

        # Generate deployment report
        report = f"""# Deployment Report

**Deployment Date**: {datetime.utcnow().isoformat()}

## Deployment Statistics

| Artifact Type | Deployed | Failed |
|--------------|----------|--------|
| Atoms | {stats['atoms']['deployed']} | {stats['atoms']['failed']} |
| Molecules | {stats['molecules']['deployed']} | {stats['molecules']['failed']} |
| Workflows | {stats['workflows']['deployed']} | {stats['workflows']['failed']} |
| Risks | {stats['risks']['deployed']} | {stats['risks']['failed']} |
| Controls | {stats['controls']['deployed']} | {stats['controls']['failed']} |
| Regulations | {stats['regulations']['deployed']} | {stats['regulations']['failed']} |

## Status

"""

        total_deployed = sum(s["deployed"] for s in stats.values())
        total_failed = sum(s["failed"] for s in stats.values())

        if total_failed == 0:
            report += "✅ **All artifacts deployed successfully**\n"
            exit_code = 0
        else:
            report += f"⚠️ **{total_failed} artifacts failed to deploy**\n"
            exit_code = 1

        # Write report
        with open("deployment-report.md", "w") as f:
            f.write(report)

        print(report)
        sys.exit(exit_code)

    finally:
        await deployer.close()


if __name__ == "__main__":
    asyncio.run(main())
