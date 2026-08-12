from __future__ import annotations

import json
import logging
import os
from importlib import resources
from pathlib import Path
from typing import Any, Literal, Mapping, cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel, ConfigDict

from .audit import AuditPersistence, LocalAuditPersistence, S3AuditPersistence
from .engine import decide

logger = logging.getLogger(__name__)
# Lambda's default root logger is WARNING; this named logger must emit the
# deliberately minimized decision events used by the CloudWatch metric filter.
logger.setLevel(logging.INFO)

ScenarioId = Literal["vehicle_simple", "home_complex", "guardrail_sensitive"]
PolicyMode = Literal["baseline", "adaptive"]


class DecisionRequest(BaseModel):
    """Closed public input contract for the synthetic demonstration."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: ScenarioId
    policy_mode: PolicyMode


class AuditUnavailableError(RuntimeError):
    """Internal marker that keeps adapter failures separate from policy failures."""


class _FailClosedAuditPersistence:
    def __init__(self, persistence: AuditPersistence) -> None:
        self.persistence = persistence

    def persist(self, record: Mapping[str, Any]) -> str:
        try:
            return self.persistence.persist(record)
        except Exception as exc:
            raise AuditUnavailableError from exc


def create_app(
    *,
    audit_persistence: AuditPersistence | None = None,
    adaptive_enabled: bool | None = None,
    policy_artifact: Mapping[str, Any] | None = None,
) -> FastAPI:
    """Build the thin HTTP layer over the existing responsible decision engine."""
    assets = _load_demo_assets()
    scenarios = cast(dict[str, dict[str, Any]], assets["scenarios"])
    packaged_policy = cast(dict[str, Any], assets["adaptive_policy"])
    configured_persistence = (
        audit_persistence if audit_persistence is not None else _audit_persistence_from_env()
    )
    persistence = _FailClosedAuditPersistence(configured_persistence)
    is_adaptive_enabled = (
        _read_boolean_env("ADAPTIVE_ENABLED", default=True)
        if adaptive_enabled is None
        else adaptive_enabled
    )
    selected_policy = packaged_policy if policy_artifact is None else policy_artifact

    application = FastAPI(
        title="API de Demonstração — Próximo Passo Responsável",
        version="1.0.0",
        description=(
            "Executa somente cenários oficiais de Clientes Sintéticos. "
            "Não aprova, contrata, precifica nem define limite de crédito."
        ),
    )

    @application.exception_handler(RequestValidationError)
    async def invalid_request(
        _request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": "Requisição inválida para a API de Demonstração."},
        )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/ready")
    def ready() -> dict[str, str]:
        return {"status": "ready"}

    @application.post("/v1/decisions")
    def create_decision(request: DecisionRequest) -> dict[str, Any]:
        if request.policy_mode == "adaptive" and not is_adaptive_enabled:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Política Adaptativa pausada; selecione explicitamente o "
                    "Baseline Determinístico."
                ),
            )

        try:
            decision = decide(
                scenarios[request.scenario_id],
                persistence,
                policy_mode=request.policy_mode,
                policy_artifact=(
                    selected_policy if request.policy_mode == "adaptive" else None
                ),
            )
        except AuditUnavailableError as exc:
            _log_telemetry("audit_unavailable", policy_mode=request.policy_mode)
            raise HTTPException(
                status_code=503,
                detail="Auditoria indisponível.",
            ) from exc
        except ValueError as exc:
            _log_telemetry("adaptive_unavailable", policy_mode=request.policy_mode)
            raise HTTPException(
                status_code=503,
                detail="Política Adaptativa indisponível.",
            ) from exc

        _log_telemetry(
            "decision",
            policy_mode=request.policy_mode,
            selected_action=decision["selected_action"],
            guardrails_count=len(decision["guardrails_triggered"]),
            requires_human_review=decision["requires_human_review"],
        )
        return decision

    return application


def _log_telemetry(event: str, **attributes: Any) -> None:
    """Emit only aggregate decision metadata; never request or audit payloads."""
    logger.info(json.dumps({"event": event, **attributes}, sort_keys=True))


def _audit_persistence_from_env() -> AuditPersistence:
    backend = os.getenv("AUDIT_BACKEND", "local").strip().lower()
    if backend == "local":
        return LocalAuditPersistence(Path(os.getenv("AUDIT_LOG_DIR", "logs/decisions")))
    if backend == "s3":
        return S3AuditPersistence(
            bucket=os.getenv("AUDIT_S3_BUCKET", ""),
            prefix=os.getenv("AUDIT_S3_PREFIX", "decisions"),
            endpoint_url=os.getenv("AUDIT_S3_ENDPOINT_URL"),
        )
    raise RuntimeError("AUDIT_BACKEND deve ser 'local' ou 's3'")


def _load_demo_assets() -> dict[str, Any]:
    asset = resources.files("responsible_next_step").joinpath("demo_assets.json")
    with asset.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise RuntimeError("demo_assets.json deve conter um objeto JSON")
    expected_scenarios = {
        "vehicle_simple",
        "home_complex",
        "guardrail_sensitive",
    }
    if payload.get("schema_version") != "demo_assets_v0.1":
        raise RuntimeError("schema_version dos ativos de demonstração incompatível")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, dict) or set(scenarios) != expected_scenarios:
        raise RuntimeError("catálogo de cenários oficiais incompatível")
    if not isinstance(payload.get("adaptive_policy"), dict):
        raise RuntimeError("Política Adaptativa oficial ausente")
    return payload


def _read_boolean_env(name: str, *, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} deve ser booleano")


app = create_app()
handler = Mangum(app, lifespan="off")
