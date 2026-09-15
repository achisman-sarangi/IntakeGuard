from app.schemas.manifest import DatasetValidationResponse
from app.schemas.pii import PIIType, RedactionDatasetSummary, RedactionPreview, RedactionSummary
from app.services.dataset_profiler import DatasetProfiler
from app.services.manifest import ManifestBuilder
from app.services.pii_detector import PIIDetector
from app.services.redactor import Redactor
from app.services.validator import DatasetValidator

MAX_PREVIEW_ROWS = 5


class IngestionGuard:
    def __init__(self) -> None:
        self._profiler = DatasetProfiler()
        self._detector = PIIDetector()
        self._redactor = Redactor()
        self._validator = DatasetValidator()
        self._manifest_builder = ManifestBuilder()

    def process(self, content: bytes, filename: str) -> DatasetValidationResponse:
        profile = self._profiler.profile(content, filename)
        header, rows = self._profiler.parse(content)
        pii_findings = self._detector.detect(rows)
        transformed_rows = self._redactor.redact(rows, pii_findings)
        validation = self._validator.validate(transformed_rows)

        counts = {pii_type: 0 for pii_type in PIIType}
        for finding in pii_findings:
            counts[finding.type] += 1
        pii_summary = RedactionSummary(
            total_findings=len(pii_findings),
            email_findings=counts[PIIType.EMAIL],
            phone_findings=counts[PIIType.PHONE],
            ssn_findings=counts[PIIType.SSN],
            ip_findings=counts[PIIType.IP_ADDRESS],
            name_findings=counts[PIIType.PERSON_NAME],
            rows_affected=len({finding.row_index for finding in pii_findings}),
        )
        manifest = self._manifest_builder.build(
            filename=filename,
            columns_received=profile.dataset.column_count,
            input_rows=rows,
            output_rows=transformed_rows,
            pii_findings=pii_findings,
            validation=validation,
        )
        return DatasetValidationResponse(
            dataset=RedactionDatasetSummary(
                filename=filename,
                row_count=profile.dataset.row_count,
                column_count=profile.dataset.column_count,
            ),
            pii_summary=pii_summary,
            validation=validation,
            manifest=manifest,
            preview=RedactionPreview(
                before=rows[:MAX_PREVIEW_ROWS],
                after=transformed_rows[:MAX_PREVIEW_ROWS],
            ),
            status=validation.status,
        )
