from enum import Enum
from typing import Literal

from pydantic import BaseModel


class PIIType(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SSN = "SSN"
    IP_ADDRESS = "IP_ADDRESS"
    PERSON_NAME = "PERSON_NAME"


class DetectionSource(str, Enum):
    COLUMN_CLASSIFICATION = "COLUMN_CLASSIFICATION"
    VALUE_PATTERN = "VALUE_PATTERN"
    EMBEDDED_PATTERN = "EMBEDDED_PATTERN"


class PIIFinding(BaseModel):
    row_index: int
    column: str
    type: PIIType
    source: DetectionSource
    original_value: str


class RedactionDatasetSummary(BaseModel):
    filename: str
    row_count: int
    column_count: int


class RedactionSummary(BaseModel):
    total_findings: int
    email_findings: int
    phone_findings: int
    ssn_findings: int
    ip_findings: int
    name_findings: int
    rows_affected: int


class RedactionPreview(BaseModel):
    before: list[dict[str, str]]
    after: list[dict[str, str]]


class DatasetRedactionResponse(BaseModel):
    dataset: RedactionDatasetSummary
    summary: RedactionSummary
    findings: list[PIIFinding]
    preview: RedactionPreview
    status: Literal["REDACTED"] = "REDACTED"
