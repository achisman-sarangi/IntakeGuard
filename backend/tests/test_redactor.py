from app.schemas.pii import DetectionSource, PIIFinding, PIIType
from app.services.pii_detector import PIIDetector
from app.services.redactor import Redactor


def _redact(value: str, column: str = "notes") -> str:
    rows = [{column: value}]
    return Redactor().redact(rows, PIIDetector().detect(rows))[0][column]


def test_redacts_each_pattern_type() -> None:
    assert _redact("user@example.com") == "[REDACTED_EMAIL]"
    assert _redact("415-555-0198") == "[REDACTED_PHONE]"
    assert _redact("123-45-6789") == "[REDACTED_SSN]"
    assert _redact("10.10.4.21") == "[REDACTED_IP]"


def test_redacts_entire_name_field() -> None:
    assert _redact("Synthetic Person", "technician_name") == "[REDACTED_NAME]"


def test_embedded_redaction_preserves_surrounding_text() -> None:
    value = "Machine CNC-482 failed. Contact joe@example.com or 415-555-0198."
    assert _redact(value) == (
        "Machine CNC-482 failed. Contact [REDACTED_EMAIL] or [REDACTED_PHONE]."
    )


def test_non_sensitive_values_and_input_remain_unchanged() -> None:
    rows = [{"machine_id": "CNC-482", "notes": "Routine service"}]
    result = Redactor().redact(rows, [])
    assert result == rows
    assert result is not rows
    assert result[0] is not rows[0]


def test_replaces_repeated_sensitive_value_without_corruption() -> None:
    assert _redact("ops@example.com then ops@example.com") == (
        "[REDACTED_EMAIL] then [REDACTED_EMAIL]"
    )


def test_redaction_is_idempotent() -> None:
    rows = [{"email": "user@example.com", "notes": "Call 415-555-0198"}]
    detector = PIIDetector()
    first = Redactor().redact(rows, detector.detect(rows))
    second = Redactor().redact(first, detector.detect(first))
    assert second == first


def test_rejects_finding_with_invalid_location() -> None:
    finding = PIIFinding(
        row_index=2,
        column="notes",
        type=PIIType.EMAIL,
        source=DetectionSource.VALUE_PATTERN,
        original_value="user@example.com",
    )
    try:
        Redactor().redact([{"notes": "user@example.com"}], [finding])
    except ValueError as exc:
        assert "out of range" in str(exc)
    else:
        raise AssertionError("Expected invalid finding location to fail")
