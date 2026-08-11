from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping

from . import engine

REPORT_SCHEMA_VERSION = "golden_set_evaluation_report_v0.1"
REQUIRED_CASE_FIELDS = {
    "case_id",
    "description",
    "context",
    "expected_action_class",
    "expected_guardrails_triggered",
    "expected_requires_human_review",
    "expected_reason_codes",
    "expected_success_criterion",
    "justification",
    "pass_fail_criteria",
}
REQUIRED_DECISION_FIELDS = {
    "decision_id",
    "request_id",
    "selected_action",
    "eligible_actions",
    "policy_version",
    "reason_codes",
    "requires_human_review",
    "guardrails_triggered",
    "audit_log_ref",
    "not_credit_approval",
    "requires_formal_credit_analysis",
}
CONTEXT_STRING_FIELDS = {
    "request_id",
    "schema_version",
    "synthetic_customer_id",
    "source_dataset",
    "event_timestamp",
    "collateral_type",
    "channel",
    "journey_stage",
    "synthetic_risk_level",
    "policy_confidence",
    "engagement_level",
    "context_completeness",
    "synthetic_segment",
    "relationship_tier",
    "collateral_detail_status",
    "collateral_complexity",
}
DOCUMENTED_EXPECTED_REASON_CODES = {
    "adversarial_or_unsafe_context",
    "approval_clarification_needed",
    "collateral_complexity",
    "collateral_details_missing",
    "context_incomplete_but_recoverable",
    "digital_channel_fit",
    "documentation_required",
    "early_journey_stage",
    "education_before_simulation",
    "human_in_the_loop",
    "insufficient_context",
    "low_policy_confidence",
    "no_critical_guardrail_triggered",
    "no_responsible_action_available",
    "specialist_required",
    "sufficient_context_for_simulation",
    "vehicle_collateral_anchor",
}
CONTEXT_ENUMS = {
    "schema_version": {"synthetic_customer_context_v0.1"},
    "source_dataset": {"golden_set"},
    "collateral_type": engine.VALID_COLLATERALS,
    "channel": engine.VALID_CHANNELS,
    "journey_stage": {"awareness", "simulation", "documentation", "proposal", "follow_up"},
    "synthetic_risk_level": engine.VALID_RISK_LEVELS,
    "policy_confidence": engine.VALID_CONFIDENCE,
    "engagement_level": {"low", "medium", "high"},
    "context_completeness": {"insufficient", "partial", "sufficient"},
    "synthetic_segment": {
        "digital_simple",
        "collateral_complex",
        "high_relationship_synthetic",
        "education_first",
        "documentation_needed",
        "guardrail_sensitive",
        "cold_start",
    },
    "relationship_tier": {"standard", "high_relationship"},
    "collateral_detail_status": {"missing", "partial", "complete"},
    "collateral_complexity": {"low", "medium", "high"},
}


def evaluate_golden_set(
    golden_set_path: str | Path,
    audit_log_dir: str | Path,
) -> Dict[str, Any]:
    """Execute the deterministic baseline against a versioned golden set."""
    path = Path(golden_set_path)
    cases = _load_cases(path)
    results: List[Dict[str, Any]] = []

    for evaluation_case in cases:
        decision = engine.decide(evaluation_case["context"], Path(audit_log_dir))
        failures = _evaluate_case(evaluation_case, decision)
        results.append(
            {
                "case_id": evaluation_case["case_id"],
                "description": evaluation_case["description"],
                "expected_action": evaluation_case["expected_action_class"],
                "actual_action": decision.get("selected_action"),
                "policy_version": decision.get("policy_version"),
                "expected_success_criterion": evaluation_case[
                    "expected_success_criterion"
                ],
                "justification": evaluation_case["justification"],
                "pass_fail_criteria": evaluation_case["pass_fail_criteria"],
                "passed": not failures,
                "failures": failures,
                "reason_codes": decision.get("reason_codes")
                if isinstance(decision.get("reason_codes"), list)
                else [],
                "guardrails_triggered": decision.get("guardrails_triggered")
                if isinstance(decision.get("guardrails_triggered"), list)
                else [],
                "requires_human_review": decision.get(
                    "requires_human_review", False
                ),
                "audit_log_ref": decision.get("audit_log_ref"),
            }
        )

    passed = sum(result["passed"] for result in results)
    valid_logs = sum(not any("log auditável" in failure for failure in result["failures"]) for result in results)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "golden_set_ref": str(path),
        "policy_version": results[0]["policy_version"],
        "total_cases": len(results),
        "passed_cases": passed,
        "failed_cases": len(results) - passed,
        "all_passed": passed == len(results),
        "cases": results,
        "coverage": {
            "selected_actions": sorted(
                {
                    result["actual_action"]
                    for result in results
                    if isinstance(result["actual_action"], str)
                }
            ),
            "guardrails": sorted(
                {
                    guardrail
                    for result in results
                    for guardrail in result["guardrails_triggered"]
                }
            ),
            "reason_codes": sorted(
                {
                    reason
                    for result in results
                    for reason in result["reason_codes"]
                }
            ),
            "audit_logs": {
                "expected": len(results),
                "valid": valid_logs,
                "coverage_rate": valid_logs / len(results),
            },
        },
    }


