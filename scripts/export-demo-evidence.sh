#!/usr/bin/env bash
# Export a minimized, hash-verifiable evidence bundle. This deliberately derives
# the account-bound audit bucket instead of reading Terraform outputs: outputs
# can be empty after a partial destroy.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
region="${AWS_REGION:-us-east-1}"
expected_account="969212888717"
account="$(aws sts get-caller-identity --query Account --output text)"
[[ "$account" == "$expected_account" ]] || { echo "Unexpected AWS account: $account" >&2; exit 2; }
[[ "$region" == "us-east-1" ]] || { echo "Unexpected AWS region: $region" >&2; exit 2; }
audit_bucket="${AUDIT_BUCKET:-tc4-mlops-demo-${account}-audit}"
expected_audit_bucket="tc4-mlops-demo-${account}-audit"
[[ "$audit_bucket" == "$expected_audit_bucket" ]] || { echo "Refusing a non-canonical audit bucket." >&2; exit 2; }
evidence_dir="${EVIDENCE_DIR:-$root/artifacts/teardown-evidence-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$evidence_dir/decisions" "$evidence_dir/operational"
evidence_dir="$(cd "$evidence_dir" && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

# A complete allowlist projection is the minimization boundary. Raw audit JSON
# and scenario contexts only ever exist in a temporary file outside the bundle.
: > "$evidence_dir/decisions/decisions.jsonl"
if aws s3api head-bucket --bucket "$audit_bucket" >/dev/null 2>&1; then
  aws s3api list-objects-v2 --bucket "$audit_bucket" --prefix decisions/ --output json > "$tmp_dir/audit-index.json"
  python - "$tmp_dir/audit-index.json" > "$evidence_dir/operational/audit-object-index.json" <<'PY'
import json, sys
source = json.load(open(sys.argv[1]))
print(json.dumps({"objects": [{k: item[k] for k in ("Key", "LastModified", "Size") if k in item}
                              for item in source.get("Contents", [])]}, indent=2, default=str))
PY
  while IFS= read -r key; do
    [[ -n "$key" ]] || continue
    aws s3api get-object --bucket "$audit_bucket" --key "$key" "$tmp_dir/audit-record.json" >/dev/null
    python - "$tmp_dir/audit-record.json" >> "$evidence_dir/decisions/decisions.jsonl" <<'PY'
