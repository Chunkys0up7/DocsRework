"""
Custom exceptions for the Banking Docs-as-Code platform
"""

from typing import Optional, Dict, Any


class BankingDocsException(Exception):
    """Base exception for all application errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BankingDocsException):
    """Raised when validation fails"""
    pass


class SchemaValidationError(ValidationError):
    """Raised when JSON schema validation fails"""
    pass


class SemanticValidationError(ValidationError):
    """Raised when semantic validation fails"""
    pass


class ReferenceValidationError(ValidationError):
    """Raised when reference validation fails"""
    pass


class CircularDependencyError(ValidationError):
    """Raised when circular dependency is detected"""
    pass


class VersioningError(BankingDocsException):
    """Raised when versioning rules are violated"""
    pass


class DeploymentError(BankingDocsException):
    """Raised when deployment fails"""
    pass


class KnowledgeGraphError(BankingDocsException):
    """Raised when KG operations fail"""
    pass


class RiskCalculationError(BankingDocsException):
    """Raised when risk calculation fails"""
    pass


class ComplianceError(BankingDocsException):
    """Raised when compliance check fails"""
    pass


class ControlError(BankingDocsException):
    """Raised when control validation fails"""
    pass


class AuthenticationError(BankingDocsException):
    """Raised when authentication fails"""
    pass


class AuthorizationError(BankingDocsException):
    """Raised when authorization fails"""
    pass


class ResourceNotFoundError(BankingDocsException):
    """Raised when requested resource is not found"""
    pass


class DuplicateResourceError(BankingDocsException):
    """Raised when attempting to create duplicate resource"""
    pass
