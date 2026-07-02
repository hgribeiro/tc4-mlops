from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

POLICY_VERSION = "baseline_deterministic_v0.1"
DECISION_TYPE = "responsible_next_step"

VALID_COLLATERALS = {"vehicle", "home", "investment"}
VALID_CHANNELS = {"superapp", "branch", "specialist", "hybrid"}
VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
VALID_CONFIDENCE = {"low", "medium", "high"}
EXCESSIVE_CONTACT_LIMIT = 4

CANONICAL_ACTIONS = [
    "simulate_vehicle_secured_loan",
    "simulate_home_equity",
    "simulate_investment_secured_loan",
    "educational_content_secured_credit",
    "request_documents",
    "route_to_specialist",
    "no_offer_now",
]

MINIMIZED_CONTEXT_FIELDS = [
    "schema_version",
    "synthetic_customer_id",
    "source_dataset",
    "random_seed",
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
    "contact_repetition_count",
    "collateral_detail_status",
    "collateral_complexity",
    "risk_communication_available",
    "human_review_hint",
]

REQUIRED_FIELDS = [
    "request_id",
    "schema_version",
    "synthetic_customer_id",
    "source_dataset",
    "random_seed",
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
    "contact_repetition_count",
    "collateral_detail_status",
    "collateral_complexity",
    "risk_communication_available",
    "known_guardrail_flags",
    "human_review_hint",
    "allowed_input_features",
]

# Field names are treated case-insensitively. The list blocks personal data,
# sensitive attributes, real financial values and known temporal leakage.
PROHIBITED_FIELD_NAMES = {
    "cpf",
    "tax_id",
    "document_number",
    "name",
    "full_name",
    "email",
    "phone",
    "telephone",
    "address",
    "birth_date",
    "gender",
    "race",
    "ethnicity",
    "religion",
    "health",
    "sexual_orientation",
    "real_income",
    "income",
    "salary",
    "real_wealth",
    "wealth",
    "net_worth",
    "real_balance",
    "bank_account",
    "account_number",
    "credit_score_real",
    "private_bank_rule",
}


@dataclass(frozen=True)
class Selection:
    action: str
    eligible_actions: List[str]
    reason_codes: List[str]
    requires_human_review: bool


def decide(context: Mapping[str, Any], audit_log_dir: Path) -> Dict[str, Any]:
    """Decide the responsible next step and append a minimized audit log."""
    guardrails = _evaluate_guardrails(context)
    selection = _select_action(context, guardrails)
    decision_id = f"dec_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    audit_log_ref = _append_audit_log(
        audit_log_dir=audit_log_dir,
        decision_id=decision_id,
        decided_at=now,
        context=context,
        selection=selection,
        guardrails=guardrails,
    )

    return {
        "decision_id": decision_id,
        "request_id": str(context.get("request_id", "")),
        "decision_type": DECISION_TYPE,
        "selected_action": selection.action,
        "eligible_actions": selection.eligible_actions,
        "policy_version": POLICY_VERSION,
        "reason_codes": selection.reason_codes,
        "requires_human_review": selection.requires_human_review,
        "guardrails_triggered": guardrails,
        "audit_log_ref": str(audit_log_ref),
        "not_credit_approval": True,
        "not_credit_contracting": True,
        "does_not_define_real_rate": True,
        "does_not_define_real_limit": True,
        "not_simulated_qualified_proposal": True,
        "requires_formal_credit_analysis": True,
        "message": (
            "Esta decisão recomenda um Próximo Passo Responsável de jornada para um "
            "Cliente Sintético; pode iniciar uma simulação, mas não representa aprovação, "
            "não cria Proposta Qualificada Simulada, não representa contratação e não define "
            "taxa ou limite real de crédito."
        ),
    }


def _evaluate_guardrails(context: Mapping[str, Any]) -> List[str]:
    guardrails: List[str] = []

    missing = [field for field in REQUIRED_FIELDS if field not in context]
    if missing:
        guardrails.append("missing_required_context")

    if context.get("channel") not in VALID_CHANNELS:
        guardrails.append("invalid_channel")

    if context.get("collateral_type") not in VALID_COLLATERALS:
        guardrails.append("unsupported_collateral")

    if context.get("synthetic_risk_level") not in VALID_RISK_LEVELS:
        guardrails.append("invalid_synthetic_risk_level")
    elif context.get("synthetic_risk_level") == "critical":
        guardrails.append("adversarial_or_unsafe_context")

    if context.get("policy_confidence") not in VALID_CONFIDENCE:
        guardrails.append("invalid_policy_confidence")

    if _as_int(context.get("contact_repetition_count"), default=0) >= EXCESSIVE_CONTACT_LIMIT:
        guardrails.append("excessive_contact_repetition")

    allowed_features = context.get("allowed_input_features")
    if isinstance(allowed_features, list) and "duration" in {str(f).lower() for f in allowed_features}:
        guardrails.append("temporal_leakage_duration")

    if _contains_prohibited_field(context):
        guardrails.append("prohibited_personal_data")

    for flag in context.get("known_guardrail_flags", []) or []:
        normalized = str(flag).strip()
        if normalized and normalized not in guardrails:
            guardrails.append(normalized)

    return guardrails


