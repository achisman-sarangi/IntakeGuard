import re
from collections.abc import Iterator, Mapping, Sequence

from app.schemas.pii import DetectionSource, PIIFinding, PIIType

SENSITIVE_COLUMN_TYPES: dict[str, PIIType] = {
    "technician_name": PIIType.PERSON_NAME,
    "employee_name": PIIType.PERSON_NAME,
    "customer_name": PIIType.PERSON_NAME,
    "technician_email": PIIType.EMAIL,
    "email": PIIType.EMAIL,
    "email_address": PIIType.EMAIL,
    "phone": PIIType.PHONE,
    "phone_number": PIIType.PHONE,
    "ssn": PIIType.SSN,
    "social_security_number": PIIType.SSN,
}

_EMAIL = re.compile(
    r"(?<![\w.+-])[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}(?![\w.-])"
)
_PHONE = re.compile(
    r"(?<![\d])(?:\+1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?!\d)"
)
_SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
_IPV4_CANDIDATE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
_REDACTION_TOKEN = re.compile(r"^\[REDACTED_(?:EMAIL|PHONE|SSN|IP|NAME)\]$")


def _valid_ipv4(value: str) -> bool:
    return all(0 <= int(octet) <= 255 for octet in value.split("."))


class PIIDetector:
    def classify_column(self, column: str) -> PIIType | None:
        normalized = re.sub(r"[^a-z0-9]+", "_", column.strip().lower()).strip("_")
        return SENSITIVE_COLUMN_TYPES.get(normalized)

    def detect(self, rows: Sequence[Mapping[str, str]]) -> list[PIIFinding]:
        findings: list[PIIFinding] = []
        seen: set[tuple[int, str, PIIType, str]] = set()

        for row_index, row in enumerate(rows, start=1):
            for column, value in row.items():
                if not value.strip() or _REDACTION_TOKEN.fullmatch(value.strip()):
                    continue
                column_type = self.classify_column(column)
                matches = list(self._pattern_matches(value))

                exact = next(
                    (
                        (pii_type, matched)
                        for pii_type, matched, start, end in matches
                        if start == 0 and end == len(value)
                    ),
                    None,
                )
                if column_type is not None and (exact is None or exact[0] != column_type):
                    self._add(
                        findings,
                        seen,
                        row_index,
                        column,
                        column_type,
                        DetectionSource.COLUMN_CLASSIFICATION,
                        value,
                    )
                    continue

                for pii_type, matched, start, end in matches:
                    source = (
                        DetectionSource.VALUE_PATTERN
                        if start == 0 and end == len(value)
                        else DetectionSource.EMBEDDED_PATTERN
                    )
                    self._add(
                        findings,
                        seen,
                        row_index,
                        column,
                        pii_type,
                        source,
                        matched,
                    )
        return findings

    @staticmethod
    def _add(
        findings: list[PIIFinding],
        seen: set[tuple[int, str, PIIType, str]],
        row_index: int,
        column: str,
        pii_type: PIIType,
        source: DetectionSource,
        original_value: str,
    ) -> None:
        key = (row_index, column, pii_type, original_value)
        if key in seen:
            return
        seen.add(key)
        findings.append(
            PIIFinding(
                row_index=row_index,
                column=column,
                type=pii_type,
                source=source,
                original_value=original_value,
            )
        )

    @staticmethod
    def _pattern_matches(value: str) -> Iterator[tuple[PIIType, str, int, int]]:
        patterns = (
            (PIIType.EMAIL, _EMAIL),
            (PIIType.PHONE, _PHONE),
            (PIIType.SSN, _SSN),
        )
        for pii_type, pattern in patterns:
            for match in pattern.finditer(value):
                yield pii_type, match.group(), match.start(), match.end()
        for match in _IPV4_CANDIDATE.finditer(value):
            if _valid_ipv4(match.group()):
                yield PIIType.IP_ADDRESS, match.group(), match.start(), match.end()
