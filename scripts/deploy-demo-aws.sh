#!/usr/bin/env bash
# Creates and verifies the temporary AWS demo. It intentionally leaves demo
# resources deployed for the follow-up teardown workflow; it never touches the
# persistent bootstrap state or destroys it.
set -euo pipefail

: "${AWS_PROFILE:=coding-agent}"
export AWS_PROFILE
if [[ "$AWS_PROFILE" != "coding-agent" ]]; then
  echo "Use AWS_PROFILE=coding-agent for this authorized bootstrap/deploy." >&2
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
region="${AWS_REGION:-us-east-1}"
commit_sha="${COMMIT_SHA:-$(git rev-parse HEAD)}"
state_bucket="${STATE_BUCKET:-tc4-mlops-tfstate-969212888717-bootstrap25}"
state_key="demo/terraform.tfstate"
demo_dir="infrastructure/environments/demo"
backend_file="${demo_dir}/backend.hcl"

account="$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)"
[[ "$account" == "969212888717" ]] || { echo "Unexpected AWS account: $account" >&2; exit 2; }
[[ "$commit_sha" =~ ^[0-9a-f]{7,64}$ ]] || { echo "COMMIT_SHA must be a Git SHA" >&2; exit 2; }

cat > "$backend_file" <<EOF
bucket = "$state_bucket"
key = "$state_key"
region = "$region"
encrypt = true
use_lockfile = true
EOF
trap 'rm -f "$backend_file"' EXIT

terraform -chdir="$demo_dir" init -reconfigure -backend-config=backend.hcl
terraform -chdir="$demo_dir" apply -auto-approve -var="aws_region=$region" -var="commit_sha=$commit_sha"
expires_at="$(terraform -chdir="$demo_dir" output -raw expires_at)"
ecr_url="$(terraform -chdir="$demo_dir" output -raw ecr_repository_url)"
cloudfront_url="$(terraform -chdir="$demo_dir" output -raw cloudfront_url)"
distribution_id="$(terraform -chdir="$demo_dir" output -raw cloudfront_distribution_id)"

aws ecr get-login-password --region "$region" --profile "$AWS_PROFILE" | docker login --username AWS --password-stdin "${ecr_url%%/*}"
docker build --platform linux/amd64 -f Dockerfile.lambda -t "$ecr_url:$commit_sha" .
docker push "$ecr_url:$commit_sha"

terraform -chdir="$demo_dir" apply -auto-approve \
  -var="aws_region=$region" -var="commit_sha=$commit_sha" -var="expires_at=$expires_at" \
  -var="image_uri=$ecr_url:$commit_sha"
api_url="$(terraform -chdir="$demo_dir" output -raw api_url)"
audit_bucket="$(terraform -chdir="$demo_dir" output -raw audit_bucket_name)"
log_group="/aws/lambda/tc4-mlops-demo-${account}-api"

(
  cd presentation
  npm ci
  DEMO_API_URL="$api_url" npm run build
)
aws s3 sync presentation/dist "s3://$(terraform -chdir="$demo_dir" output -raw presentation_bucket_name)/" \
  --delete --only-show-errors --profile "$AWS_PROFILE" --region "$region"
invalidation_id="$(aws cloudfront create-invalidation --distribution-id "$distribution_id" --paths '/*' --profile "$AWS_PROFILE" --query 'Invalidation.Id' --output text)"
aws cloudfront wait invalidation-completed --distribution-id "$distribution_id" --id "$invalidation_id" --profile "$AWS_PROFILE"

curl --fail --silent --show-error --retry 12 --retry-delay 5 "$cloudfront_url" >/dev/null
curl --fail --silent --show-error --retry 12 --retry-delay 5 "$api_url/health" >/dev/null
origin="${cloudfront_url%/}"
cors_headers="$(curl --fail --silent --show-error -X OPTIONS "$api_url/v1/decisions" -H "Origin: $origin" -H 'Access-Control-Request-Method: POST' -D - -o /dev/null)"
grep -qi "access-control-allow-origin: $origin" <<<"$cors_headers"

for policy in baseline adaptive; do
  for scenario in vehicle_simple home_complex guardrail_sensitive; do
    response="$(curl --fail --silent --show-error -X POST "$api_url/v1/decisions" -H 'content-type: application/json' -H "Origin: $origin" --data "{\"scenario_id\":\"$scenario\",\"policy_mode\":\"$policy\"}")"
    python -c 'import json,sys; d=json.load(sys.stdin); assert d["decision_id"].startswith("dec_"); assert d["audit_log_ref"].startswith("s3://"); assert d["not_credit_approval"] is True' <<<"$response"
  done
done

object_count="$(aws s3api list-objects-v2 --bucket "$audit_bucket" --prefix decisions/ --profile "$AWS_PROFILE" --query 'KeyCount' --output text)"
[[ "$object_count" -ge 6 ]] || { echo "Expected at least six audit objects; found $object_count" >&2; exit 1; }
# The API accepts only IDs, but this independently checks that scenario payloads
# did not leak into the Lambda log stream.
for forbidden in vehicle_simple home_complex guardrail_sensitive; do
  [[ "$(aws logs filter-log-events --log-group-name "$log_group" --filter-pattern "$forbidden" --profile "$AWS_PROFILE" --query 'length(events)' --output text)" == "0" ]] || { echo "Found forbidden payload marker in logs: $forbidden" >&2; exit 1; }
done

printf '\nCloudFront: %s\nAPI: %s\nECR: %s:%s\nAudit: s3://%s/decisions/\nState: s3://%s/%s\nExpiresAt: %s\n' \
  "$cloudfront_url" "$api_url" "$ecr_url" "$commit_sha" "$audit_bucket" "$state_bucket" "$state_key" "$expires_at"
