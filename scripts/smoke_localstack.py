#!/usr/bin/env python3
"""Exercise the emulated public HTTP contract and its minimized S3 evidence."""
from __future__ import annotations

import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import boto3


def post_decision(api_url: str) -> dict[str, object]:
    request = Request(
        f"{api_url.rstrip('/')}/v1/decisions",
        data=json.dumps(
            {"scenario_id": "vehicle_simple", "policy_mode": "baseline"}
        ).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    last_error: Exception | None = None
    for _ in range(24):
        try:
            with urlopen(request, timeout=10) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP inesperado: {response.status}")
                return json.loads(response.read())
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"API Gateway/Lambda não ficou pronto: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--localstack-endpoint", default="http://localhost:4566")
    args = parser.parse_args()

    decision = post_decision(args.api_url)
    required = {
        "decision_id",
        "request_id",
        "selected_action",
        "policy_version",
        "reason_codes",
        "requires_human_review",
        "guardrails_triggered",
        "audit_log_ref",
    }
    missing = required - decision.keys()
    if missing:
        raise RuntimeError(f"contrato HTTP sem campos obrigatórios: {sorted(missing)}")
    if decision["selected_action"] != "simulate_vehicle_secured_loan":
        raise RuntimeError("cenário vehicle_simple não preservou o Próximo Passo Responsável")
    if decision["not_credit_approval"] is not True:
        raise RuntimeError("contrato perdeu a limitação de não aprovação")

    audit_ref = str(decision["audit_log_ref"])
    expected_prefix = f"s3://{args.bucket}/"
    if not audit_ref.startswith(expected_prefix):
        raise RuntimeError(f"referência de auditoria inesperada: {audit_ref}")
    key = audit_ref.removeprefix(expected_prefix)
    s3 = boto3.client(
        "s3",
        endpoint_url=args.localstack_endpoint,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    object_body = s3.get_object(Bucket=args.bucket, Key=key)["Body"].read()
    audit_record = json.loads(object_body)
    if audit_record.get("decision_id") != decision["decision_id"]:
        raise RuntimeError("objeto S3 não corresponde à decisão HTTP")
    forbidden = {"email", "cpf", "name", "real_income"}
    if forbidden & set(audit_record.get("context_minimized", {})):
        raise RuntimeError("objeto S3 contém campo proibido")

    print(
        "LocalStack smoke passed: HTTP decision contract and minimized S3 audit object "
        f"({audit_ref})."
    )


if __name__ == "__main__":
    main()
