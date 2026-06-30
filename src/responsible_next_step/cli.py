from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from .engine import decide


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

    parser.error("comando inválido")
    return 2


def _load_json(input_ref: str) -> Dict[str, Any]:
    if input_ref == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(input_ref).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("o JSON de entrada deve ser um objeto")
    return payload
