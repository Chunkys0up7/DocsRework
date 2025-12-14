# Banking Docs-as-Code Ontology

## Overview

This document defines the core ontology for the Banking Docs-as-Code Knowledge Graph system. The ontology provides a formal specification of concepts, relationships, and constraints that govern how banking documentation, processes, risks, controls, and regulations are modeled and interconnected.

## Ontology Design Principles

1. **Clarity**: Concepts are precisely defined with no ambiguity
2. **Coherence**: Definitions are consistent and logically sound
3. **Extensibility**: New concepts can be added without breaking existing models
4. **Minimal Ontological Commitment**: Only essential distinctions are encoded
5. **Separation of Concerns**: Clear boundaries between layers (ontology, atoms, molecules, workflows)

## Layered Knowledge Model

The system follows a four-layer architecture:

```
┌─────────────────────────────────────────┐
│         Workflow Layer                  │
│  (Composed Business Processes)          │
└──────────────┬──────────────────────────┘
               │ composes
┌──────────────┴──────────────────────────┐
│         Molecule Layer                  │
│  (Multi-step Procedures)                │
└──────────────┬──────────────────────────┘
               │ composes
┌──────────────┴──────────────────────────┐
│         Atom Layer                      │
│  (Atomic Operations)                    │
└──────────────┬──────────────────────────┘
               │ grounded in
┌──────────────┴──────────────────────────┐
│    Ontology Foundation                  │
│  (Core Concepts & Relationships)        │
└─────────────────────────────────────────┘
```

## Core Concepts

### 1. Process Entities

#### Atom
**Definition**: An atomic, indivisible unit of work that performs a single, well-defined operation.

**Properties**:
- `id`: Unique identifier (pattern: `atom:name:vX.Y.Z`)
- `version`: Semantic version
- `name`: Human-readable name
- `description`: Detailed description
- `owner`: Person responsible for this atom
- `steward`: Person maintaining this atom
- `inputs`: Required input parameters
- `outputs`: Produced outputs
- `implementation`: How the atom is executed (API, script, manual)
- `sla`: Service level agreements

**Invariants**:
- An atom MUST NOT depend on other atoms directly
- An atom MUST be stateless and idempotent where possible
- An atom MUST have exactly one clearly defined purpose

#### Molecule
**Definition**: A coordinated sequence of atoms that together accomplish a coherent multi-step procedure.

**Properties**:
- `id`: Unique identifier (pattern: `molecule:name:vX.Y.Z`)
- `version`: Semantic version
- `atoms`: Ordered collection of atom references
- `flow`: Control flow definition (transitions, gates, conditions)
- `inputs`: Required inputs for the molecule
- `outputs`: Outputs produced by the molecule

**Invariants**:
- A molecule MUST reference at least 2 atoms
- All atom references MUST be valid and versioned
- Flow transitions MUST form a valid directed graph
- Every step MUST be reachable from the start step
- There MUST be at least one path to END

#### Workflow
**Definition**: A composed business process that orchestrates atoms, molecules, and other workflows to achieve a complex business objective.

**Properties**:
- `id`: Unique identifier (pattern: `workflow:name:vX.Y.Z`)
- `version`: Semantic version
- `components`: Collection of atoms, molecules, sub-workflows
- `flow`: Complex flow control (sequential, parallel, conditional)
- `businessContext`: Business metadata (department, priority, frequency)
- `monitoring`: KPIs and alerting configuration

**Invariants**:
- Component references MUST be valid and versioned
- Parallel branches MUST eventually join
- Error handling MUST be defined for critical paths
- SLA configuration MUST be realistic and measurable

### 2. Risk & Control Entities

#### Risk
**Definition**: A potential event or condition that could adversely affect the bank's ability to achieve its objectives.

**Properties**:
- `id`: Unique identifier (pattern: `risk:name:vX.Y.Z`)
- `category`: Risk category (operational, financial, compliance, etc.)
- `likelihood`: Probability of occurrence (1-5)
- `impact`: Severity of consequences (1-5)
- `inherentRisk`: Risk before controls (likelihood × impact)
- `residualRisk`: Risk after controls applied
- `controls`: Controls that mitigate this risk

**Risk Calculation**:
```
Inherent Risk Score = Likelihood × Impact
Residual Risk Score = Inherent Risk × (1 - Σ(Control Effectiveness) / 100)

Risk Level Mapping:
- 1-4: Low
- 5-9: Medium
- 10-16: High
- 17-25: Critical
```

#### Control
**Definition**: A mechanism, policy, or procedure designed to mitigate risks and ensure compliance with regulations.

