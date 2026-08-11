"""Publication and offline validation of the official experiment evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .bank_marketing import SOURCE_URL
from .experiment import (
    ACTIONS,
    ADAPTIVE_POLICY_VERSION,
    BASELINE_POLICY_VERSION,
    EXPERIMENT_SCHEMA_VERSION,
    POLICY_ARTIFACT_SCHEMA_VERSION,
)

PROVENANCE_SCHEMA_VERSION = "official_experiment_provenance_v0.1"
EXPECTED_FULL_DATASET_ROWS = 45_211
APPROVED_FILENAMES = frozenset({"report.json", "policy.json", "provenance.json"})


def write_official_provenance_manifest(
    artifact_dir: str | Path,
    report: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    """Write deterministic provenance for report and policy derived artifacts."""

    destination = Path(artifact_dir)
    coverage = _coverage_review(report, policy)
    dataset = report["dataset"]
    manifest = {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "evidence_classification": {
            "synthetic": True,
            "offline": True,
            "causal": False,
            "real_credit_evidence": False,
        },
        "source": {
            "dataset": dataset["source_dataset"],
            "version": dataset["source_version"],
            "canonical_url": dataset.get("source_url", SOURCE_URL),
            "file_name": dataset["source_file"],
            "sha256": dataset["source_sha256"],
            "row_count": dataset["row_count"],
            "raw_data_versioned": False,
        },
        "preparation": {
            "schema_version": dataset["preparation_schema_version"],
            "feature_columns": dataset["feature_columns"],
            "excluded_columns": dataset["excluded_columns"],
            "temporal_leakage_columns": dataset["temporal_leakage_columns"],
            "temporal_leakage_excluded": (
                "duration" in dataset["temporal_leakage_columns"]
                and "duration" not in dataset["feature_columns"]
            ),
            "preparation_seed": report["seeds"][0],
        },
        "experiment": {
            "experiment_ref": report["experiment_ref"],
            "report_schema_version": report["experiment_schema_version"],
            "policy_schema_version": policy["schema_version"],
            "baseline_policy_version": BASELINE_POLICY_VERSION,
            "adaptive_policy_version": policy["policy_version"],
            "seeds": report["seeds"],
            "horizon_per_seed": report["horizon_per_seed"],
            "actions": report["actions"],
            "context_features": report["context_features"],
            "reward_contract": report["reward_contract"],
        },
        "coverage_review": coverage,
        "artifacts": {
            name: {
                "sha256": _sha256_file(destination / name),
                "media_type": "application/json",
            }
            for name in ("policy.json", "report.json")
        },
        "limitations": report["limitations"],
    }
    (destination / "provenance.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def validate_official_experiment_artifacts(
    artifact_dir: str | Path,
) -> dict[str, Any]:
    """Validate committed evidence without downloading or reading the raw dataset."""

    directory = Path(artifact_dir)
    if not directory.is_dir():
        raise ValueError(f"diretório de artefatos oficiais não encontrado: {directory}")
    filenames = {path.name for path in directory.iterdir()}
    if filenames != APPROVED_FILENAMES or not all(
        (directory / name).is_file() for name in APPROVED_FILENAMES
    ):
        unexpected = sorted(filenames - APPROVED_FILENAMES)
        missing = sorted(APPROVED_FILENAMES - filenames)
        raise ValueError(
            "o diretório oficial deve conter somente os artefatos derivados aprovados "
            f"{sorted(APPROVED_FILENAMES)}; inesperados={unexpected}, ausentes={missing}"
        )

    report = _load_object(directory / "report.json")
    policy = _load_object(directory / "policy.json")
    manifest = _load_object(directory / "provenance.json")

    _require(
        manifest.get("schema_version") == PROVENANCE_SCHEMA_VERSION,
        "schema de proveniência incompatível",
    )
    artifacts = manifest.get("artifacts")
    _require(isinstance(artifacts, dict), "manifesto sem hashes de artefatos")
    _require(
        set(artifacts) == {"policy.json", "report.json"},
        "manifesto deve hashear somente report.json e policy.json",
    )
    for name in ("policy.json", "report.json"):
        expected_hash = artifacts[name].get("sha256")
        actual_hash = _sha256_file(directory / name)
        _require(
            expected_hash == actual_hash,
            f"SHA-256 inválido para {name}: esperado {expected_hash}, obtido {actual_hash}",
        )

    _require(
        report.get("experiment_schema_version") == EXPERIMENT_SCHEMA_VERSION,
        "schema do relatório incompatível",
    )
    _require(
        policy.get("schema_version") == POLICY_ARTIFACT_SCHEMA_VERSION,
        "schema da política incompatível",
    )
    _require(
        policy.get("policy_version") == ADAPTIVE_POLICY_VERSION,
        "versão da Política Adaptativa incompatível",
    )
    _require(
        policy.get("experiment_ref") == report.get("experiment_ref"),
        "relatório e política têm experiment_ref diferentes",
    )
    _require(report.get("actions") == list(ACTIONS), "catálogo de Braços incompatível")
    _require(policy.get("actions") == report.get("actions"), "Braços da política divergem")
    _require(
        policy.get("context_features") == report.get("context_features"),
        "features de contexto da política divergem",
    )

    dataset = report.get("dataset", {})
    source = manifest.get("source", {})
    _require(
        dataset.get("row_count") == EXPECTED_FULL_DATASET_ROWS,
        "relatório não foi produzido com as 45.211 linhas da Bank Marketing completa",
    )
    _require(source.get("row_count") == dataset.get("row_count"), "linhagem de linhas diverge")
    _require(
        source.get("dataset") == dataset.get("source_dataset")
        and source.get("version") == dataset.get("source_version")
        and source.get("file_name") == dataset.get("source_file"),
        "identificação da fonte diverge entre relatório e manifesto",
    )
    _require(
        source.get("sha256") == dataset.get("source_sha256"),
        "hash da fonte diverge entre relatório e manifesto",
    )
    _require(source.get("canonical_url") == SOURCE_URL, "fonte pública canônica incompatível")
    _require(source.get("raw_data_versioned") is False, "dados brutos não podem ser versionados")

    preparation = manifest.get("preparation", {})
    feature_columns = dataset.get("feature_columns", [])
    _require("duration" not in feature_columns, "duration aparece nas features pré-interação")
    _require(
        "duration" in dataset.get("excluded_columns", []),
        "duration não está declarada entre as colunas excluídas",
    )
    _require(
        preparation.get("temporal_leakage_excluded") is True,
        "manifesto não confirma exclusão de vazamento temporal",
    )
    _require(
        preparation.get("schema_version")
        == dataset.get("preparation_schema_version"),
        "schema de preparação diverge entre relatório e manifesto",
    )
    _require(
        "duration" in preparation.get("temporal_leakage_columns", []),
        "manifesto não identifica duration como vazamento temporal",
    )

    seeds = report.get("seeds")
    _require(
        isinstance(seeds, list)
        and len(seeds) >= 5
        and len(seeds) == len(set(seeds))
        and all(isinstance(seed, int) for seed in seeds),
        "o experimento oficial requer ao menos cinco seeds inteiras distintas",
    )
    horizon = report.get("horizon_per_seed")
    _require(
        horizon == EXPECTED_FULL_DATASET_ROWS,
        "o horizonte oficial deve percorrer as 45.211 linhas em cada seed",
    )
    runs = report.get("runs")
    _require(
        isinstance(runs, list) and [run.get("seed") for run in runs] == seeds,
        "resultados por seed não correspondem às seeds declaradas",
    )
    experiment = manifest.get("experiment", {})
    _require(experiment.get("seeds") == seeds, "seeds divergem no manifesto")
    _require(experiment.get("horizon_per_seed") == horizon, "horizonte diverge no manifesto")

    classification = manifest.get("evidence_classification", {})
    _require(
        classification
        == {
            "synthetic": True,
            "offline": True,
            "causal": False,
            "real_credit_evidence": False,
        },
        "classificação sintética, offline e não causal está ausente",
    )
    reward_contract = report.get("reward_contract", {})
    _require(reward_contract.get("not_causal_evidence") is True, "limite não causal ausente")
    _require(
        any("synthetic" in str(item).lower() for item in report.get("limitations", [])),
        "limitação sintética ausente do relatório",
    )

    coverage = _coverage_review(report, policy)
    _require(
        manifest.get("coverage_review") == coverage,
        "revisão de cobertura não corresponde ao relatório e à política",
    )
    dimensions = {
        part
        for context in coverage["contexts_observed"]
        for part in context.split("|")
    }
    _require(
        {"vehicle", "home", "investment"}.issubset(dimensions),
        "cobertura não inclui os três tipos de garantia sintéticos",
    )
    _require(
        {"awareness", "documentation", "simulation"}.issubset(dimensions),
        "cobertura não inclui os três estágios sintéticos",
    )
    _require(
        coverage["eligible_actions_observed"] == list(ACTIONS),
        "nem todos os Braços apareceram em conjuntos elegíveis",
    )

    return {
        "status": "valid",
        "hashes_verified": True,
        "dataset_row_count": dataset["row_count"],
        "dataset_sha256": dataset["source_sha256"],
        "seed_count": len(seeds),
        "seeds": seeds,
        "horizon_per_seed": horizon,
        "context_count": coverage["context_count"],
        "actions_without_adaptive_exposure": coverage[
            "actions_without_adaptive_exposure"
        ],
        "synthetic_offline_non_causal": True,
        "validated_artifacts": ["policy.json", "report.json"],
    }


def _coverage_review(
    report: Mapping[str, Any], policy: Mapping[str, Any]
) -> dict[str, Any]:
    posteriors = policy.get("posteriors", {})
    contexts = sorted(posteriors)
    eligible_actions = sorted(
        {action for actions in posteriors.values() for action in actions},
        key=ACTIONS.index,
    )
    metrics = report["metrics"]
    adaptive_exposure = metrics["adaptive_exposure"]
    baseline_exposure = metrics["baseline_exposure"]
    missing_adaptive = [
        action for action in ACTIONS if float(adaptive_exposure.get(action, 0)) == 0
    ]
    structural_baseline_zeros = [
        action for action in ACTIONS if float(baseline_exposure.get(action, 0)) == 0
    ]
    low_adaptive_exposure = [
        action
        for action in ACTIONS
        if 0 < float(adaptive_exposure.get(action, 0)) < 5
    ]
    anomalies = [
        f"Braço sem exposição adaptativa: {action}" for action in missing_adaptive
    ] + [
        (
            "Baixa exposição adaptativa média (< 5 por seed): "
            f"{action}={float(adaptive_exposure[action])}"
        )
        for action in low_adaptive_exposure
    ]
    return {
        "status": "reviewed",
        "context_count": len(contexts),
        "contexts_observed": contexts,
        "eligible_actions_observed": eligible_actions,
        "adaptive_actions_exposed": [
            action for action in ACTIONS if float(adaptive_exposure.get(action, 0)) > 0
        ],
        "actions_without_adaptive_exposure": missing_adaptive,
        "actions_with_low_adaptive_exposure": low_adaptive_exposure,
        "expected_baseline_structural_zeros": structural_baseline_zeros,
        "anomalies": anomalies,
        "anomaly_review": (
            "anomalies_documented" if anomalies else "no_unexplained_anomalies"
        ),
        "notes": [
            "Zeros do baseline fora de conteúdo educativo e no_offer_now são esperados pela estratégia fixa.",
            "Baixa exposição de simulações reflete a raridade desses contextos públicos e a convergência da política; deve aparecer nos gráficos, não ser interpretada como eficácia real.",
            "Contextos e recompensas de Empréstimos com Garantia são sintéticos; cobertura não implica evidência causal.",
        ],
    }


def _load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"não foi possível ler {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} deve conter um objeto JSON")
    return payload


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)
