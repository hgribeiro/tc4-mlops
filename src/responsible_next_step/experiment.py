"""Transparent, reproducible offline comparison for responsible journey actions.

Bank Marketing supplies only minimized pre-interaction context and the observed
response target. Multi-arm outcomes are synthetic and therefore must not be
interpreted as causal evidence for real secured-loan decisions.
"""

from __future__ import annotations

import hashlib
import json
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .bank_marketing import PreparedBankMarketing, prepare_bank_marketing

EXPERIMENT_SCHEMA_VERSION = "offline_bandit_experiment_v0.1"
POLICY_ARTIFACT_SCHEMA_VERSION = "adaptive_policy_artifact_v0.1"
ADAPTIVE_POLICY_VERSION = "contextual_thompson_sampling_v0.1"
BASELINE_POLICY_VERSION = "fixed_global_education_v0.1"
CONTEXT_FEATURES = (
    "collateral_type",
    "channel",
    "synthetic_segment",
    "journey_stage",
)
ACTIONS = (
    "simulate_vehicle_secured_loan",
    "simulate_home_equity",
    "simulate_investment_secured_loan",
    "educational_content_secured_credit",
    "request_documents",
    "route_to_specialist",
    "no_offer_now",
)
PRIOR_ALPHA = 1.0
PRIOR_BETA = 1.0


@dataclass(frozen=True)
class ExperimentContext:
    collateral_type: str
    channel: str
    synthetic_segment: str
    journey_stage: str
    contact_repetition_count: int

    def policy_key(self) -> str:
        return "|".join(str(getattr(self, name)) for name in CONTEXT_FEATURES)

    def audit_context(self) -> dict[str, str]:
        return {name: str(getattr(self, name)) for name in CONTEXT_FEATURES}


@dataclass
class Posterior:
    alpha: float = PRIOR_ALPHA
    beta: float = PRIOR_BETA

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def update(self, reward: int) -> None:
        self.alpha += reward
        self.beta += 1 - reward


@dataclass(frozen=True)
class SeedRun:
    metrics: dict[str, Any]
    posteriors: dict[str, dict[str, Posterior]]
    decisions: tuple[dict[str, Any], ...]


