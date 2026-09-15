from collections import Counter
from collections.abc import Mapping, Sequence

from app.schemas.validation import (
    IngestionStatus,
    ValidationCode,
    ValidationFinding,
    ValidationResult,
    ValidationSeverity,
)
from app.services.dataset_profiler import infer_type
from app.services.pii_detector import PIIDetector

_REQUIRED_IDENTIFIERS = ("work_order_id", "machine_id")


class DatasetValidator:
    def __init__(self, pii_detector: PIIDetector | None = None) -> None:
        self._pii_detector = pii_detector or PIIDetector()

    def validate(self, rows: Sequence[Mapping[str, str]]) -> ValidationResult:
        findings: list[ValidationFinding] = []
        findings.extend(self._residual_pii_findings(rows))
        findings.extend(self._required_value_findings(rows))
        findings.extend(self._duplicate_identifier_findings(rows))
        findings.extend(self._duplicate_row_findings(rows))
        findings.extend(self._number_findings(rows))

        error_count = sum(
            finding.severity is ValidationSeverity.ERROR for finding in findings
        )
        warning_count = sum(
            finding.severity is ValidationSeverity.WARNING for finding in findings
        )
        return ValidationResult(
            error_count=error_count,
            warning_count=warning_count,
            findings=findings,
            status=(
                IngestionStatus.BLOCKED if error_count else IngestionStatus.READY
            ),
        )

    def _residual_pii_findings(
        self, rows: Sequence[Mapping[str, str]]
    ) -> list[ValidationFinding]:
        return [
            ValidationFinding(
                code=ValidationCode.RESIDUAL_PII,
                severity=ValidationSeverity.ERROR,
                row_index=finding.row_index,
                column=finding.column,
                sensitive_type=finding.type,
                evidence=f"Detectable {finding.type.value} remains after redaction.",
                message=f"Residual {finding.type.value} detected in {finding.column}.",
            )
            for finding in self._pii_detector.detect(rows)
        ]

    @staticmethod
    def _required_value_findings(
        rows: Sequence[Mapping[str, str]],
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        for row_index, row in enumerate(rows, start=1):
            for column in _REQUIRED_IDENTIFIERS:
                if column in row and not row[column].strip():
                    findings.append(
                        ValidationFinding(
                            code=ValidationCode.MISSING_REQUIRED_VALUE,
                            severity=ValidationSeverity.ERROR,
                            row_index=row_index,
                            column=column,
                            message=f"Required field {column} is empty.",
                        )
                    )
        return findings

    @staticmethod
    def _duplicate_identifier_findings(
        rows: Sequence[Mapping[str, str]],
    ) -> list[ValidationFinding]:
        values = [row.get("work_order_id", "").strip() for row in rows]
        duplicates = {value for value, count in Counter(values).items() if value and count > 1}
        seen: set[str] = set()
        findings: list[ValidationFinding] = []
        for row_index, value in enumerate(values, start=1):
            if value in duplicates and value in seen:
                findings.append(
                    ValidationFinding(
                        code=ValidationCode.DUPLICATE_IDENTIFIER,
                        severity=ValidationSeverity.ERROR,
                        row_index=row_index,
                        column="work_order_id",
                        message=f"work_order_id {value!r} is duplicated.",
                    )
                )
            seen.add(value)
        return findings

    @staticmethod
    def _duplicate_row_findings(
        rows: Sequence[Mapping[str, str]],
    ) -> list[ValidationFinding]:
        seen: set[tuple[tuple[str, str], ...]] = set()
        findings: list[ValidationFinding] = []
        for row_index, row in enumerate(rows, start=1):
            identity = tuple(row.items())
            if identity in seen:
                findings.append(
                    ValidationFinding(
                        code=ValidationCode.DUPLICATE_ROW,
                        severity=ValidationSeverity.WARNING,
                        row_index=row_index,
                        message="Row is an exact duplicate of an earlier row.",
                    )
                )
            seen.add(identity)
        return findings

    @staticmethod
    def _number_findings(
        rows: Sequence[Mapping[str, str]],
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        for row_index, row in enumerate(rows, start=1):
            value = row.get("repair_cost")
            if value is None or not value.strip():
                continue
            if infer_type([value.strip()]) not in {"integer", "number"}:
                findings.append(
                    ValidationFinding(
                        code=ValidationCode.INVALID_NUMBER,
                        severity=ValidationSeverity.ERROR,
                        row_index=row_index,
                        column="repair_cost",
                        message="repair_cost must be a finite number when provided.",
                    )
                )
        return findings
