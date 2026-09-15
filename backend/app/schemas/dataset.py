from typing import Literal

from pydantic import BaseModel

InferredType = Literal["string", "integer", "number", "boolean", "date", "empty"]


class DatasetSummary(BaseModel):
    filename: str
    file_size_bytes: int
    row_count: int
    column_count: int
    duplicate_row_count: int


class ColumnProfile(BaseModel):
    name: str
    inferred_type: InferredType
    empty_count: int
    unique_count: int


class DatasetProfileResponse(BaseModel):
    dataset: DatasetSummary
    columns: list[ColumnProfile]
    sample_rows: list[dict[str, str]]
    status: Literal["PROFILED"] = "PROFILED"
