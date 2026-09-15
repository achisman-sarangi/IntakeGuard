import pytest

from app.services.dataset_profiler import (
    DatasetProfileError,
    DatasetProfiler,
    infer_type,
)


def test_profiles_normal_csv_statistics() -> None:
    content = (
        b"id,cost,active,created_at,note\n"
        b"1,12.50,true,2026-09-15,ready\n"
        b"2,,false,2026-09-16,ready\n"
        b"2,,false,2026-09-16,ready\n"
    )

    result = DatasetProfiler().profile(content, "input.csv")
    columns = {column.name: column for column in result.columns}

    assert result.dataset.filename == "input.csv"
    assert result.dataset.file_size_bytes == len(content)
    assert result.dataset.row_count == 3
    assert result.dataset.column_count == 5
    assert result.dataset.duplicate_row_count == 1
    assert columns["cost"].empty_count == 2
    assert columns["note"].unique_count == 1
    assert columns["id"].inferred_type == "integer"
    assert columns["cost"].inferred_type == "number"
    assert columns["active"].inferred_type == "boolean"
    assert columns["created_at"].inferred_type == "date"
    assert result.sample_rows[0]["note"] == "ready"
    assert result.status == "PROFILED"


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (["1", "-2", "+3"], "integer"),
        (["1.5", "2", "3e2"], "number"),
        (["true", "FALSE"], "boolean"),
        (["2026-09-15", "2025-01-01"], "date"),
        (["1", "unknown"], "string"),
        ([], "empty"),
    ],
)
def test_type_inference(values: list[str], expected: str) -> None:
    assert infer_type(values) == expected


def test_sample_rows_are_bounded() -> None:
    content = "id\n" + "\n".join(str(value) for value in range(10)) + "\n"
    result = DatasetProfiler().profile(content.encode(), "rows.csv")
    assert len(result.sample_rows) == 5


@pytest.mark.parametrize(
    "content",
    [
        b'a,b\n"unterminated,1\n',
        b"a,b\n1,2,3\n",
        b",b\n1,2\n",
        b"a,a\n1,2\n",
    ],
)
def test_rejects_malformed_or_invalid_csv(content: bytes) -> None:
    with pytest.raises(DatasetProfileError):
        DatasetProfiler().profile(content, "bad.csv")


@pytest.mark.parametrize("content", [b"", b" \r\n"])
def test_rejects_empty_csv(content: bytes) -> None:
    with pytest.raises(DatasetProfileError, match="empty"):
        DatasetProfiler().profile(content, "empty.csv")
