from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .experiment import (
    ACTIONS,
    CONTEXT_FEATURES,
    POLICY_ARTIFACT_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class AdaptivePolicy:
    policy_version: str
    training_seed: int
    context_features: tuple[str, ...]
    context_key_separator: str
    prior_alpha: float
    prior_beta: float
    posteriors: Mapping[str, Mapping[str, tuple[float, float]]]

    def select(self, context: Mapping[str, Any], eligible_actions: Sequence[str]) -> str:
        """Sample only from actions already admitted by responsible guardrails."""
        if not eligible_actions:
            raise ValueError("a política adaptativa requer ao menos um Braço elegível")
        unknown = set(eligible_actions).difference(ACTIONS)
        if unknown:
            raise ValueError(f"Braços elegíveis desconhecidos: {sorted(unknown)}")
        if len(eligible_actions) == 1:
            return eligible_actions[0]

        context_key = self.context_key_separator.join(
            str(context.get(feature, "")) for feature in self.context_features
        )
        context_posteriors = self.posteriors.get(context_key, {})
        seed_material = "|".join(
            [
                self.policy_version,
                str(self.training_seed),
                str(context.get("request_id", "")),
                context_key,
            ]
        )
        seed = int.from_bytes(
            hashlib.sha256(seed_material.encode("utf-8")).digest()[:8], "big"
        )
        rng = random.Random(seed)
        samples = {}
        for action in eligible_actions:
            alpha, beta = context_posteriors.get(
                action, (self.prior_alpha, self.prior_beta)
            )
            samples[action] = rng.betavariate(alpha, beta)
        return max(
            eligible_actions,
            key=lambda action: (samples[action], -ACTIONS.index(action)),
        )


def parse_adaptive_policy(payload: Mapping[str, Any]) -> AdaptivePolicy:
    if not isinstance(payload, Mapping):
        raise ValueError("o artefato adaptativo deve ser um objeto JSON")
    if payload.get("schema_version") != POLICY_ARTIFACT_SCHEMA_VERSION:
        raise ValueError(
            "schema_version incompatível no artefato adaptativo; esperado "
            f"{POLICY_ARTIFACT_SCHEMA_VERSION!r}"
        )

    policy_version = payload.get("policy_version")
    policy_version_prefix = "contextual_thompson_sampling_"
    if (
        not isinstance(policy_version, str)
        or not policy_version.startswith(policy_version_prefix)
        or len(policy_version) == len(policy_version_prefix)
    ):
        raise ValueError("policy_version adaptativa ausente ou incompatível")
    if payload.get("guardrails_required_before_selection") is not True:
        raise ValueError("o artefato deve exigir Guardrails antes da seleção")
    if payload.get("not_credit_approval") is not True:
        raise ValueError("o artefato deve declarar que não representa aprovação")

    actions = payload.get("actions")
    if not isinstance(actions, list) or tuple(actions) != ACTIONS:
        raise ValueError("catálogo de Braços incompatível no artefato adaptativo")
    context_features = payload.get("context_features")
    if not isinstance(context_features, list) or tuple(context_features) != CONTEXT_FEATURES:
        raise ValueError("definição de contexto incompatível no artefato adaptativo")
    separator = payload.get("context_key_separator")
    if not isinstance(separator, str) or not separator:
        raise ValueError("context_key_separator inválido no artefato adaptativo")

    priors = payload.get("priors")
    if not isinstance(priors, Mapping):
        raise ValueError("priors ausentes no artefato adaptativo")
    prior_alpha = _positive_number(priors.get("alpha"), "priors.alpha")
    prior_beta = _positive_number(priors.get("beta"), "priors.beta")

    training_seed = payload.get("training_seed")
    if isinstance(training_seed, bool) or not isinstance(training_seed, int):
        raise ValueError("training_seed inválida no artefato adaptativo")
    experiment_ref = payload.get("experiment_ref")
    if not isinstance(experiment_ref, str) or not experiment_ref:
        raise ValueError("experiment_ref ausente no artefato adaptativo")

    raw_posteriors = payload.get("posteriors")
    if not isinstance(raw_posteriors, Mapping):
        raise ValueError("posteriors ausentes no artefato adaptativo")
    posteriors: dict[str, dict[str, tuple[float, float]]] = {}
    for context_key, raw_actions in raw_posteriors.items():
        if not isinstance(context_key, str) or len(context_key.split(separator)) != len(
            CONTEXT_FEATURES
        ):
            raise ValueError("chave de contexto inválida no artefato adaptativo")
        if not isinstance(raw_actions, Mapping):
            raise ValueError("posteriores de contexto devem ser um objeto")
        parsed_actions: dict[str, tuple[float, float]] = {}
        for action, posterior in raw_actions.items():
            if action not in ACTIONS:
                raise ValueError(f"Braço desconhecido nos posteriors: {action!r}")
            if not isinstance(posterior, Mapping):
                raise ValueError(f"posterior inválido para o Braço {action!r}")
            parsed_actions[action] = (
                _positive_number(posterior.get("alpha"), f"{action}.alpha"),
                _positive_number(posterior.get("beta"), f"{action}.beta"),
            )
        posteriors[context_key] = parsed_actions

    return AdaptivePolicy(
        policy_version=policy_version,
        training_seed=training_seed,
        context_features=tuple(context_features),
        context_key_separator=separator,
        prior_alpha=prior_alpha,
        prior_beta=prior_beta,
        posteriors=posteriors,
    )


def _positive_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValueError(f"{field} deve ser um número positivo")
    return float(value)
