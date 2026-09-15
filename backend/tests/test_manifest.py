from app.schemas.pii import DetectionSource, PIIFinding, PIIType
from app.schemas.validation import IngestionStatus, ValidationCode, ValidationFinding, ValidationResult, ValidationSeverity
from app.services.manifest import ManifestBuilder


def test_manifest_uses_actual_execution_counts() -> None:
    pii_findings = [
        PIIFinding(row_index=1, column="email", type=PIIType.EMAIL, source=DetectionSource.VALUE_PATTERN, original_value="a@example.com"),
        PIIFinding(row_index=1, column="phone", type=PIIType.PHONE, source=DetectionSource.VALUE_PATTERN, original_value="415-555-0198"),
    ]
    validation = ValidationResult(
        error_count=1,
        warning_count=1,
        status=IngestionStatus.BLOCKED,
        findings=[
            ValidationFinding(code=ValidationCode.RESIDUAL_PII, severity=ValidationSeverity.ERROR, row_index=1, column="notes", message="Residual EMAIL detected."),
            ValidationFinding(code=ValidationCode.DUPLICATE_ROW, severity=ValidationSeverity.WARNING, row_index=2, message="Duplicate row."),
        ],
    )
    manifest = ManifestBuilder().build(
        filename="input.csv",
        columns_received=2,
        input_rows=[{"a": "1"}, {"a": "1"}],
        output_rows=[{"a": "1"}, {"a": "1"}],
        pii_findings=pii_findings,
        validation=validation,
    )
    assert manifest.sensitive_findings_detected == 2
    assert manifest.redactions_applied == 2
    assert manifest.residual_pii_findings == 1
    assert manifest.validation_errors == 1
    assert manifest.validation_warnings == 1
    assert {item.type: item.count for item in manifest.transformations} == {
        "REDACT_EMAIL": 1,
        "REDACT_PHONE": 1,
    }
    assert manifest.status is IngestionStatus.BLOCKED
