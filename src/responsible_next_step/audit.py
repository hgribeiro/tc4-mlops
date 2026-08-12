from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Protocol


class AuditPersistence(Protocol):
    """Persist a minimized decision record and return its audit reference."""

    def persist(self, record: Mapping[str, Any]) -> str:
        """Persist the record or propagate the persistence failure."""
        ...


class S3AuditPersistence:
    """Persist one minimized decision per private S3 object."""

    def __init__(
        self,
        bucket: str,
        prefix: str = "decisions",
        *,
        client: Any | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        if not bucket:
            raise ValueError("AUDIT_S3_BUCKET é obrigatório para auditoria S3")
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        if client is None:
            import boto3

            client = boto3.client("s3", endpoint_url=endpoint_url)
        self.client = client

    def persist(self, record: Mapping[str, Any]) -> str:
        context = record.get("context_minimized", {})
        event_timestamp = (
            context.get("event_timestamp") if isinstance(context, Mapping) else None
        )
        logged_at = str(record.get("logged_at", ""))
        timestamp = str(event_timestamp or logged_at)
        date_part = timestamp[:10] if len(timestamp) >= 10 else logged_at[:10]
        decision_id = str(record.get("decision_id", ""))
        if not decision_id:
            raise ValueError("registro de auditoria requer decision_id")

        key = "/".join(
            part for part in (self.prefix, date_part, f"{decision_id}.json") if part
        )
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(record, ensure_ascii=False, sort_keys=True),
            ContentType="application/json",
            ServerSideEncryption="AES256",
        )
        return f"s3://{self.bucket}/{key}"


class LocalAuditPersistence:
    """Append minimized decision records to date-partitioned local JSONL files."""

    def __init__(self, audit_log_dir: str | Path) -> None:
        self.audit_log_dir = Path(audit_log_dir)

    def persist(self, record: Mapping[str, Any]) -> str:
        context = record.get("context_minimized", {})
        event_timestamp = (
            context.get("event_timestamp") if isinstance(context, Mapping) else None
        )
        logged_at = str(record.get("logged_at", ""))
        timestamp = str(event_timestamp or logged_at)
        date_part = timestamp[:10] if len(timestamp) >= 10 else logged_at[:10]

        self.audit_log_dir.mkdir(parents=True, exist_ok=True)
        audit_path = self.audit_log_dir / f"{date_part}.jsonl"
        with audit_path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return str(audit_path)
