from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from .engine import decide
from .experiment import DEFAULT_MLFLOW_EXPERIMENT, run_offline_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="responsible-next-step",
        description=(
            "Decide um Próximo Passo Responsável para um Cliente Sintético. "
            "A saída não representa aprovação, contratação, taxa ou limite real de crédito."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    decide_parser = subparsers.add_parser(
        "decide",
        help="Recebe um Cliente Sintético em JSON e retorna uma decisão auditável.",
    )
    decide_parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Caminho para JSON de Cliente Sintético; use '-' para ler de stdin.",
    )
    decide_parser.add_argument(
        "--audit-log-dir",
        default="logs/decisions",
        help="Diretório onde o log auditável minimizado será gravado.",
    )
    decide_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Imprime JSON indentado para leitura humana.",
    )

    experiment_parser = subparsers.add_parser(
        "experiment",
        help="Compara baseline experimental e Thompson Sampling em ambiente sintético.",
    )
    experiment_parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Caminho para bank-full.csv ou fixture compatível.",
    )
    experiment_parser.add_argument(
        "--output-dir",
        default="artifacts/experiment",
        help="Diretório para relatório, política e log auditável da avaliação.",
    )
    experiment_parser.add_argument(
        "--seeds",
        default="11,29,47,71,97",
        help="Seeds inteiras separadas por vírgula; o relatório agrega todas.",
    )
    experiment_parser.add_argument(
        "--horizon",
        type=int,
        default=1000,
        help="Número de decisões avaliadas por seed.",
    )
    experiment_parser.add_argument(
        "--tracking-uri",
        default="sqlite:///mlflow.db",
        help="Tracking URI local do MLflow (padrão: sqlite:///mlflow.db).",
    )
    experiment_parser.add_argument(
        "--mlflow-experiment-name",
        default=DEFAULT_MLFLOW_EXPERIMENT,
        help="Nome do experimento no MLflow.",
    )
    experiment_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Imprime JSON indentado para leitura humana.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "decide":
        try:
            payload = _load_json(args.input)
            decision = decide(payload, Path(args.audit_log_dir))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"Erro ao processar decisão: {exc}", file=sys.stderr)
            return 2

        indent = 2 if args.pretty else None
        print(json.dumps(decision, ensure_ascii=False, indent=indent, sort_keys=True))
        return 0

    if args.command == "experiment":
        try:
            seeds = _parse_seeds(args.seeds)
            report = run_offline_experiment(
                args.input,
                args.output_dir,
                seeds=seeds,
                horizon=args.horizon,
                tracking_uri=args.tracking_uri,
                mlflow_experiment_name=args.mlflow_experiment_name,
            )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"Erro ao executar experimento: {exc}", file=sys.stderr)
            return 2

        indent = 2 if args.pretty else None
        print(json.dumps(report, ensure_ascii=False, indent=indent, sort_keys=True))
        return 0

    parser.error("comando inválido")
    return 2


def _parse_seeds(raw: str) -> list[int]:
    try:
        seeds = [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise ValueError("--seeds deve conter inteiros separados por vírgula") from exc
    if not seeds:
        raise ValueError("--seeds deve conter ao menos uma seed")
    return seeds


def _load_json(input_ref: str) -> Dict[str, Any]:
    if input_ref == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(input_ref).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("o JSON de entrada deve ser um objeto")
    return payload