def run_offline_experiment(
    csv_path: str | Path,
    output_dir: str | Path,
    *,
    seeds: Sequence[int],
    horizon: int,
) -> dict[str, Any]:
    """Compare a fixed baseline with contextual Thompson Sampling.

    Each seed evaluates both policies on the same deterministic synthetic
    counterfactual draws. Guardrails produce the eligible set before either
    policy selects an action.
    """

    if not seeds:
        raise ValueError("at least one experiment seed is required")
    if horizon <= 0:
        raise ValueError("horizon must be greater than zero")

    prepared = prepare_bank_marketing(csv_path, seed=seeds[0])
    if not prepared.features:
        raise ValueError("the prepared dataset must contain at least one row")

    seed_runs = [
        _run_seed(prepared, seed=seed, horizon=horizon)
        for seed in seeds
    ]
    experiment_ref = _experiment_ref(prepared, seeds, horizon)
    report = _build_report(prepared, seeds, horizon, seed_runs, experiment_ref)
    policy = _build_policy_artifact(seed_runs[-1], seeds[-1], experiment_ref)

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (destination / "policy.json").write_text(
        json.dumps(policy, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (destination / "evaluation_decisions.jsonl").open("w", encoding="utf-8") as log:
        for seed_run in seed_runs:
            for decision in seed_run.decisions:
                log.write(json.dumps(decision, ensure_ascii=False, sort_keys=True) + "\n")
    return report


def _run_seed(
    prepared: PreparedBankMarketing, *, seed: int, horizon: int
) -> SeedRun:
    rng = random.Random(seed)
    posteriors: dict[str, dict[str, Posterior]] = {}
    baseline_reward = 0
    adaptive_reward = 0
    regret = 0.0
    explorations = 0
    exploration_opportunities = 0
    baseline_exposure = {action: 0 for action in ACTIONS}
    adaptive_exposure = {action: 0 for action in ACTIONS}
    decisions: list[dict[str, Any]] = []

    row_count = len(prepared.features)
    offset = seed % row_count
    for step in range(horizon):
        row_index = (offset + step) % row_count
        features = prepared.features[row_index]
        observed_target = prepared.target[row_index]
        context = _synthetic_context(features)
        eligible, guardrails = _eligible_actions(context)
        context_posteriors = posteriors.setdefault(context.policy_key(), {})
        for action in eligible:
            context_posteriors.setdefault(action, Posterior())

        baseline_action = (
            "educational_content_secured_credit"
            if "educational_content_secured_credit" in eligible
            else eligible[0]
        )
        baseline_outcome = _sample_reward(
            seed, step, baseline_action, context, observed_target
        )
        baseline_reward += baseline_outcome
        baseline_exposure[baseline_action] += 1

        greedy_action = max(
            eligible,
            key=lambda action: (context_posteriors[action].mean, -ACTIONS.index(action)),
        )
        samples = {
            action: rng.betavariate(
                context_posteriors[action].alpha, context_posteriors[action].beta
            )
            for action in eligible
        }
        adaptive_action = max(
            eligible, key=lambda action: (samples[action], -ACTIONS.index(action))
        )
        exploration = len(eligible) > 1 and adaptive_action != greedy_action
        exploration_opportunities += int(len(eligible) > 1)
        explorations += int(exploration)

        adaptive_outcome = _sample_reward(
            seed, step, adaptive_action, context, observed_target
        )
        adaptive_reward += adaptive_outcome
        adaptive_exposure[adaptive_action] += 1
        regret += max(
            _reward_probability(context, action, observed_target)
            for action in eligible
        ) - _reward_probability(context, adaptive_action, observed_target)
        # A forced safety outcome is audited but must not teach the policy that
        # no_offer_now is preferable in otherwise unguarded contexts.
        if len(eligible) > 1:
            context_posteriors[adaptive_action].update(adaptive_outcome)

        decisions.extend(
            [
                _audit_decision(
                    seed, step, "baseline", BASELINE_POLICY_VERSION,
                    context, baseline_action, eligible, guardrails, baseline_outcome, False
                ),
                _audit_decision(
                    seed, step, "adaptive", ADAPTIVE_POLICY_VERSION,
                    context, adaptive_action, eligible, guardrails, adaptive_outcome, exploration
                ),
            ]
        )

    return SeedRun(
        metrics={
            "seed": seed,
            "baseline_reward": baseline_reward,
            "adaptive_reward": adaptive_reward,
            "uplift": adaptive_reward - baseline_reward,
            "adaptive_cumulative_regret": regret,
            "exploration_rate": explorations / exploration_opportunities
            if exploration_opportunities
            else 0.0,
            "baseline_exposure": baseline_exposure,
            "adaptive_exposure": adaptive_exposure,
        },
        posteriors=posteriors,
        decisions=tuple(decisions),
    )


def _synthetic_context(features: Mapping[str, Any]) -> ExperimentContext:
    contact = str(features["contact_channel_proxy"])
    previous = int(features["previous_contact_count"])
    outcome = str(features["previous_outcome"])

    if contact == "cellular":
        collateral, channel = "vehicle", "superapp"
    elif contact == "telephone":
        collateral, channel = "home", "hybrid"
    else:
        collateral, channel = "investment", "specialist"

    if outcome == "success":
        segment, stage = "digital_simple", "simulation"
    elif previous > 0:
        segment, stage = "documentation_needed", "documentation"
    else:
        segment, stage = "education_first", "awareness"

    return ExperimentContext(
        collateral_type=collateral,
        channel=channel,
        synthetic_segment=segment,
        journey_stage=stage,
        contact_repetition_count=int(features["contact_repetition_count"]),
    )


def _eligible_actions(context: ExperimentContext) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if context.contact_repetition_count >= 10:
        return ("no_offer_now",), ("excessive_contact_repetition",)

    actions = ["educational_content_secured_credit", "no_offer_now"]
    if context.journey_stage == "documentation":
        actions.extend(["request_documents", "route_to_specialist"])
    elif context.journey_stage == "simulation":
        actions.append({
            "vehicle": "simulate_vehicle_secured_loan",
            "home": "simulate_home_equity",
            "investment": "simulate_investment_secured_loan",
        }[context.collateral_type])
        if context.collateral_type in {"home", "investment"}:
            actions.append("route_to_specialist")
    return tuple(action for action in ACTIONS if action in actions), ()


def _reward_probability(
    context: ExperimentContext, action: str, observed_target: int
) -> float:
    """Documented synthetic contract; this is not an observed causal outcome."""

    probability = 0.03
    if action == "no_offer_now":
        probability = 0.80 if context.contact_repetition_count >= 10 else 0.03
    elif context.journey_stage == "awareness":
        probability = 0.78 if action == "educational_content_secured_credit" else 0.10
    elif context.journey_stage == "documentation":
        probability = {
            "request_documents": 0.82,
            "route_to_specialist": 0.48,
            "educational_content_secured_credit": 0.16,
        }.get(action, 0.04)
    elif context.collateral_type == "vehicle":
        probability = 0.86 if action == "simulate_vehicle_secured_loan" else 0.14
    elif context.collateral_type == "home":
        probability = 0.82 if action == "route_to_specialist" else 0.28
    elif context.collateral_type == "investment":
        probability = 0.80 if action == "route_to_specialist" else 0.25

    # y is used only inside the outcome environment, never as a decision feature.
    if observed_target and action != "no_offer_now":
        probability += 0.06
    return min(max(probability, 0.01), 0.95)


def _sample_reward(
    seed: int,
    step: int,
    action: str,
    context: ExperimentContext,
    observed_target: int,
) -> int:
    digest = hashlib.sha256(f"{seed}|{step}|{action}".encode("utf-8")).digest()
    draw = int.from_bytes(digest[:8], "big") / float(2**64)
    return int(draw < _reward_probability(context, action, observed_target))


def _audit_decision(
    seed: int,
    step: int,
    policy: str,
    policy_version: str,
    context: ExperimentContext,
    action: str,
    eligible: Iterable[str],
    guardrails: Iterable[str],
    reward: int,
    exploration: bool,
) -> dict[str, Any]:
    event_id = hashlib.sha256(
        f"{seed}|{step}|{policy}|{action}".encode("utf-8")
    ).hexdigest()[:16]
    guardrail_list = list(guardrails)
    reason_codes = (
        ["excessive_contact_repetition", "no_responsible_action_available"]
        if guardrail_list
        else ["eligible_after_guardrails", "synthetic_experiment_selection"]
    )
    return {
        "audit_event_id": f"eval_{event_id}",
        "decision_id": f"dec_eval_{event_id}",
        "request_id": f"req_eval_{seed}_{step}_{policy}",
        "seed": seed,
        "step": step,
        "policy": policy,
        "policy_version": policy_version,
        "context": context.audit_context(),
        "selected_action": action,
        "eligible_actions": list(eligible),
        "reason_codes": reason_codes,
        "guardrails_triggered": guardrail_list,
        "requires_human_review": action == "route_to_specialist",
        "exploration_flag": exploration,
        "simulated_reward": reward,
        "not_credit_approval": True,
        "requires_formal_credit_analysis": True,
        "synthetic_counterfactual_outcome": True,
        "message": (
            "Avaliação offline de Próximo Passo Responsável para Cliente Sintético; "
            "não representa aprovação, contratação, taxa ou limite real de crédito."
        ),
    }


def _build_report(
    prepared: PreparedBankMarketing,
    seeds: Sequence[int],
    horizon: int,
    seed_runs: Sequence[SeedRun],
    experiment_ref: str,
) -> dict[str, Any]:
    metrics = [run.metrics for run in seed_runs]
    baseline = [item["baseline_reward"] for item in metrics]
    adaptive = [item["adaptive_reward"] for item in metrics]
    uplift = [item["uplift"] for item in metrics]
    regret = [item["adaptive_cumulative_regret"] for item in metrics]
    exploration = [item["exploration_rate"] for item in metrics]
    baseline_exposure = _mean_exposure(metrics, "baseline_exposure")
    adaptive_exposure = _mean_exposure(metrics, "adaptive_exposure")

    return {
        "experiment_ref": experiment_ref,
        "experiment_schema_version": EXPERIMENT_SCHEMA_VERSION,
        "seeds": list(seeds),
        "horizon_per_seed": horizon,
        "context_features": list(CONTEXT_FEATURES),
        "actions": list(ACTIONS),
        "baseline_strategy": "fixed educational content with safe eligible fallback",
        "adaptive_strategy": "contextual Thompson Sampling with Beta(1, 1) priors",
        "guardrail_order": "eligible actions are computed before policy selection",
        "reward_contract": {
            "type": "binary synthetic qualified-journey outcome",
            "observed_proxy_target_used_only_by_environment": "y",
            "not_click_optimized": True,
            "not_causal_evidence": True,
            "coefficient_reference": "docs/experiments/offline-bandit.md",
        },
        "dataset": {
            "source_dataset": prepared.metadata["source_dataset"],
            "source_version": prepared.metadata["source_version"],
            "source_sha256": prepared.metadata["source_sha256"],
            "row_count": prepared.metadata["row_count"],
            "feature_columns": prepared.metadata["feature_columns"],
            "excluded_columns": prepared.metadata["excluded_columns"],
        },
        "metrics": {
            "baseline_reward_mean": statistics.fmean(baseline),
            "adaptive_reward_mean": statistics.fmean(adaptive),
            "uplift_mean": statistics.fmean(uplift),
            "uplift_stddev": _population_stddev(uplift),
            "baseline_cumulative_reward_mean": statistics.fmean(baseline),
            "adaptive_cumulative_reward_mean": statistics.fmean(adaptive),
            "adaptive_cumulative_regret_mean": statistics.fmean(regret),
            "exploration_rate_mean": statistics.fmean(exploration),
            "baseline_exposure": baseline_exposure,
            "adaptive_exposure": adaptive_exposure,
        },
        "runs": metrics,
        "limitations": [
            "Bank Marketing has no randomized multi-arm counterfactual outcomes.",
            "Rewards and secured-loan contexts are synthetic and reproducible, not causal banking evidence.",
            "This experiment does not approve, price, contract, or recommend real credit.",
        ],
    }


def _build_policy_artifact(
    seed_run: SeedRun, seed: int, experiment_ref: str
) -> dict[str, Any]:
    posteriors = {
        context: {
            action: {"alpha": posterior.alpha, "beta": posterior.beta}
            for action, posterior in sorted(actions.items())
        }
        for context, actions in sorted(seed_run.posteriors.items())
    }
    return {
        "schema_version": POLICY_ARTIFACT_SCHEMA_VERSION,
        "policy_version": ADAPTIVE_POLICY_VERSION,
        "experiment_ref": experiment_ref,
        "training_seed": seed,
        "actions": list(ACTIONS),
        "context_features": list(CONTEXT_FEATURES),
        "context_key_separator": "|",
        "priors": {"alpha": PRIOR_ALPHA, "beta": PRIOR_BETA},
        "posteriors": posteriors,
        "guardrails_required_before_selection": True,
        "not_credit_approval": True,
    }


def _mean_exposure(metrics: Sequence[dict[str, Any]], field: str) -> dict[str, float]:
    return {
        action: statistics.fmean(item[field][action] for item in metrics)
        for action in ACTIONS
    }


def _population_stddev(values: Sequence[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _experiment_ref(
    prepared: PreparedBankMarketing, seeds: Sequence[int], horizon: int
) -> str:
    payload = json.dumps(
        {
            "schema": EXPERIMENT_SCHEMA_VERSION,
            "source_sha256": prepared.metadata["source_sha256"],
            "seeds": list(seeds),
            "horizon": horizon,
            "actions": ACTIONS,
        },
        sort_keys=True,
    )
    return "exp_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
