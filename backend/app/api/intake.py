from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.dataset import DatasetProfileResponse
from app.schemas.manifest import DatasetValidationResponse
from app.schemas.pii import (
    DatasetRedactionResponse,
    PIIType,
    RedactionDatasetSummary,
    RedactionPreview,
    RedactionSummary,
)
from app.services.dataset_profiler import DatasetProfileError, DatasetProfiler
from app.services.ingestion_guard import IngestionGuard
from app.services.pii_detector import PIIDetector
from app.services.redactor import Redactor

router = APIRouter(prefix="/api/intake", tags=["intake"])

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_PREVIEW_ROWS = 5


async def _read_csv_upload(file: UploadFile) -> tuple[str, bytes]:
    filename = file.filename or ""
    if Path(filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv files are supported.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file exceeds the 5 MB size limit.",
        )
    return Path(filename).name, content


@router.post("/profile", response_model=DatasetProfileResponse)
async def profile_dataset(file: UploadFile = File(...)) -> DatasetProfileResponse:
    filename, content = await _read_csv_upload(file)

    try:
        return DatasetProfiler().profile(
            content=content,
            filename=filename,
        )
    except DatasetProfileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/redact", response_model=DatasetRedactionResponse)
async def redact_dataset(file: UploadFile = File(...)) -> DatasetRedactionResponse:
    filename, content = await _read_csv_upload(file)
    try:
        header, rows = DatasetProfiler().parse(content)
    except DatasetProfileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    findings = PIIDetector().detect(rows)
    redacted_rows = Redactor().redact(rows, findings)
    counts = {pii_type: 0 for pii_type in PIIType}
    for finding in findings:
        counts[finding.type] += 1

    return DatasetRedactionResponse(
        dataset=RedactionDatasetSummary(
            filename=filename,
            row_count=len(rows),
            column_count=len(header),
        ),
        summary=RedactionSummary(
            total_findings=len(findings),
            email_findings=counts[PIIType.EMAIL],
            phone_findings=counts[PIIType.PHONE],
            ssn_findings=counts[PIIType.SSN],
            ip_findings=counts[PIIType.IP_ADDRESS],
            name_findings=counts[PIIType.PERSON_NAME],
            rows_affected=len({finding.row_index for finding in findings}),
        ),
        findings=findings,
        preview=RedactionPreview(
            before=rows[:MAX_PREVIEW_ROWS],
            after=redacted_rows[:MAX_PREVIEW_ROWS],
        ),
    )


@router.post("/validate", response_model=DatasetValidationResponse)
async def validate_dataset(file: UploadFile = File(...)) -> DatasetValidationResponse:
    filename, content = await _read_csv_upload(file)
    try:
        return IngestionGuard().process(content, filename)
    except DatasetProfileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