def _load_cases(path: Path) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    case_ids: set[str] = set()
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        value = json.loads(raw_line)
        if not isinstance(value, dict):
            raise ValueError(f"caso na linha {line_number} deve ser um objeto")
        missing = sorted(REQUIRED_CASE_FIELDS - value.keys())
        if missing:
            raise ValueError(
                f"caso na linha {line_number} não contém campos obrigatórios: {missing}"
            )
        for field in REQUIRED_CASE_FIELDS - {"context"}:
            if field in {
                "expected_guardrails_triggered",
                "expected_requires_human_review",
                "expected_reason_codes",
            }:
                continue
            if not isinstance(value[field], str) or not value[field].strip():
                raise ValueError(
                    f"{field} na linha {line_number} deve ser uma string não vazia"
                )
        if value["case_id"] in case_ids:
            raise ValueError(f"case_id duplicado na linha {line_number}")
        case_ids.add(value["case_id"])
        if not isinstance(value["context"], dict):
            raise ValueError(f"context na linha {line_number} deve ser um objeto")
        _validate_context(value["context"], line_number)
        for field in ("expected_guardrails_triggered", "expected_reason_codes"):
            if not isinstance(value[field], list) or not all(
                isinstance(item, str) and item.strip() for item in value[field]
            ):
                raise ValueError(
                    f"{field} na linha {line_number} deve ser uma lista de strings"
                )
        if value["expected_action_class"] not in engine.CANONICAL_ACTIONS:
            raise ValueError(
                f"expected_action_class na linha {line_number} não é um Braço canônico"
            )
        undocumented_reasons = sorted(
            set(value["expected_reason_codes"]) - DOCUMENTED_EXPECTED_REASON_CODES
        )
        if undocumented_reasons:
            raise ValueError(
                f"expected_reason_codes na linha {line_number} contém códigos não documentados: {undocumented_reasons}"
            )
        if not isinstance(value["expected_requires_human_review"], bool):
            raise ValueError(
                f"expected_requires_human_review na linha {line_number} deve ser booleano"
            )
        cases.append(value)
    if len(cases) != 5:
        raise ValueError(f"o Golden Set oficial deve conter exatamente 5 casos; recebeu {len(cases)}")
    return cases


