from app.schemas.pii import DetectionSource, PIIType
from app.services.pii_detector import PIIDetector


def _findings(value: str, column: str = "notes"):
    return PIIDetector().detect([{column: value}])


def test_detects_email() -> None:
    finding = _findings("user@example.com")[0]
    assert (finding.type, finding.source) == (
        PIIType.EMAIL,
        DetectionSource.VALUE_PATTERN,
    )


def test_detects_supported_phone_formats() -> None:
    for phone in (
        "415-555-0198",
        "(415) 555-0198",
        "415 555 0198",
        "+1 415-555-0198",
    ):
        assert _findings(phone)[0].type is PIIType.PHONE


def test_detects_ssn() -> None:
    assert _findings("123-45-6789")[0].type is PIIType.SSN


def test_detects_valid_but_not_invalid_ipv4() -> None:
    assert _findings("10.10.4.21")[0].type is PIIType.IP_ADDRESS
    assert _findings("999.999.999.999") == []


def test_classifies_normalized_sensitive_columns() -> None:
    detector = PIIDetector()
    assert detector.classify_column(" Email Address ") is PIIType.EMAIL
    assert detector.classify_column("phone-number") is PIIType.PHONE
    assert detector.classify_column("inventory_id") is None


def test_person_name_only_comes_from_configured_column() -> None:
    detector = PIIDetector()
    findings = detector.detect(
        [{"technician_name": "Synthetic Person", "notes": "Contact Sarah"}]
    )
    assert len(findings) == 1
    assert findings[0].type is PIIType.PERSON_NAME
    assert findings[0].source is DetectionSource.COLUMN_CLASSIFICATION


def test_detects_all_embedded_types() -> None:
    text = (
        "Email ops@example.com or call 415-555-0198 from 10.10.4.21; "
        "test SSN 123-45-6789."
    )
    findings = _findings(text)
    assert {finding.type for finding in findings} == {
        PIIType.EMAIL,
        PIIType.PHONE,
        PIIType.SSN,
        PIIType.IP_ADDRESS,
    }
    assert all(f.source is DetectionSource.EMBEDDED_PATTERN for f in findings)


def test_repeated_value_in_same_cell_has_no_duplicate_finding() -> None:
    findings = _findings("ops@example.com then ops@example.com")
    assert len(findings) == 1


def test_detection_does_not_mutate_rows_and_skips_empty_values() -> None:
    rows = [{"email": "user@example.com", "blank": "   "}]
    original = [dict(row) for row in rows]
    PIIDetector().detect(rows)
    assert rows == original


def test_already_redacted_value_is_ignored() -> None:
    assert _findings("[REDACTED_EMAIL]", "email") == []
