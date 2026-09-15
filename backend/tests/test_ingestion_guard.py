from pathlib import Path

from app.schemas.validation import IngestionStatus, ValidationCode
from app.services.ingestion_guard import IngestionGuard

SAMPLES = Path(__file__).parents[1] / "samples"


def test_dirty_sample_is_blocked_with_expected_reasons() -> None:
    path = SAMPLES / "manufacturing_work_orders.csv"
    result = IngestionGuard().process(path.read_bytes(), path.name)
    codes = [finding.code for finding in result.validation.findings]
    assert result.status is IngestionStatus.BLOCKED
    assert result.validation.error_count == 2
    assert result.validation.warning_count == 1
    assert ValidationCode.MISSING_REQUIRED_VALUE in codes
    assert ValidationCode.DUPLICATE_IDENTIFIER in codes
    assert ValidationCode.DUPLICATE_ROW in codes
    assert result.manifest.residual_pii_findings == 0


def test_clean_sample_is_ready() -> None:
    path = SAMPLES / "manufacturing_work_orders_clean.csv"
    result = IngestionGuard().process(path.read_bytes(), path.name)
    assert result.status is IngestionStatus.READY
    assert result.validation.error_count == 0
    assert result.manifest.residual_pii_findings == 0
    assert result.manifest.rows_received == result.manifest.rows_output == 10


def test_guard_manifest_counts_detected_pii_and_redactions() -> None:
    content = (
        b"work_order_id,machine_id,technician_name,email,repair_cost\n"
        b"WO-1,MX-1,Synthetic Person,user@example.com,12.50\n"
    )
    result = IngestionGuard().process(content, "input.csv")
    assert result.pii_summary.total_findings == 2
    assert result.manifest.sensitive_findings_detected == 2
    assert result.manifest.redactions_applied == 2
    assert result.status is IngestionStatus.READY
    assert result.preview.after[0]["email"] == "[REDACTED_EMAIL]"
