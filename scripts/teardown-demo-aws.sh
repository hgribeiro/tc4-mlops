#!/usr/bin/env bash
# Guarded teardown for ONLY the temporary demo. It is deliberately resilient to
# partial state: no destructive target is read from Terraform outputs.
set -euo pipefail
usage() { echo 'Usage: teardown-demo-aws.sh (--confirm-destroy|--expired-only) [--plan-only]; --confirm-destroy requires DESTROY_APPROVED=DESTROY_DEMO' >&2; exit 2; }
(($# >= 1 && $# <= 2)) || usage
mode="$1"; plan_only="${2:-}"
[[ "$mode" == --confirm-destroy || "$mode" == --expired-only ]] || usage
[[ -z "$plan_only" || "$plan_only" == --plan-only ]] || usage
[[ "$mode" != --confirm-destroy || "${DESTROY_APPROVED:-}" == DESTROY_DEMO ]] || { echo 'Set DESTROY_APPROVED=DESTROY_DEMO after review.' >&2; exit 2; }
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$root"
region="${AWS_REGION:-us-east-1}"; expected_account="969212888717"
state_bucket="${STATE_BUCKET:-tc4-mlops-tfstate-969212888717-bootstrap25}"
state_key="demo/terraform.tfstate"; bootstrap_state_key="bootstrap/terraform.tfstate"
demo_dir="infrastructure/environments/demo"; backend_file="$demo_dir/backend.hcl"
evidence_dir="${EVIDENCE_DIR:-$root/artifacts/teardown-evidence-$(date -u +%Y%m%dT%H%M%SZ)}"
[[ -n "${CI:-}" || -n "${AWS_PROFILE:-}" ]] || { echo 'Refusing implicit default AWS profile; set AWS_PROFILE.' >&2; exit 2; }
[[ "$region" == us-east-1 ]] || { echo "Unexpected AWS region: $region" >&2; exit 2; }
account="$(aws sts get-caller-identity --query Account --output text)"; [[ "$account" == "$expected_account" ]] || { echo "Unexpected AWS account: $account" >&2; exit 2; }
audit_bucket="tc4-mlops-demo-${account}-audit"
mkdir -p "$evidence_dir"; evidence_dir="$(cd "$evidence_dir" && pwd)"
state_file="$(mktemp)"; plan_file="$(mktemp)"
trap 'rm -f "$backend_file" "$state_file" "$plan_file" "${plan_file}.json"' EXIT

state_present=false
state_has_managed_resources=false
if aws s3api head-object --bucket "$state_bucket" --key "$state_key" >/dev/null 2>&1; then
  state_present=true
  cat > "$backend_file" <<EOF
bucket = "$state_bucket"
key = "$state_key"
region = "$region"
encrypt = true
use_lockfile = true
EOF
  terraform -chdir="$demo_dir" init -reconfigure -backend-config=backend.hcl >/dev/null
  terraform -chdir="$demo_dir" state list > "$evidence_dir/state-resource-addresses.txt"
  grep -q '^aws_' "$evidence_dir/state-resource-addresses.txt" && state_has_managed_resources=true || true
  terraform -chdir="$demo_dir" state pull > "$state_file"
  # State may be partial, but it must never contain bootstrap addresses or an
  # unrecognised managed resource before this script is allowed to destroy it.
  python - "$state_file" "$audit_bucket" <<'PY'
import json, re, sys
state, expected_bucket = json.load(open(sys.argv[1])), sys.argv[2]
allowed = {
 "aws_s3_bucket.presentation", "aws_s3_bucket.audit", "aws_s3_bucket_ownership_controls.presentation", "aws_s3_bucket_ownership_controls.audit",
 "aws_s3_bucket_public_access_block.presentation", "aws_s3_bucket_public_access_block.audit", "aws_s3_bucket_server_side_encryption_configuration.presentation", "aws_s3_bucket_server_side_encryption_configuration.audit",
 "aws_s3_bucket_policy.presentation", "aws_s3_bucket_policy.audit", "aws_cloudfront_origin_access_control.presentation", "aws_cloudfront_distribution.presentation",
 "aws_ecr_repository.api", "aws_ecr_repository_policy.lambda_pull", "aws_ecr_lifecycle_policy.api", "aws_cloudwatch_log_group.api", "aws_iam_role.lambda", "aws_iam_role_policy.lambda_runtime",
 "aws_lambda_function.api", "aws_apigatewayv2_api.http", "aws_apigatewayv2_integration.api", "aws_apigatewayv2_route.decisions", "aws_apigatewayv2_route.health",
 "aws_apigatewayv2_route.ready", "aws_apigatewayv2_stage.default", "aws_lambda_permission.api_gateway", "aws_cloudwatch_log_metric_filter.decisions",
 "aws_cloudwatch_log_metric_filter.audit_failures", "aws_cloudwatch_metric_alarm.lambda_errors", "aws_cloudwatch_metric_alarm.audit_failures", "aws_cloudwatch_dashboard.demo",
}
found_audit = False
for resource in state.get("resources", []):
    address = resource["type"] + "." + resource["name"]
    if resource.get("mode") == "data":
        if address != "aws_caller_identity.current": raise SystemExit("Unexpected data source in demo state: " + address)
        continue
    if address not in allowed: raise SystemExit("Unexpected managed resource in demo state: " + address)
    if address == "aws_s3_bucket.audit":
        found_audit = True
        for instance in resource.get("instances", []):
            if instance.get("attributes", {}).get("bucket") != expected_bucket:
                raise SystemExit("Demo state audit bucket is not the account-bound canonical bucket.")
print("tracked-audit=" + str(found_audit).lower())
PY
fi

bucket_present=false
if aws s3api head-bucket --bucket "$audit_bucket" >/dev/null 2>&1; then
  bucket_present=true
  # Canonical name alone is not sufficient: tags bind an orphan recovery to the
  # intended temporary demo before it can be exported, emptied, or deleted.
  tags="$(aws s3api get-bucket-tagging --bucket "$audit_bucket" --output json)"
  expires_at="$(python - "$tags" <<'PY'
import json, sys
values={x['Key']: x['Value'] for x in json.loads(sys.argv[1]).get('TagSet', [])}
required={'Project':'tc4-mlops','Environment':'demo','ManagedBy':'terraform','DataClass':'synthetic-audit'}
if any(values.get(k) != v for k,v in required.items()): raise SystemExit('Audit bucket tags do not identify the temporary demo.')
commit=values.get('Commit',''); expiry=values.get('ExpiresAt','')
if len(commit) < 7 or any(c not in '0123456789abcdef' for c in commit) or not expiry: raise SystemExit('Audit bucket lacks a valid Commit or ExpiresAt tag.')
print(expiry)
PY
)"
  if "$state_present"; then
    python - "$state_file" "$expires_at" <<'PY'
import json, sys
for resource in json.load(open(sys.argv[1])).get('resources', []):
    if resource.get('type') == 'aws_s3_bucket' and resource.get('name') == 'audit':
        for instance in resource.get('instances', []):
            if instance.get('attributes', {}).get('tags', {}).get('ExpiresAt') != sys.argv[2]:
                raise SystemExit('State/live audit ExpiresAt mismatch; refusing destroy.')
PY
  fi
elif "$state_present"; then
  # A partial destroy can remove the bucket before the state/output. The state
  # remains recoverable and Terraform may clean it, but scheduling cannot infer
  # expiry without a live guarded resource.
  expires_at=""
else
  [[ "$mode" == --expired-only ]] && { echo 'No active demo state or audit bucket; scheduled failsafe no-op.'; exit 0; }
  echo 'No active demo state or canonical audit bucket; refusing claimed teardown.' >&2; exit 1
fi

if [[ "$mode" == --expired-only ]]; then
  [[ -n "${expires_at:-}" ]] || { echo 'Cannot determine ExpiresAt from state-aware audit resource; refusing scheduled destroy.' >&2; exit 1; }
  expires_epoch="$(date -u -d "$expires_at" +%s)" || { echo 'Invalid ExpiresAt.' >&2; exit 1; }
  [[ "$(date -u +%s)" -ge "$expires_epoch" ]] || { echo "Demo not expired: $expires_at"; exit 0; }
fi

# Export and independently verify before the audit bucket can be emptied.
EVIDENCE_DIR="$evidence_dir" AUDIT_BUCKET="$audit_bucket" scripts/export-demo-evidence.sh
cp "$evidence_dir/manifest.json" "$evidence_dir/manifest-before-destroy.json"
python - "$evidence_dir" "$evidence_dir/manifest-before-destroy.json" <<'PY'
import hashlib, json, pathlib, sys
root, manifest = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for item in json.loads(manifest.read_text())["files"]:
    data=(root/item["path"]).read_bytes()
    if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
        raise SystemExit("Evidence manifest verification failed: " + item["path"])
PY

empty_audit_bucket() {
  local inventory request
  while :; do
    inventory="$(aws s3api list-object-versions --bucket "$audit_bucket" --output json)"
    request="$(python - "$inventory" <<'PY'
import json, sys
payload=json.loads(sys.argv[1]); objects=[]
for section in ('Versions', 'DeleteMarkers'):
    for item in payload.get(section, []): objects.append({'Key':item['Key'], 'VersionId':item['VersionId']})
print(json.dumps({'Objects':objects, 'Quiet':True}))
PY
)"
    [[ "$request" != '{"Objects": [], "Quiet": true}' ]] || break
    aws s3api delete-objects --bucket "$audit_bucket" --delete "$request" >/dev/null
  done
  inventory="$(aws s3api list-object-versions --bucket "$audit_bucket" --output json)"
  python - "$inventory" <<'PY'
import json, sys
x=json.loads(sys.argv[1])
if x.get('Versions') or x.get('DeleteMarkers'): raise SystemExit('Audit bucket is not empty after deletion.')
PY
}
if "$state_present" && "$state_has_managed_resources"; then
  commit_sha="$(python - "$state_file" <<'PY'