def _select_action(context: Mapping[str, Any], guardrails: List[str]) -> Selection:
    critical_guardrails = {
        "invalid_channel",
        "unsupported_collateral",
        "adversarial_or_unsafe_context",
        "excessive_contact_repetition",
        "temporal_leakage_duration",
        "prohibited_personal_data",
        "missing_required_context",
        "invalid_synthetic_risk_level",
        "invalid_policy_confidence",
    }
    if critical_guardrails.intersection(guardrails):
        return Selection(
            action="no_offer_now",
            eligible_actions=["no_offer_now"],
            reason_codes=_unique(
                [
                    _reason_for_guardrail(g)
                    for g in guardrails
                    if g in critical_guardrails
                ]
                + ["no_responsible_action_available", "approval_clarification_needed"]
            ),
            requires_human_review=False,
        )

    collateral = str(context.get("collateral_type", ""))
    channel = str(context.get("channel", ""))
    risk = str(context.get("synthetic_risk_level", ""))
    confidence = str(context.get("policy_confidence", ""))
    engagement = str(context.get("engagement_level", ""))
    completeness = str(context.get("context_completeness", ""))
    detail_status = str(context.get("collateral_detail_status", ""))
    complexity = str(context.get("collateral_complexity", ""))
    relationship = str(context.get("relationship_tier", ""))
    journey_stage = str(context.get("journey_stage", ""))
    human_review_hint = bool(context.get("human_review_hint", False))
    risk_communication = bool(context.get("risk_communication_available", False))

    eligible = _eligible_actions_for_context(context)

    if completeness == "partial" or detail_status in {"missing", "partial"}:
        return Selection(
            action="request_documents",
            eligible_actions=_ordered_subset(eligible, ["request_documents", "educational_content_secured_credit", "route_to_specialist", "no_offer_now"]),
            reason_codes=["documentation_required", "context_incomplete_but_recoverable", "collateral_details_missing", "approval_clarification_needed"],
            requires_human_review=collateral == "home" or complexity == "high" or human_review_hint,
        )

    if completeness == "insufficient" or journey_stage == "awareness" or engagement == "low":
        return Selection(
            action="educational_content_secured_credit",
            eligible_actions=_ordered_subset(eligible, ["educational_content_secured_credit", "request_documents", "no_offer_now"]),
            reason_codes=["education_before_simulation", "insufficient_context", "early_journey_stage", "approval_clarification_needed"],
            requires_human_review=human_review_hint,
        )

    if risk == "high" or confidence == "low" or complexity == "high" or human_review_hint:
        reason_codes = ["specialist_required", "high_value_or_complex_case"]
        if collateral == "home":
            reason_codes.extend(["home_collateral_complexity", "specialist_guidance_required"])
        if complexity == "high":
            reason_codes.append("collateral_complexity")
        if confidence == "low":
            reason_codes.append("low_policy_confidence")
        if risk == "high":
            reason_codes.append("high_synthetic_risk")
        reason_codes.append("human_in_the_loop")

        return Selection(
            action="route_to_specialist",
            eligible_actions=_ordered_subset(eligible, ["route_to_specialist", "request_documents", "educational_content_secured_credit", "no_offer_now"]),
            reason_codes=_unique(reason_codes),
            requires_human_review=True,
        )

    if collateral == "vehicle" and channel == "superapp" and engagement == "high" and risk in {"low", "medium"}:
        return Selection(
            action="simulate_vehicle_secured_loan",
            eligible_actions=_ordered_subset(eligible, ["simulate_vehicle_secured_loan", "educational_content_secured_credit", "request_documents", "no_offer_now"]),
            reason_codes=["vehicle_collateral_anchor", "digital_channel_fit", "sufficient_context_for_simulation", "qualified_intent_signal", "low_or_medium_synthetic_risk", "no_critical_guardrail_triggered"],
            requires_human_review=False,
        )

    if collateral == "home":
        return Selection(
            action="simulate_home_equity",
            eligible_actions=_ordered_subset(eligible, ["simulate_home_equity", "route_to_specialist", "request_documents", "no_offer_now"]),
            reason_codes=["home_equity_requires_guidance", "simulation_preferred_over_direct_offer", "human_review_recommended", "longer_delayed_reward_expected"],
            requires_human_review=True,
        )

    if collateral == "investment" and relationship == "high_relationship" and risk_communication:
        return Selection(
            action="simulate_investment_secured_loan",
            eligible_actions=_ordered_subset(eligible, ["simulate_investment_secured_loan", "route_to_specialist", "educational_content_secured_credit", "request_documents", "no_offer_now"]),
            reason_codes=["investment_collateral_candidate", "relationship_context_supports_simulation", "risk_communication_required", "human_review_if_sensitive"],
            requires_human_review=False,
        )

    return Selection(
        action="educational_content_secured_credit",
        eligible_actions=_ordered_subset(eligible, ["educational_content_secured_credit", "request_documents", "route_to_specialist", "no_offer_now"]),
        reason_codes=["education_before_simulation", "responsible_personalization", "approval_clarification_needed"],
        requires_human_review=human_review_hint,
    )


