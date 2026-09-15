import pytest
from fastapi.testclient import TestClient

from app.main import app, parse_cors_allowed_origins

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "intakeguard"}


def test_local_frontend_origin_is_allowed_by_cors() -> None:
    response = client.options(
        "/api/intake/validate",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_origins_are_parsed_trimmed_and_deduplicated() -> None:
    assert parse_cors_allowed_origins(
        " https://intakeguard.vercel.app/, ,http://localhost:5173,"
        "https://intakeguard.vercel.app "
    ) == ["https://intakeguard.vercel.app", "http://localhost:5173"]


def test_cors_defaults_to_local_development_origins() -> None:
    assert parse_cors_allowed_origins(None) == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@pytest.mark.parametrize(
    "value",
    ["*", "https://example.com/path", "javascript:alert(1)", "not-an-origin"],
)
def test_cors_rejects_wildcard_and_malformed_origins(value: str) -> None:
    with pytest.raises(RuntimeError):
        parse_cors_allowed_origins(value)


def test_successful_csv_upload() -> None:
    content = b"id,name\n1,Ada\n2,Grace\n"
    response = client.post(
        "/api/intake/profile",
        files={"file": ("people.csv", content, "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["dataset"]["row_count"] == 2
    assert body["dataset"]["column_count"] == 2
    assert body["columns"][0]["inferred_type"] == "integer"


def test_rejects_unsupported_extension() -> None:
    response = client.post(
        "/api/intake/profile",
        files={"file": ("people.txt", b"id\n1\n", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only .csv files are supported."


def test_rejects_empty_upload() -> None:
    response = client.post(
        "/api/intake/profile",
        files={"file": ("empty.csv", b"", "text/csv")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_rejects_oversized_upload() -> None:
    response = client.post(
        "/api/intake/profile",
        files={"file": ("large.csv", b"x" * (5 * 1024 * 1024 + 1), "text/csv")},
    )
    assert response.status_code == 400
    assert "5 MB" in response.json()["detail"]


def test_successful_csv_redaction() -> None:
    content = (
        b"technician_name,technician_email,failure_notes\n"
        b'Synthetic Person,user@example.com,"Call 415-555-0198 from 10.10.4.21"\n'
    )
    response = client.post(
        "/api/intake/redact",
        files={"file": ("work-orders.csv", content, "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REDACTED"
    assert body["dataset"] == {
        "filename": "work-orders.csv",
        "row_count": 1,
        "column_count": 3,
    }
    assert body["summary"]["total_findings"] == 4
    assert body["summary"]["rows_affected"] == 1
    assert body["preview"]["after"][0] == {
        "technician_name": "[REDACTED_NAME]",
        "technician_email": "[REDACTED_EMAIL]",
        "failure_notes": "Call [REDACTED_PHONE] from [REDACTED_IP]",
    }


def test_redaction_preview_is_bounded() -> None:
    content = ("email\n" + "\n".join(f"user{i}@example.com" for i in range(8))).encode()
    response = client.post(
        "/api/intake/redact",
        files={"file": ("people.csv", content, "text/csv")},
    )
    assert response.status_code == 200
    assert len(response.json()["preview"]["before"]) == 5
    assert len(response.json()["preview"]["after"]) == 5


def test_redact_reuses_upload_validation() -> None:
    unsupported = client.post(
        "/api/intake/redact",
        files={"file": ("people.txt", b"email\nuser@example.com\n", "text/plain")},
    )
    empty = client.post(
        "/api/intake/redact",
        files={"file": ("empty.csv", b"", "text/csv")},
    )
    malformed = client.post(
        "/api/intake/redact",
        files={"file": ("bad.csv", b"a,b\n1,2,3\n", "text/csv")},
    )
    assert unsupported.status_code == 400
    assert empty.status_code == 400
    assert malformed.status_code == 400


def test_successful_csv_validation() -> None:
    content = (
        b"work_order_id,machine_id,email,repair_cost\n"
        b"WO-1,MX-1,user@example.com,12.50\n"
    )
    response = client.post(
        "/api/intake/validate",
        files={"file": ("input.csv", content, "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "READY"
    assert body["validation"]["error_count"] == 0
    assert body["manifest"]["redactions_applied"] == 1
    assert body["preview"]["after"][0]["email"] == "[REDACTED_EMAIL]"


def test_validate_maps_expected_dataset_failures_to_400() -> None:
    for filename, content in (
        ("input.txt", b"a\n1\n"),
        ("empty.csv", b""),
        ("bad.csv", b"a,b\n1,2,3\n"),
    ):
        response = client.post(
            "/api/intake/validate",
            files={"file": (filename, content, "text/csv")},
        )
        assert response.status_code == 400
