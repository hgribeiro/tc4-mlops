"""Reproducible preparation of the public Bank Marketing proxy dataset."""

from __future__ import annotations

import csv
import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_DATASET = "bank_marketing_public_proxy"
SOURCE_VERSION = "UCI dataset 222 / bank-full.csv"
SCHEMA_VERSION = "bank_marketing_prepared_v0.1"

_REQUIRED_COLUMNS = {"contact", "campaign", "pdays", "previous", "poutcome", "y"}
_EXCLUDED_FROM_FEATURES = {
    "age",
    "job",
    "marital",
    "education",
    "default",
    "balance",
    "housing",
    "loan",
    "day",
    "month",
    "duration",
}
_FEATURE_COLUMNS = (
    "contact_channel_proxy",
    "contact_repetition_count",
    "days_since_previous_contact",
    "previous_contact_count",
    "previous_outcome",
)


@dataclass(frozen=True)
class PreparedBankMarketing:
    """Features, binary target, and lineage returned by the public preparation seam."""

    features: tuple[dict[str, Any], ...]
    target: tuple[int, ...]
    metadata: dict[str, Any]


def _integer(row: dict[str, str], column: str, row_number: int) -> int:
    try:
        return int(row[column])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            f"row {row_number}: column '{column}' must contain an integer"
        ) from error


def _target(value: str, row_number: int) -> int:
    normalized = value.strip().lower()
    if normalized not in {"yes", "no"}:
        raise ValueError(
            f"row {row_number}: target 'y' must be 'yes' or 'no', received {value!r}"
        )
    return int(normalized == "yes")


def prepare_bank_marketing(
    csv_path: str | Path, *, seed: int
) -> PreparedBankMarketing:
    """Prepare minimized pre-interaction features from ``bank-full.csv``.

    The seed deterministically defines row order for offline experiments. The
    post-contact field ``duration`` and the documented prohibited proxy fields
    are never copied into prepared features.
    """

    source_path = Path(csv_path)
    source_bytes = source_path.read_bytes()

    with source_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=";")
        fieldnames = set(reader.fieldnames or ())
        missing = sorted(_REQUIRED_COLUMNS - fieldnames)
        if missing:
            raise ValueError(
                "Bank Marketing CSV is missing required columns: " + ", ".join(missing)
            )

        prepared_rows: list[tuple[dict[str, Any], int]] = []
        for row_number, row in enumerate(reader, start=2):
            pdays = _integer(row, "pdays", row_number)
            features = {
                "contact_channel_proxy": row["contact"].strip().lower(),
                "contact_repetition_count": min(
                    max(_integer(row, "campaign", row_number), 0), 10
                ),
                "days_since_previous_contact": None if pdays < 0 else pdays,
                "previous_contact_count": max(
                    _integer(row, "previous", row_number), 0
                ),
                "previous_outcome": row["poutcome"].strip().lower(),
            }
            prepared_rows.append((features, _target(row["y"], row_number)))

    random.Random(seed).shuffle(prepared_rows)
    features = tuple(row[0] for row in prepared_rows)
    target = tuple(row[1] for row in prepared_rows)
    metadata = {
        "source_dataset": SOURCE_DATASET,
        "source_version": SOURCE_VERSION,
        "source_file": source_path.name,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "schema_version": SCHEMA_VERSION,
        "random_seed": seed,
        "row_count": len(features),
        "feature_columns": list(_FEATURE_COLUMNS),
        "target_name": "y",
        "target_mean": sum(target) / len(target) if target else None,
        "excluded_columns": sorted(_EXCLUDED_FROM_FEATURES & fieldnames),
        "temporal_leakage_columns": ["duration"] if "duration" in fieldnames else [],
    }
    return PreparedBankMarketing(features=features, target=target, metadata=metadata)