def _eligible_actions_for_context(context: Mapping[str, Any]) -> List[str]:
    collateral = str(context.get("collateral_type", ""))
    channel = str(context.get("channel", ""))
    actions = ["educational_content_secured_credit", "request_documents", "route_to_specialist", "no_offer_now"]

    if collateral == "vehicle" and channel in {"superapp", "hybrid"}:
        actions.insert(0, "simulate_vehicle_secured_loan")
    if collateral == "home" and channel in {"superapp", "branch", "specialist", "hybrid"}:
        actions.insert(0, "simulate_home_equity")
    if collateral == "investment" and channel in {"superapp", "branch", "specialist", "hybrid"}:
        actions.insert(0, "simulate_investment_secured_loan")

    return _ordered_subset(actions, CANONICAL_ACTIONS)


def _append_audit_log(
    audit_log_dir: Path,
    decision_id: str,
    decided_at: str,
    context: Mapping[str, Any],
    selection: Selection,
    guardrails: List[str],
) -> Path:
    event_timestamp = str(context.get("event_timestamp") or decided_at)
    date_part = event_timestamp[:10] if len(event_timestamp) >= 10 else decided_at[:10]
    audit_log_dir.mkdir(parents=True, exist_ok=True)
    audit_path = audit_log_dir / f"{date_part}.jsonl"

    record = {
        "decision_id": decision_id,
        "request_id": str(context.get("request_id", "")),
        "logged_at": decided_at,
        "policy_version": POLICY_VERSION,
        "selected_action": selection.action,
        "eligible_actions": selection.eligible_actions,
        "reason_codes": selection.reason_codes,
        "guardrails_triggered": guardrails,
        "requires_human_review": selection.requires_human_review,
        "context_minimized": _minimize_context(context),
        "dropped_prohibited_fields_count": _count_prohibited_fields(context),
        "config_ref": "docs/product/offer-arms.md#baseline-deterministico-inicial",
        "environment": "local_demo",
        "not_credit_approval": True,
        "not_credit_contracting": True,
        "does_not_define_real_rate": True,
        "does_not_define_real_limit": True,
        "not_simulated_qualified_proposal": True,
        "requires_formal_credit_analysis": True,
    }
    with audit_path.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return audit_path


def _minimize_context(context: Mapping[str, Any]) -> Dict[str, Any]:
    return {field: context[field] for field in MINIMIZED_CONTEXT_FIELDS if field in context}


def _contains_prohibited_field(value: Any) -> bool:
    return _count_prohibited_fields(value) > 0


def _count_prohibited_fields(value: Any) -> int:
    count = 0
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key).lower() in PROHIBITED_FIELD_NAMES:
                count += 1
            count += _count_prohibited_fields(nested)
    elif isinstance(value, list):
        for item in value:
            count += _count_prohibited_fields(item)
    return count


def _reason_for_guardrail(guardrail: str) -> str:
    return {
        "invalid_channel": "invalid_channel",
        "unsupported_collateral": "synthetic_ineligibility",
        "adversarial_or_unsafe_context": "adversarial_or_unsafe_context",
        "excessive_contact_repetition": "excessive_contact_repetition",
        "temporal_leakage_duration": "no_responsible_action_available",
        "prohibited_personal_data": "no_responsible_action_available",
        "missing_required_context": "insufficient_context",
        "invalid_synthetic_risk_level": "synthetic_ineligibility",
        "invalid_policy_confidence": "synthetic_ineligibility",
    }.get(guardrail, "no_responsible_action_available")


def _ordered_subset(values: Iterable[str], preferred_order: Iterable[str]) -> List[str]:
    value_set = set(values)
    ordered = [item for item in preferred_order if item in value_set]
    return ordered if "no_offer_now" in ordered else ordered + ["no_offer_now"]


def _unique(values: Iterable[str]) -> List[str]:
    result: List[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