import json, sys
values=[]
for resource in json.load(open(sys.argv[1])).get('resources', []):
 for instance in resource.get('instances', []):
  tag=instance.get('attributes', {}).get('tags', {}).get('Commit')
  if tag: values.append(tag)
print(sorted(set(values))[0] if values else '')
PY
)"
  [[ "$commit_sha" =~ ^[0-9a-f]{7,64}$ ]] || { echo 'State has no valid temporary-demo Commit tag.' >&2; exit 1; }
  terraform -chdir="$demo_dir" plan -destroy -lock-timeout=5m -out="$plan_file" -var="aws_region=$region" -var="commit_sha=$commit_sha" >/dev/null
  terraform -chdir="$demo_dir" show -json "$plan_file" > "${plan_file}.json"
  python - "${plan_file}.json" <<'PY'
import json, sys
changes=json.load(open(sys.argv[1])).get('resource_changes', [])
if any(change.get('change', {}).get('actions') != ['delete'] for change in changes): raise SystemExit('Destroy plan is not delete-only; refusing apply.')
if not any(change.get('change', {}).get('actions') == ['delete'] for change in changes): raise SystemExit('Destroy plan contains no deletes; refusing claimed teardown.')
PY
fi
[[ "$plan_only" != --plan-only ]] || { echo "Evidence and delete-only plan verified without changing AWS: $evidence_dir"; exit 0; }
if "$bucket_present"; then empty_audit_bucket; fi
if "$state_present" && "$state_has_managed_resources"; then terraform -chdir="$demo_dir" apply -auto-approve "$plan_file"; fi
# An audit bucket not tracked by state is a guarded orphan; delete it only after
# its verified export and after Terraform has removed any tracked resources.
if aws s3api head-bucket --bucket "$audit_bucket" >/dev/null 2>&1; then
  aws s3api delete-bucket --bucket "$audit_bucket"
