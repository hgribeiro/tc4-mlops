#!/usr/bin/env bash
# Start or remove the isolated LocalStack Community transport for issue #23.
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
terraform_dir="$root_dir/infrastructure/environments/localstack"
compose_file="$root_dir/infrastructure/localstack/docker-compose.yml"
build_dir="$root_dir/.build/localstack-lambda"
lambda_zip="$root_dir/.build/localstack-lambda.zip"
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_EC2_METADATA_DISABLED=true

compose() {
  docker compose -f "$compose_file" "$@"
}

terraform_init() {
  # The local backend does not create parent directories for its state file.
  # Cleanup removes this directory, so recreate it before every init.
  mkdir -p "$terraform_dir/state"
  terraform -chdir="$terraform_dir" init -reconfigure
}

require_command() {
  command -v "$1" >/dev/null || {
    echo "Required command not found: $1" >&2
    exit 1
  }
}

wait_for_localstack() {
  for _ in $(seq 1 60); do
    if curl --fail --silent http://localhost:4566/_localstack/health | grep -Eq '"lambda": "(available|running)"'; then
      return 0
    fi
    sleep 2
  done
  echo "LocalStack Lambda did not become available within 120 seconds." >&2
  return 1
}

package_lambda_zip() {
  rm -rf "$build_dir" "$lambda_zip"
  mkdir -p "$build_dir"
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    --volume "$root_dir:/workspace" \
    --workdir /workspace \
    python:3.12-slim \
    sh -ec 'python -m pip install --no-cache-dir --upgrade --target .build/localstack-lambda "boto3>=1.35,<2" "fastapi>=0.115,<1" "mangum>=0.19,<1" && python -m pip install --no-cache-dir --upgrade --no-deps --target .build/localstack-lambda . && cd .build/localstack-lambda && python -m zipfile -c ../localstack-lambda.zip .'
}

destroy() {
  local destroy_status=0
  local compose_status=0

  if [[ -f "$lambda_zip" ]]; then
    terraform -chdir="$terraform_dir" destroy -auto-approve -var="lambda_zip_path=$lambda_zip" || destroy_status=$?
  else
    terraform -chdir="$terraform_dir" destroy -auto-approve || destroy_status=$?
  fi
  compose down --volumes --remove-orphans || compose_status=$?

  # Keep Terraform state when destroy fails so the failure is recoverable and
  # never report a successful cleanup after leaving resources behind.
  if (( destroy_status == 0 && compose_status == 0 )); then
    rm -rf "$root_dir/.build" "$terraform_dir/state" "$terraform_dir/.terraform"
  fi
  if (( destroy_status != 0 )); then
    return "$destroy_status"
  fi
  return "$compose_status"
}

case "${1:-start}" in
  start)
    require_command docker
    require_command terraform
    require_command curl
    compose up -d
    wait_for_localstack

    package_lambda_zip
    # Rebuild ignored provider metadata so a prior interrupted local run cannot
    # make the local backend point at stale .terraform state.
    rm -rf "$terraform_dir/.terraform"
    terraform_init
    terraform -chdir="$terraform_dir" apply -auto-approve -var="lambda_zip_path=$lambda_zip"
    python "${root_dir}/scripts/smoke_localstack.py" \
      --api-url "$(terraform -chdir="$terraform_dir" output -no-color -raw api_endpoint)" \
      --bucket "$(terraform -chdir="$terraform_dir" output -no-color -raw audit_bucket_name)"
    ;;
  cleanup)
    require_command docker
    require_command terraform
    terraform_init
    destroy
    ;;
  *)
    echo "Usage: $0 [start|cleanup]" >&2
    exit 2
    ;;
esac
