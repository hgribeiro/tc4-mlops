import os
import subprocess
from pathlib import Path


DEPLOY_SCRIPT = Path("scripts/deploy-demo-aws.sh").resolve()


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(0o755)


def test_partial_state_with_ecr_resumes_infrastructure_before_reading_cloudfront_outputs(
    tmp_path: Path,
):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    command_log = tmp_path / "commands.log"
    bootstrap_applied = tmp_path / "bootstrap-applied"

    _write_executable(
        fake_bin / "terraform",
        """#!/usr/bin/env bash
set -euo pipefail
printf 'terraform %s\n' "$*" >> "$COMMAND_LOG"
case "$*" in
  *" init "*) exit 0 ;;
  *" state list") echo 'aws_ecr_repository.api'; exit 0 ;;
  *" output -raw ecr_repository_url") echo '969212888717.dkr.ecr.us-east-1.amazonaws.com/tc4-mlops-demo-969212888717-api'; exit 0 ;;
  *" output -raw cloudfront_url")
    [[ -f "$BOOTSTRAP_APPLIED" ]] || { echo 'cloudfront output unavailable before bootstrap apply' >&2; exit 1; }
    echo 'https://example.cloudfront.net'; exit 0 ;;
  *" output -raw cloudfront_distribution_id") echo 'EDISTRIBUTION'; exit 0 ;;
  *" apply "*) touch "$BOOTSTRAP_APPLIED"; exit 0 ;;
  *) echo "unexpected terraform command: $*" >&2; exit 90 ;;
esac
""",
    )
    _write_executable(
        fake_bin / "aws",
        """#!/usr/bin/env bash
set -euo pipefail
printf 'aws %s\n' "$*" >> "$COMMAND_LOG"
case "$*" in
  "sts get-caller-identity --query Account --output text") echo '969212888717' ;;
  "ecr get-login-password --region us-east-1") echo 'token' ;;
  *) exit 91 ;;
esac
""",
    )
    _write_executable(
        fake_bin / "docker",
        """#!/usr/bin/env bash
printf 'docker %s\n' "$*" >> "$COMMAND_LOG"
exit 23
""",
    )

    env = os.environ | {
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "COMMAND_LOG": str(command_log),
        "BOOTSTRAP_APPLIED": str(bootstrap_applied),
        "COMMIT_SHA": "74f475990bc9327b1106b71351965dced63af2f3",
        "EXPIRES_AT": "2026-08-13T04:12:52Z",
    }
    result = subprocess.run(
        [str(DEPLOY_SCRIPT)],
        cwd=DEPLOY_SCRIPT.parent.parent,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 23
    commands = command_log.read_text().splitlines()
    apply_index = next(i for i, command in enumerate(commands) if " apply " in command)
    output_index = next(
        i for i, command in enumerate(commands) if "output -raw cloudfront_url" in command
    )
    assert apply_index < output_index
    assert "-target=aws_cloudfront_distribution.presentation" in commands[apply_index]