**Properties**:
- `id`: Unique identifier (pattern: `control:name:vX.Y.Z`)
- `controlType`: preventive, detective, corrective, compensating
- `automationLevel`: fully-automated, semi-automated, manual
- `frequency`: How often the control executes
- `effectiveness`: Control effectiveness rating (0-100%)
- `mitigatedRisks`: Risks addressed by this control

**Control Types**:
- **Preventive**: Prevents risk from occurring
- **Detective**: Detects when risk has occurred
- **Corrective**: Corrects effects after risk occurrence
- **Compensating**: Alternative control when primary is not feasible

#### Regulation
**Definition**: A legal or regulatory requirement that the bank must comply with.

**Properties**:
- `id`: Unique identifier (pattern: `regulation:name:vX.Y.Z`)
- `jurisdiction`: Geographic applicability
- `authority`: Regulatory body
- `requirements`: Specific compliance requirements
- `effectiveDate`: When regulation took effect
- `relatedControls`: Controls implementing this regulation

### 3. Supporting Entities

#### Actor
**Definition**: A person, role, or system that interacts with processes.

**Types**:
- Human Actor (employee, customer, regulator)
- System Actor (API, service, database)
- Role (approver, reviewer, executor)

#### Document
**Definition**: A source document from which knowledge has been extracted.

**Properties**:
- Document type (policy, procedure, manual, regulation)
- Source location
- Extraction timestamp
- Extracted entities (atoms, risks, controls)

#### Artifact
**Definition**: Any versioned entity in the system (atom, molecule, workflow, risk, control, regulation).

**Common Properties**:
- `id`: Unique versioned identifier
- `version`: Semantic version
- `owner`: Responsible person
- `metadata`: Creation/update timestamps, deprecation status

## Relationships

### Process Relationships

| Relationship | Source | Target | Cardinality | Description |
|-------------|--------|--------|-------------|-------------|
| `COMPOSES` | Molecule | Atom | 1:N | Molecule is composed of atoms |
| `COMPOSES` | Workflow | Atom/Molecule/Workflow | 1:N | Workflow is composed of components |
| `REQUIRES` | Atom/Molecule/Workflow | Input | 1:N | Requires input parameters |
| `PRODUCES` | Atom/Molecule/Workflow | Output | 1:N | Produces outputs |
| `DEPENDS_ON` | Atom/Molecule/Workflow | Atom/Molecule/Workflow | N:M | Depends on other components |
| `SUPERSEDES` | Artifact | Artifact | 1:1 | New version replaces old |
| `TRANSITIONS_TO` | Step | Step | 1:N | Flow transition between steps |

### Risk & Control Relationships

| Relationship | Source | Target | Cardinality | Description |
|-------------|--------|--------|-------------|-------------|
| `HAS_RISK` | Atom/Molecule/Workflow | Risk | N:M | Process has associated risks |
| `MITIGATES` | Control | Risk | N:M | Control mitigates risk |
| `HAS_CONTROL` | Atom/Molecule/Workflow | Control | N:M | Process implements control |
| `REQUIRES_CONTROL` | Risk | Control | N:M | Risk requires this control |
| `DEPENDS_ON` | Control | Control | N:M | Control depends on another |

### Regulatory Relationships

| Relationship | Source | Target | Cardinality | Description |
|-------------|--------|--------|-------------|-------------|
| `COMPLIES_WITH` | Atom/Molecule/Workflow | Regulation | N:M | Process complies with regulation |
| `ADDRESSES` | Control | Regulation | N:M | Control addresses regulatory requirement |
| `RELATES_TO` | Risk | Regulation | N:M | Risk related to regulation |
| `ENFORCES` | Regulation | Requirement | 1:N | Regulation enforces requirements |

### Ownership Relationships

| Relationship | Source | Target | Cardinality | Description |
|-------------|--------|--------|-------------|-------------|
| `OWNED_BY` | Artifact | Actor | N:1 | Artifact is owned by actor |
| `STEWARDED_BY` | Artifact | Actor | N:1 | Artifact is stewarded by actor |
| `APPROVED_BY` | Artifact | Actor | N:M | Artifact approved by actor |
| `EXECUTES` | Actor | Atom/Molecule/Workflow | N:M | Actor executes process |

## Competency Questions

The ontology is designed to answer the following competency questions:

### Process Questions
1. What are all the steps required to open a customer account?
2. Which atoms are used in the customer onboarding molecule?
3. What workflows depend on the identity verification atom?
4. What is the expected duration of the account opening workflow?
5. Which processes have been deprecated and what are their replacements?