import json, sys
record = json.load(open(sys.argv[1]))
forbidden = ("cpf", "email", "phone", "address", "income", "patrimony", "accesskey", "secret", "sessiontoken")
def names(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key.lower()
            yield from names(child)
    elif isinstance(value, list):
        for child in value:
            yield from names(child)
if any(word in name for name in names(record) for word in forbidden):
    raise SystemExit("Audit record contains a prohibited field name; refusing export.")
allowed = (
    "decision_id", "request_id", "selected_action", "eligible_actions", "policy_version",
    "reason_codes", "guardrails_triggered", "requires_human_review",
    "requires_formal_credit_analysis", "not_credit_approval", "not_credit_contracting",
    "not_simulated_qualified_proposal", "does_not_define_real_limit",
    "does_not_define_real_rate", "dropped_prohibited_fields_count", "logged_at",
)
if not isinstance(record.get("decision_id"), str) or not isinstance(record.get("request_id"), str):
    raise SystemExit("Audit record lacks required decision identifiers; refusing export.")
print(json.dumps({key: record.get(key) for key in allowed if key in record}, separators=(",", ":")))
PY
  done < <(python - "$tmp_dir/audit-index.json" <<'PY'
import json, sys
for item in json.load(open(sys.argv[1])).get("Contents", []):
    print(item.get("Key", ""))
PY
)
else
  printf '{"objects":[],"audit_bucket_status":"absent"}\n' > "$evidence_dir/operational/audit-object-index.json"
fi

policy_version="$(python -c 'import json; print(json.load(open("artifacts/official-experiment/policy.json"))["policy_version"])')"
python - "$evidence_dir/operational/versions.json" "$account" "$region" "$audit_bucket" "$policy_version" <<'PY'
import json, sys
json.dump({"account_id": sys.argv[2], "region": sys.argv[3], "audit_bucket": sys.argv[4],
           "policy_version": sys.argv[5],
           "minimization": "No Terraform state, credentials, CloudWatch logs, raw audit records, or scenario payloads are exported."}, open(sys.argv[1], "w"), indent=2)
PY
prefix="tc4-mlops-demo-${account}"
python - "$evidence_dir/operational/metric-queries.json" "$prefix" <<'PY'
import json, sys
prefix = sys.argv[2]
queries = [
 {"Id":"invocations","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Invocations","Dimensions":[{"Name":"FunctionName","Value":prefix+"-api"}]},"Period":60,"Stat":"Sum"},"ReturnData":True},
 {"Id":"errors","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Errors","Dimensions":[{"Name":"FunctionName","Value":prefix+"-api"}]},"Period":60,"Stat":"Sum"},"ReturnData":True},
 {"Id":"duration","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Duration","Dimensions":[{"Name":"FunctionName","Value":prefix+"-api"}]},"Period":60,"Stat":"Average"},"ReturnData":True},
 {"Id":"decisions","MetricStat":{"Metric":{"Namespace":"TC4MLOps/Demo","MetricName":"Decisions"},"Period":60,"Stat":"Sum"},"ReturnData":True},
 {"Id":"auditfailures","MetricStat":{"Metric":{"Namespace":"TC4MLOps/Demo","MetricName":"AuditFailures"},"Period":60,"Stat":"Sum"},"ReturnData":True},
]
json.dump(queries, open(sys.argv[1], "w"), separators=(",", ":"))
PY
start_time="$(date -u -d '-4 hours' +%Y-%m-%dT%H:%M:%SZ)"
end_time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
aws cloudwatch get-metric-data --metric-data-queries "file://$evidence_dir/operational/metric-queries.json" --start-time "$start_time" --end-time "$end_time" --scan-by TimestampAscending --output json > "$evidence_dir/operational/cloudwatch-metrics.json"

# Do not emit live API URLs, image URIs, Terraform outputs, or raw logs. This
# inventory records only canonical names and presence for recovery/audit.
python - "$evidence_dir/operational/resource-inventory.json" "$account" "$region" <<'PY'
import json, subprocess, sys
account, region = sys.argv[2:]
prefix = f"tc4-mlops-demo-{account}"
def exists(command):
    return subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
resources = {
 "audit_bucket": exists(["aws", "s3api", "head-bucket", "--bucket", prefix + "-audit"]),
 "presentation_bucket": exists(["aws", "s3api", "head-bucket", "--bucket", prefix + "-presentation"]),
 "ecr_repository": exists(["aws", "ecr", "describe-repositories", "--repository-names", prefix + "-api"]),
 "lambda": exists(["aws", "lambda", "get-function", "--function-name", prefix + "-api"]),
}
json.dump({"account_id": account, "region": region, "resources": resources}, open(sys.argv[1], "w"), indent=2)
PY

# The manifest is JSON so it can be verified independently without shell tools.
python - "$evidence_dir" <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1]); manifest = root / "manifest.json"
files = []
for path in sorted(p for p in root.rglob("*") if p.is_file() and p != manifest):
    data = path.read_bytes()
    files.append({"path": str(path.relative_to(root)), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
manifest.write_text(json.dumps({"algorithm":"sha256", "files":files}, indent=2) + "\n")
for item in json.loads(manifest.read_text())["files"]:
    data = (root / item["path"]).read_bytes()
    assert len(data) == item["bytes"] and hashlib.sha256(data).hexdigest() == item["sha256"]
PY
printf 'Minimized, hash-verified evidence exported to %s\n' "$evidence_dir"
