"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ArtifactType(str, Enum):
    """Artifact type enumeration"""
    ATOM = "atom"
    MOLECULE = "molecule"
    WORKFLOW = "workflow"
    RISK = "risk"
    CONTROL = "control"
    REGULATION = "regulation"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ControlType(str, Enum):
    """Control type enumeration"""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATING = "compensating"
    DIRECTIVE = "directive"


class ComplianceStatus(str, Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non-compliant"
    NOT_APPLICABLE = "not-applicable"
    IN_PROGRESS = "in-progress"


# Base models
class BaseArtifact(BaseModel):
    """Base model for all artifacts"""
    id: str = Field(..., pattern=r"^(atom|molecule|workflow|risk|control|regulation):[a-z0-9-]+:v\d+\.\d+\.\d+$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    owner: EmailStr
    steward: EmailStr
    tags: Optional[List[str]] = []


# Atom models
class AtomInput(BaseModel):
    """Atom input parameter"""
    name: str
    type: str
    required: bool
    description: Optional[str] = None


class AtomOutput(BaseModel):
    """Atom output parameter"""
    name: str
    type: str
    description: Optional[str] = None


class AtomCreate(BaseArtifact):
    """Model for creating an atom"""
    inputs: List[AtomInput]
    outputs: List[AtomOutput]
    risks: List[str] = []
    controls: List[str] = []
    regulations: List[str] = []


class AtomResponse(AtomCreate):
    """Model for atom response"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Molecule models
class MoleculeStep(BaseModel):
    """Molecule step definition"""
    stepId: str
    atomRef: str
    description: Optional[str] = None


class FlowTransition(BaseModel):
    """Flow transition definition"""
    from_step: str = Field(..., alias="from")
    to_step: str = Field(..., alias="to")
    condition: Optional[str] = None
    label: Optional[str] = None


class MoleculeFlow(BaseModel):
    """Molecule flow definition"""
    startStep: str
    transitions: List[FlowTransition]


class MoleculeCreate(BaseArtifact):
    """Model for creating a molecule"""
    atoms: List[MoleculeStep]
    flow: MoleculeFlow
    inputs: List[AtomInput]
    outputs: List[AtomOutput]
    risks: List[str] = []
    controls: List[str] = []
    regulations: List[str] = []


class MoleculeResponse(MoleculeCreate):
    """Model for molecule response"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Workflow models
class WorkflowComponent(BaseModel):
    """Workflow component definition"""
    stepId: str
    componentRef: str
    componentType: str
    description: Optional[str] = None


class WorkflowCreate(BaseArtifact):
    """Model for creating a workflow"""
    components: List[WorkflowComponent]
    flow: Dict[str, Any]
    inputs: List[AtomInput]
    outputs: List[AtomOutput]
    risks: List[str] = []
    controls: List[str] = []
    regulations: List[str] = []
    businessContext: Optional[Dict[str, Any]] = None
    monitoring: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowCreate):
    """Model for workflow response"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Risk models
class RiskScore(BaseModel):
    """Risk score model"""
    score: int = Field(..., ge=1, le=25)
    level: RiskLevel


class RiskLikelihood(BaseModel):
    """Risk likelihood model"""
    score: int = Field(..., ge=1, le=5)
    rationale: str


class RiskImpact(BaseModel):
    """Risk impact model"""
    score: int = Field(..., ge=1, le=5)
    rationale: str


class RiskCreate(BaseArtifact):
    """Model for creating a risk"""
    category: str
    subcategory: Optional[str] = None
    likelihood: RiskLikelihood
    impact: RiskImpact
    inherentRisk: RiskScore
    residualRisk: Optional[RiskScore] = None
    controls: List[Dict[str, Any]] = []
    regulations: List[str] = []
    affectedProcesses: List[str] = []


class RiskResponse(RiskCreate):
    """Model for risk response"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Control models
class ControlEffectiveness(BaseModel):
    """Control effectiveness model"""
    rating: int = Field(..., ge=0, le=100)
    lastAssessed: datetime
    assessedBy: Optional[EmailStr] = None


class ControlCreate(BaseArtifact):
    """Model for creating a control"""
    controlType: ControlType
    automationLevel: str
    frequency: str
    effectiveness: ControlEffectiveness
    mitigatedRisks: List[Dict[str, Any]] = []
    regulations: List[Dict[str, Any]] = []
    appliedToProcesses: List[str] = []


class ControlResponse(ControlCreate):
    """Model for control response"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Regulation models
class RegulationRequirement(BaseModel):
    """Regulation requirement model"""
    requirementId: str
    description: str
    mandatory: bool


class RegulationCreate(BaseArtifact):
    """Model for creating a regulation"""
    shortName: Optional[str] = None
    jurisdiction: List[str]
    authority: Dict[str, Any]
    category: str
    effectiveDate: str
    requirements: List[RegulationRequirement]
    relatedControls: List[Dict[str, Any]] = []
    affectedProcesses: List[str] = []


class RegulationResponse(RegulationCreate):
    """Model for regulation response"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# List response models
class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Analytics models
class RiskAnalyticsResponse(BaseModel):
    """Risk analytics response"""
    totalRisks: int
    risksByLevel: Dict[str, int]
    averageInherentRisk: float
    averageResidualRisk: float
    highRiskWorkflows: List[str]


class ComplianceAnalyticsResponse(BaseModel):
    """Compliance analytics response"""
    totalRegulations: int
    complianceStatus: Dict[str, int]
    averageCoverage: float
    gapCount: int


# Error models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
