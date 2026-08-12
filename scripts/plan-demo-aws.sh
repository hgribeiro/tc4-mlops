#!/usr/bin/env bash
# Produces a non-mutating plan for the temporary demo using the same backend,
# account, region and immutable-image contract as deploy-demo-aws.sh.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
region="${AWS_REGION:-us-east-1}"
commit_sha="${COMMIT_SHA:-$(git rev-parse HEAD)}"
low_quota_mode="${LOW_QUOTA_MODE:-true}"
state_bucket="${STATE_BUCKET:-tc4-mlops-tfstate-969212888717-bootstrap25}"
state_key="demo/terraform.tfstate"
demo_dir="infrastructure/environments/demo"
backend_file="${demo_dir}/backend.hcl"
plan_file="${PLAN_FILE:-${RUNNER_TEMP:-/tmp}/tc4-mlops-demo.tfplan}"

account="$(aws sts get-caller-identity --query Account --output text)"
[[ "$account" == "969212888717" ]] || { echo "Unexpected AWS account: $account" >&2; exit 2; }
[[ "$commit_sha" =~ ^[0-9a-f]{7,64}$ ]] || { echo "COMMIT_SHA must be a Git SHA" >&2; exit 2; }
[[ "$low_quota_mode" == "true" || "$low_quota_mode" == "false" ]] || { echo "LOW_QUOTA_MODE must be true or false" >&2; exit 2; }

cat > "$backend_file" <<EOF
bucket = "$state_bucket"
key = "$state_key"
region = "$region"
encrypt = true
use_lockfile = true
EOF
trap 'rm -f "$backend_file"' EXIT

# Refresh is intentionally disabled: the plan role is read-only apart from the
# S3 lockfile and must never need broad access to live demo resources.
terraform -chdir="$demo_dir" init -reconfigure -backend-config=backend.hcl
set +e
terraform -chdir="$demo_dir" plan -refresh=false -lock-timeout=5m -detailed-exitcode \
  -out="$plan_file" -var="aws_region=$region" -var="commit_sha=$commit_sha" \
  -var="low_quota_mode=$low_quota_mode" \
  -var="image_uri=969212888717.dkr.ecr.${region}.amazonaws.com/tc4-mlops-demo-969212888717-api:$commit_sha"
plan_status=$?
set -e
if [[ "$plan_status" -eq 0 || "$plan_status" -eq 2 ]]; then
  echo "Non-mutating Terraform plan completed (exit $plan_status)."
  exit 0
fi
exit "$plan_status"
