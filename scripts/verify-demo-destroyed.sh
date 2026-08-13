#!/usr/bin/env bash
# Read-only verification of concrete temporary-demo residues and required
# persistent bootstrap survivors. With no flag it also requires no active demo
# state or lock. --allow-active-demo-state is only the pre-pointer-delete check.
set -euo pipefail
usage() { echo 'Usage: verify-demo-destroyed.sh [--allow-active-demo-state]' >&2; exit 2; }
[[ $# -le 1 ]] || usage
allow_active_state=false
[[ $# -eq 0 || "$1" == --allow-active-demo-state ]] || usage
[[ $# -eq 0 ]] || allow_active_state=true
region="${AWS_REGION:-us-east-1}"
expected_account="969212888717"
state_bucket="${STATE_BUCKET:-tc4-mlops-tfstate-969212888717-bootstrap25}"
state_key="demo/terraform.tfstate"
bootstrap_key="bootstrap/terraform.tfstate"
[[ "$region" == "us-east-1" ]] || { echo "Unexpected AWS region: $region" >&2; exit 2; }
account="$(aws sts get-caller-identity --query Account --output text)"
[[ "$account" == "$expected_account" ]] || { echo "Unexpected AWS account: $account" >&2; exit 2; }
prefix="tc4-mlops-demo-${account}"
residues=()
present() { local label="$1"; shift; "$@" >/dev/null 2>&1 && residues+=("$label") || true; }

present s3-presentation aws s3api head-bucket --bucket "${prefix}-presentation"
present s3-audit aws s3api head-bucket --bucket "${prefix}-audit"
present ecr aws ecr describe-repositories --repository-names "${prefix}-api"
present lambda aws lambda get-function --function-name "${prefix}-api"
present lambda-runtime-role aws iam get-role --role-name "${prefix}-lambda"
[[ "$(aws apigatewayv2 get-apis --query "length(Items[?Name=='${prefix}-http'] || \`[]\`)" --output text)" == 0 ]] || residues+=("api-gateway")
[[ "$(aws cloudfront list-distributions --query "length(DistributionList.Items[?Comment=='Temporary tc4-mlops synthetic demo'] || \`[]\`)" --output text)" == 0 ]] || residues+=("cloudfront")
[[ "$(aws cloudfront list-origin-access-controls --query "length(OriginAccessControlList.Items[?Name=='${prefix}-presentation-oac'] || \`[]\`)" --output text)" == 0 ]] || residues+=("cloudfront-oac")
[[ "$(aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/${prefix}-api" --query 'length(logGroups)' --output text)" == 0 ]] || residues+=("cloudwatch-log-group")
present cloudwatch-dashboard aws cloudwatch get-dashboard --dashboard-name "${prefix}-dashboard"
# shellcheck disable=SC2016 # Backticks are JMESPath literal syntax, not shell expansion.
metric_alarm_count="$(aws cloudwatch describe-alarms --alarm-name-prefix "$prefix" --query 'length(MetricAlarms || `[]`)' --output text)"
# shellcheck disable=SC2016 # Backticks are JMESPath literal syntax, not shell expansion.
composite_alarm_count="$(aws cloudwatch describe-alarms --alarm-name-prefix "$prefix" --query 'length(CompositeAlarms || `[]`)' --output text)"
alarm_count=$((metric_alarm_count + composite_alarm_count))
[[ "$alarm_count" == 0 ]] || residues+=("cloudwatch-alarm")
if ! "$allow_active_state"; then
  present demo-state aws s3api head-object --bucket "$state_bucket" --key "$state_key"
  present demo-lock aws s3api head-object --bucket "$state_bucket" --key "${state_key}.tflock"
fi

# These are explicit survivors. Failure is not downgraded to a residue because
# an apparently clean destroy without its recovery foundation is unsafe. The
# bootstrap state HeadObject proves the state bucket and recovery state exist;
# do not add a broader bucket-level probe just to duplicate that proof.
for survivor in \
  "s3api head-object --bucket $state_bucket --key $bootstrap_key" \
  "iam get-role --role-name tc4-mlops-github-plan" \
  "iam get-role --role-name tc4-mlops-github-deploy" \
  "iam get-policy --policy-arn arn:aws:iam::${account}:policy/tc4-mlops-github-automation-boundary"; do
  # shellcheck disable=SC2086 # Each trusted literal above intentionally forms AWS argv.
  aws $survivor >/dev/null || { echo "Required bootstrap survivor missing: $survivor" >&2; exit 1; }
done
aws iam list-open-id-connect-providers --query "length(OpenIDConnectProviderList[?Arn=='arn:aws:iam::${account}:oidc-provider/token.actions.githubusercontent.com'])" --output text | grep -qx 1 || { echo "Bootstrap GitHub OIDC provider missing." >&2; exit 1; }
aws budgets describe-budget --account-id "$account" --budget-name tc4-mlops-demo-monthly-usd30 --region "$region" >/dev/null || { echo "Persistent demo budget missing." >&2; exit 1; }

python - "${residues[@]}" <<'PY'
import json, sys
print(json.dumps({"residual_resources": sys.argv[1:]}, indent=2))
PY
((${#residues[@]} == 0))
