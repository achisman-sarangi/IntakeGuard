import pytest

from app.schemas.pii import PIIType
from app.schemas.validation import IngestionStatus, ValidationCode, ValidationSeverity
from app.services.validator import DatasetValidator


@pytest.mark.parametrize(
    ("value", "pii_type"),
    [
        ("Contact ops@example.com", PIIType.EMAIL),
        ("Call 415-555-0198", PIIType.PHONE),
        ("Test SSN 123-45-6789", PIIType.SSN),
        ("Controller 10.10.4.21", PIIType.IP_ADDRESS),
    ],
)
def test_residual_pii_causes_blocked(value: str, pii_type: PIIType) -> None:
    result = DatasetValidator().validate([{"notes": value}])
    assert result.status is IngestionStatus.BLOCKED
    finding = next(f for f in result.findings if f.code is ValidationCode.RESIDUAL_PII)
    assert finding.sensitive_type is pii_type
    assert finding.severity is ValidationSeverity.ERROR


def test_no_residual_pii_passes_residual_check() -> None:
    result = DatasetValidator().validate([{"notes": "Contact [REDACTED_EMAIL]"}])
    assert not any(f.code is ValidationCode.RESIDUAL_PII for f in result.findings)
    assert result.status is IngestionStatus.READY


@pytest.mark.parametrize("column", ["work_order_id", "machine_id"])
def test_missing_required_identifier_is_error(column: str) -> None:
    result = DatasetValidator().validate([{column: "   "}])
    assert result.status is IngestionStatus.BLOCKED
    assert any(
        f.code is ValidationCode.MISSING_REQUIRED_VALUE and f.column == column
        for f in result.findings
    )


def test_duplicate_work_order_id_is_error_even_when_rows_differ() -> None:
    rows = [
        {"work_order_id": "WO-1", "machine_id": "MX-1"},
        {"work_order_id": "WO-1", "machine_id": "MX-2"},
    ]
    result = DatasetValidator().validate(rows)
    assert result.status is IngestionStatus.BLOCKED
    assert sum(f.code is ValidationCode.DUPLICATE_IDENTIFIER for f in result.findings) == 1


def test_duplicate_whole_row_is_warning() -> None:
    rows = [{"facility": "Test Plant"}, {"facility": "Test Plant"}]
    result = DatasetValidator().validate(rows)
    assert result.warning_count == 1
    assert result.findings[0].code is ValidationCode.DUPLICATE_ROW
    assert result.status is IngestionStatus.READY


def test_invalid_repair_cost_is_error() -> None:
    result = DatasetValidator().validate([{"repair_cost": "not-a-number"}])
    assert result.status is IngestionStatus.BLOCKED
    assert result.findings[0].code is ValidationCode.INVALID_NUMBER


@pytest.mark.parametrize("value", ["", "   "])
def test_empty_repair_cost_is_allowed(value: str) -> None:
    result = DatasetValidator().validate([{"repair_cost": value}])
    assert result.error_count == 0
    assert result.status is IngestionStatus.READY


def test_any_error_causes_blocked_even_with_warning() -> None:
    rows = [
        {"machine_id": "", "facility": "A"},
        {"machine_id": "", "facility": "A"},
    ]
    result = DatasetValidator().validate(rows)
    assert result.error_count == 2
    assert result.warning_count == 1
    assert result.status is IngestionStatus.BLOCKED


def test_ready_invariant_rejects_detectable_pii_in_transformed_output() -> None:
    simulated_failed_transformation = [{"notes": "Email ops@example.com"}]
    result = DatasetValidator().validate(simulated_failed_transformation)
    assert result.status is not IngestionStatus.READY
    assert result.error_count > 0
