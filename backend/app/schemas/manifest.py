from pydantic import BaseModel

from app.schemas.pii import RedactionDatasetSummary, RedactionPreview, RedactionSummary
from app.schemas.validation import IngestionStatus, ValidationResult


class TransformationCount(BaseModel):
    type: str
    count: int


class TransformationManifest(BaseModel):
    dataset: str
    rows_received: int
    rows_output: int
    columns_received: int
    sensitive_findings_detected: int
    redactions_applied: int
    residual_pii_findings: int
    validation_errors: int
    validation_warnings: int
    transformations: list[TransformationCount]
    status: IngestionStatus


class DatasetValidationResponse(BaseModel):
    dataset: RedactionDatasetSummary
    pii_summary: RedactionSummary
    validation: ValidationResult
    manifest: TransformationManifest
    preview: RedactionPreview
    status: IngestionStatus
