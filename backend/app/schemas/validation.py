from enum import Enum
from pydantic import BaseModel

from app.schemas.pii import PIIType


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationCode(str, Enum):
    RESIDUAL_PII = "RESIDUAL_PII"
    MISSING_REQUIRED_VALUE = "MISSING_REQUIRED_VALUE"
    DUPLICATE_IDENTIFIER = "DUPLICATE_IDENTIFIER"
    DUPLICATE_ROW = "DUPLICATE_ROW"
    INVALID_NUMBER = "INVALID_NUMBER"


class IngestionStatus(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"


class ValidationFinding(BaseModel):
    code: ValidationCode
    severity: ValidationSeverity
    row_index: int
    column: str | None = None
    message: str
    sensitive_type: PIIType | None = None
    evidence: str | None = None


class ValidationResult(BaseModel):
    error_count: int
    warning_count: int
    findings: list[ValidationFinding]
    status: IngestionStatus