### Risk Questions
6. What are the inherent and residual risk scores for identity fraud?
7. Which workflows have the highest aggregate risk score?
8. What controls mitigate the identity fraud risk?
9. What is the effectiveness of biometric verification control?
10. Which processes are exposed to unmitigated high risks?

### Compliance Questions
11. Which controls address KYC/AML regulatory requirements?
12. What is the compliance coverage for GDPR regulation?
13. Which processes require compliance officer approval?
14. What controls are missing to achieve full regulatory compliance?
15. Which regulations apply to the customer onboarding process?

### Operational Questions
16. Who owns the customer identity verification atom?
17. Which actors are involved in the account opening workflow?
18. What is the SLA for transaction processing?
19. Which processes have failed tests in the last deployment?
20. What are the KPIs for workflow performance monitoring?

### Lineage & Traceability Questions
21. Where was this atom extracted from (source document)?
22. What is the complete dependency chain for a workflow?
23. Which version of the atom is currently in production?
24. What changed between version 1.0.0 and 2.0.0 of this molecule?
25. What is the audit trail for this process execution?

## Constraints & Validation Rules

### Structural Constraints
1. **No Circular Dependencies**: Workflows, molecules, and atoms MUST NOT form circular dependency chains
2. **Valid References**: All references to other entities MUST point to existing, valid artifacts
3. **Reachability**: Every step in a flow MUST be reachable from the start step
4. **Completeness**: Every flow path MUST eventually reach an END state

### Semantic Constraints
5. **Version Consistency**: Breaking changes MUST increment major version
6. **Ownership**: Every artifact MUST have a defined owner and steward
7. **Risk Coverage**: High and critical risks MUST have at least one control with effectiveness >= 70%
8. **Regulatory Coverage**: Mandatory regulatory requirements MUST have controls with >= 95% coverage

### Operational Constraints
9. **SLA Feasibility**: Workflow SLA MUST be >= sum of component SLAs
10. **Control Frequency**: Detective controls MUST execute at least as frequently as the processes they monitor
11. **Test Coverage**: Atoms MUST have >= 90% test coverage
12. **Approval Requirements**: Changes affecting compliance MUST have compliance officer approval

## Neo4j Graph Schema

### Node Labels
- `:Atom`
- `:Molecule`
- `:Workflow`
- `:Risk`
- `:Control`
- `:Regulation`
- `:Actor`
- `:Document`
- `:Input`
- `:Output`

### Relationship Types
- `:COMPOSES`
- `:REQUIRES`
- `:PRODUCES`
- `:HAS_RISK`
- `:MITIGATES`
- `:HAS_CONTROL`
- `:COMPLIES_WITH`
- `:ADDRESSES`
- `:OWNED_BY`
- `:STEWARDED_BY`
- `:TRANSITIONS_TO`
- `:DEPENDS_ON`
- `:SUPERSEDES`
- `:APPROVED_BY`
- `:EXECUTES`

### Indexes
```cypher
// Unique constraints
CREATE CONSTRAINT atom_id IF NOT EXISTS FOR (a:Atom) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT molecule_id IF NOT EXISTS FOR (m:Molecule) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT workflow_id IF NOT EXISTS FOR (w:Workflow) REQUIRE w.id IS UNIQUE;
CREATE CONSTRAINT risk_id IF NOT EXISTS FOR (r:Risk) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT control_id IF NOT EXISTS FOR (c:Control) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT regulation_id IF NOT EXISTS FOR (r:Regulation) REQUIRE r.id IS UNIQUE;

// Indexes for performance
CREATE INDEX atom_version IF NOT EXISTS FOR (a:Atom) ON (a.version);
CREATE INDEX atom_owner IF NOT EXISTS FOR (a:Atom) ON (a.owner);
CREATE INDEX risk_category IF NOT EXISTS FOR (r:Risk) ON (r.category);
CREATE INDEX control_type IF NOT EXISTS FOR (c:Control) ON (c.controlType);
```

## Extension Points

The ontology can be extended in the following areas:

1. **New Process Types**: Add new layers (e.g., "Procedure" between Molecule and Workflow)
2. **Additional Risk Categories**: Extend risk taxonomy with domain-specific categories
3. **Custom Control Types**: Add specialized control types for specific domains
4. **Enhanced Metadata**: Add properties for specific business contexts
5. **External Integrations**: Link to external systems (ticketing, monitoring, GRC tools)

## Version History

- **v1.0.0** (2026-01-15): Initial ontology definition with core concepts and relationships