fi

# Physical resources must be gone before the state pointer is removed. The S3
# bucket is versioned, so delete-marker recovery remains possible.
scripts/verify-demo-destroyed.sh --allow-active-demo-state > "$evidence_dir/post-destroy-physical-verification.json"
if "$state_present"; then
  aws s3api head-object --bucket "$state_bucket" --key "${state_key}.tflock" >/dev/null 2>&1 && { echo 'Demo lock remains after Terraform; refusing to delete state pointer.' >&2; exit 1; }
  aws s3api delete-object --bucket "$state_bucket" --key "$state_key" > "$evidence_dir/demo-state-delete-marker.json"
fi
scripts/verify-demo-destroyed.sh > "$evidence_dir/post-destroy-verified.json"
aws s3api head-object --bucket "$state_bucket" --key "$bootstrap_state_key" >/dev/null

# Re-seal the final bundle (including pre-destroy and post-destroy proof).
python - "$evidence_dir" <<'PY'
import hashlib, json, pathlib, sys
root=pathlib.Path(sys.argv[1]); manifest=root/'manifest.json'; files=[]
for path in sorted(p for p in root.rglob('*') if p.is_file() and p != manifest):
 data=path.read_bytes(); files.append({'path':str(path.relative_to(root)), 'sha256':hashlib.sha256(data).hexdigest(), 'bytes':len(data)})
manifest.write_text(json.dumps({'algorithm':'sha256','files':files},indent=2)+'\n')
for item in json.loads(manifest.read_text())['files']:
 data=(root/item['path']).read_bytes(); assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
PY
echo "Teardown completed; local hashed evidence: $evidence_dir"
