import csv
import io
import re
from datetime import date

from app.schemas.dataset import (
    ColumnProfile,
    DatasetProfileResponse,
    DatasetSummary,
    InferredType,
)

MAX_SAMPLE_ROWS = 5
_INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
_NUMBER_PATTERN = re.compile(
    r"^[+-]?(?:(?:\d+\.\d*)|(?:\d*\.\d+))(?:[eE][+-]?\d+)?$"
    r"|^[+-]?\d+[eE][+-]?\d+$"
)


class DatasetProfileError(ValueError):
    """Raised when input cannot be profiled as a structurally valid CSV."""


class DatasetProfiler:
    def profile(self, content: bytes, filename: str) -> DatasetProfileResponse:
        header, rows = self.parse(content)
        row_tuples = [tuple(row[name] for name in header) for row in rows]

        columns = [
            self._profile_column(name, [row[name] for row in rows])
            for name in header
        ]
        duplicate_count = len(row_tuples) - len(set(row_tuples))

        return DatasetProfileResponse(
            dataset=DatasetSummary(
                filename=filename,
                file_size_bytes=len(content),
                row_count=len(rows),
                column_count=len(header),
                duplicate_row_count=duplicate_count,
            ),
            columns=columns,
            sample_rows=rows[:MAX_SAMPLE_ROWS],
        )

    def parse(self, content: bytes) -> tuple[list[str], list[dict[str, str]]]:
        if not content:
            raise DatasetProfileError("CSV file is empty.")

        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DatasetProfileError("CSV file must be UTF-8 encoded.") from exc

        if not text.strip():
            raise DatasetProfileError("CSV file is empty.")

        return self._parse(text)

    @staticmethod
    def _parse(text: str) -> tuple[list[str], list[dict[str, str]]]:
        try:
            reader = csv.reader(io.StringIO(text, newline=""), strict=True)
            raw_rows = list(reader)
        except (csv.Error, UnicodeError) as exc:
            raise DatasetProfileError("Malformed CSV file.") from exc

        if not raw_rows:
            raise DatasetProfileError("CSV file is empty.")

        header = raw_rows[0]
        if not header or any(not name.strip() for name in header):
            raise DatasetProfileError("CSV must contain a non-empty header row.")
        if len(set(header)) != len(header):
            raise DatasetProfileError("CSV header names must be unique.")

        rows: list[dict[str, str]] = []
        for line_number, values in enumerate(raw_rows[1:], start=2):
            if len(values) != len(header):
                raise DatasetProfileError(
                    f"Malformed CSV: row {line_number} has {len(values)} fields; "
                    f"expected {len(header)}."
                )
            rows.append(dict(zip(header, values, strict=True)))
        return header, rows

    @staticmethod
    def _profile_column(name: str, values: list[str]) -> ColumnProfile:
        non_empty = [value for value in values if value.strip()]
        return ColumnProfile(
            name=name,
            inferred_type=infer_type(non_empty),
            empty_count=len(values) - len(non_empty),
            unique_count=len(set(values)),
        )


def infer_type(non_empty_values: list[str]) -> InferredType:
    if not non_empty_values:
        return "empty"

    inferred = {_infer_value(value.strip()) for value in non_empty_values}
    if len(inferred) == 1:
        return inferred.pop()
    if inferred <= {"integer", "number"}:
        return "number"
    return "string"


def _infer_value(value: str) -> InferredType:
    if value.lower() in {"true", "false"}:
        return "boolean"
    if _INTEGER_PATTERN.fullmatch(value):
        return "integer"
    if _NUMBER_PATTERN.fullmatch(value):
        return "number"
    try:
        date.fromisoformat(value)
    except ValueError:
        return "string"
    return "date"