def _validate_context(context: Mapping[str, Any], line_number: int) -> None:
    missing = sorted(set(engine.REQUIRED_FIELDS) - context.keys())
    if missing:
        raise ValueError(
            f"context na linha {line_number} não contém campos obrigatórios: {missing}"
        )
    for field in CONTEXT_STRING_FIELDS:
        if not isinstance(context[field], str) or not context[field].strip():
            raise ValueError(
                f"context.{field} na linha {line_number} deve ser uma string não vazia"
            )
    for field, allowed_values in CONTEXT_ENUMS.items():
        if context[field] not in allowed_values:
            raise ValueError(
                f"context.{field} na linha {line_number} contém valor inválido"
            )
    if not context["request_id"].startswith("req_"):
        raise ValueError(f"context.request_id na linha {line_number} deve começar com req_")
    if not context["synthetic_customer_id"].startswith("syn_"):
        raise ValueError(
            f"context.synthetic_customer_id na linha {line_number} deve começar com syn_"
        )
    try:
        datetime.fromisoformat(context["event_timestamp"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"context.event_timestamp na linha {line_number} deve usar ISO 8601"
        ) from exc
    source_record_ref = context.get("source_record_ref")
    if source_record_ref is not None and not isinstance(source_record_ref, str):
        raise ValueError(
            f"context.source_record_ref na linha {line_number} deve ser string ou null"
        )
    for field in ("random_seed", "contact_repetition_count"):
        if isinstance(context[field], bool) or not isinstance(context[field], int):
            raise ValueError(
                f"context.{field} na linha {line_number} deve ser um inteiro"
            )
    if context["random_seed"] < 0 or context["contact_repetition_count"] < 0:
        raise ValueError(
            f"context na linha {line_number} não aceita seed ou repetição negativa"
        )
    for field in ("risk_communication_available", "human_review_hint"):
        if not isinstance(context[field], bool):
            raise ValueError(
                f"context.{field} na linha {line_number} deve ser booleano"
            )
    for field in ("known_guardrail_flags", "allowed_input_features"):
        value = context[field]
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            raise ValueError(
                f"context.{field} na linha {line_number} deve ser uma lista de strings"
            )


def _decision_contract_failures(decision: Mapping[str, Any]) -> List[str]:
    missing = sorted(REQUIRED_DECISION_FIELDS - decision.keys())
    if missing:
        return [f"contrato de saída incompleto: {missing}"]

    failures: List[str] = []
    for field in (
        "decision_id",
        "request_id",
        "selected_action",
        "policy_version",
        "audit_log_ref",
    ):
        if not isinstance(decision[field], str) or not decision[field].strip():
            failures.append(f"contrato de saída exige {field} como string não vazia")
    for field in (
        "eligible_actions",
        "reason_codes",
        "guardrails_triggered",
    ):
        value = decision[field]
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value
        ):
            failures.append(f"contrato de saída exige {field} como lista de strings")
    if (
        isinstance(decision["eligible_actions"], list)
        and decision["selected_action"] not in decision["eligible_actions"]
    ):
        failures.append("selected_action deve pertencer a eligible_actions")
    for field in (
        "requires_human_review",
        "not_credit_approval",
        "requires_formal_credit_analysis",
    ):
        if not isinstance(decision[field], bool):
            failures.append(f"contrato de saída exige {field} como booleano")
    return failures


def _evaluate_case(
    evaluation_case: Mapping[str, Any], decision: Mapping[str, Any]
) -> List[str]:
    failures: List[str] = []
    failures.extend(_decision_contract_failures(decision))

    if decision.get("request_id") != evaluation_case["context"].get("request_id"):
        failures.append("request_id não corresponde ao contexto")
    if decision.get("selected_action") != evaluation_case["expected_action_class"]:
        failures.append("ação observada difere da ação esperada")
    if decision.get("guardrails_triggered") != evaluation_case[
        "expected_guardrails_triggered"
    ]:
        failures.append("Guardrails observados diferem dos esperados")
    if decision.get("requires_human_review") is not evaluation_case[
        "expected_requires_human_review"
    ]:
        failures.append("Humano no loop difere do esperado")

    observed_reasons = decision.get("reason_codes")
    actual_reasons = set(observed_reasons) if isinstance(observed_reasons, list) else set()
    missing_reasons = sorted(
        set(evaluation_case["expected_reason_codes"]) - actual_reasons
    )
    if missing_reasons:
        failures.append(f"Reason Codes esperados ausentes: {missing_reasons}")

    if decision.get("policy_version") != engine.POLICY_VERSION:
        failures.append(
            f"avaliação exige policy_version={engine.POLICY_VERSION}"
        )

    for flag in ("not_credit_approval", "requires_formal_credit_analysis"):
        if decision.get(flag) is not True:
            failures.append(f"contrato de saída exige {flag}=true")

    if not _audit_log_matches_decision(decision):
        failures.append("log auditável ausente, inválido ou incoerente")
    return failures


def _audit_log_matches_decision(decision: Mapping[str, Any]) -> bool:
    audit_ref = decision.get("audit_log_ref")
    if not isinstance(audit_ref, str):
        return False
    path = Path(audit_ref)
    if not path.is_file():
        return False
    try:
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    except (OSError, json.JSONDecodeError):
        return False
    matching = [
        record
        for record in records
        if isinstance(record, Mapping)
        and record.get("decision_id") == decision.get("decision_id")
    ]
    if len(matching) != 1:
        return False
    record = matching[0]
    return all(
        record.get(field) == decision.get(field)
        for field in (
            "request_id",
            "selected_action",
            "policy_version",
            "reason_codes",
            "guardrails_triggered",
            "requires_human_review",
        )
    )
