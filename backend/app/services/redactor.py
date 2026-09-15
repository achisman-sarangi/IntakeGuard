from collections.abc import Mapping, Sequence

from app.schemas.pii import DetectionSource, PIIFinding, PIIType

REPLACEMENT_TOKENS: dict[PIIType, str] = {
    PIIType.EMAIL: "[REDACTED_EMAIL]",
    PIIType.PHONE: "[REDACTED_PHONE]",
    PIIType.SSN: "[REDACTED_SSN]",
    PIIType.IP_ADDRESS: "[REDACTED_IP]",
    PIIType.PERSON_NAME: "[REDACTED_NAME]",
}


class Redactor:
    def redact(
        self,
        rows: Sequence[Mapping[str, str]],
        findings: Sequence[PIIFinding],
    ) -> list[dict[str, str]]:
        transformed = [dict(row) for row in rows]

        for finding in findings:
            row_position = finding.row_index - 1
            if not 0 <= row_position < len(transformed):
                raise ValueError(f"Finding row index {finding.row_index} is out of range.")
            if finding.column not in transformed[row_position]:
                raise ValueError(f"Finding column {finding.column!r} does not exist.")

            token = REPLACEMENT_TOKENS[finding.type]
            if finding.source is DetectionSource.COLUMN_CLASSIFICATION:
                transformed[row_position][finding.column] = token
            else:
                transformed[row_position][finding.column] = transformed[row_position][
                    finding.column
                ].replace(finding.original_value, token)

        return transformed
