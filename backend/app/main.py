import os
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.intake import router as intake_router

LOCAL_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def parse_cors_allowed_origins(value: str | None) -> list[str]:
    if value is None:
        return list(LOCAL_CORS_ORIGINS)

    origins: list[str] = []
    for raw_origin in value.split(","):
        origin = raw_origin.strip().rstrip("/")
        if not origin:
            continue
        if origin == "*":
            raise RuntimeError("CORS_ALLOWED_ORIGINS must not contain a wildcard.")

        parsed = urlsplit(origin)
        try:
            hostname = parsed.hostname
            parsed.port
        except ValueError as exc:
            raise RuntimeError(
                f"Invalid origin in CORS_ALLOWED_ORIGINS: {raw_origin.strip()!r}."
            ) from exc
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or not hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or any(character.isspace() for character in origin)
        ):
            raise RuntimeError(
                f"Invalid origin in CORS_ALLOWED_ORIGINS: {raw_origin.strip()!r}."
            )
        if origin not in origins:
            origins.append(origin)
    return origins


app = FastAPI(title="IntakeGuard", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_allowed_origins(os.getenv("CORS_ALLOWED_ORIGINS")),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(intake_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "intakeguard"}
