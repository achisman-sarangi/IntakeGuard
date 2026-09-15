from collections import Counter
from collections.abc import Mapping, Sequence

from app.schemas.manifest import TransformationCount, TransformationManifest
from app.schemas.pii import PIIFinding, PIIType
from app.schemas.validation import ValidationCode, ValidationResult

_TRANSFORMATION_NAMES = {
    PIIType.EMAIL: "REDACT_EMAIL",
    PIIType.PHONE: "REDACT_PHONE",
    PIIType.PERSON_NAME: "REDACT_NAME",
    PIIType.SSN: "REDACT_SSN",
    PIIType.IP_ADDRESS: "REDACT_IP",
}


class ManifestBuilder:
    def build(
        self,
        *,
        filename: str,
        columns_received: int,
        input_rows: Sequence[Mapping[str, str]],
        output_rows: Sequence[Mapping[str, str]],
        pii_findings: Sequence[PIIFinding],
        validation: ValidationResult,
    ) -> TransformationManifest:
        counts = Counter(finding.type for finding in pii_findings)
        transformations = [
            TransformationCount(type=name, count=counts[pii_type])
            for pii_type, name in _TRANSFORMATION_NAMES.items()
            if counts[pii_type]
        ]
        residual_count = sum(
            finding.code is ValidationCode.RESIDUAL_PII
            for finding in validation.findings
        )
        return TransformationManifest(
            dataset=filename,
            rows_received=len(input_rows),
            rows_output=len(output_rows),
            columns_received=columns_received,
            sensitive_findings_detected=len(pii_findings),
            redactions_applied=len(pii_findings),
            residual_pii_findings=residual_count,
            validation_errors=validation.error_count,
            validation_warnings=validation.warning_count,
            transformations=transformations,
            status=validation.status,
        )
