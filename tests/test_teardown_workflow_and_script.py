from pathlib import Path


TEARDOWN_WORKFLOW = Path(".github/workflows/demo-teardown.yml")
TEARDOWN_SCRIPT = Path("scripts/teardown-demo-aws.sh")
EXPORT_SCRIPT = Path("scripts/export-demo-evidence.sh")
VERIFY_SCRIPT = Path("scripts/verify-demo-destroyed.sh")
BOOTSTRAP = Path("infrastructure/environments/bootstrap/main.tf")
BOOTSTRAP_VARIABLES = Path("infrastructure/environments/bootstrap/variables.tf")
DEMO_TERRAFORM = Path("infrastructure/environments/demo/main.tf")
DEPLOY_WORKFLOW = Path(".github/workflows/demo-quality-and-deploy.yml")


def test_teardown_workflow_uses_protected_oidc_lifecycle_lock_and_seven_day_artifact():
    workflow = TEARDOWN_WORKFLOW.read_text()
    for expected in (
        "workflow_dispatch", "schedule:",
        "arn:aws:iam::969212888717:role/tc4-mlops-github-deploy", "name: demo",
        "id-token: write", "retention-days: 7", "actions/upload-artifact@v4",
        "--expired-only", "DESTROY_APPROVED=DESTROY_DEMO", "DESTROY_DEMO",
        "group: tc4-mlops-demo-lifecycle", "cancel-in-progress: false",
    ):
        assert expected in workflow
    assert "AWS_ACCESS_KEY_ID" not in workflow
    assert "AWS_SECRET_ACCESS_KEY" not in workflow


def test_deploy_and_teardown_share_non_cancelling_lifecycle_lock():
    assert "group: tc4-mlops-demo-lifecycle" in DEPLOY_WORKFLOW.read_text()
    assert "cancel-in-progress: false" in DEPLOY_WORKFLOW.read_text()


def test_teardown_event_matrix_requires_confirmation_and_schedules_expired_only():
    workflow = TEARDOWN_WORKFLOW.read_text()
    section = workflow.split("      - name: Export evidence and guarded teardown", 1)[1]

    assert "if [[ \"${{ github.event_name }}\" == \"schedule\" ]]" in section
    assert "scripts/teardown-demo-aws.sh --expired-only" in section
    assert '[[ "$CONFIRMATION" == "DESTROY_DEMO" ]]' in section
    assert "DESTROY_APPROVED=DESTROY_DEMO" in section
    assert "--confirm-destroy" in section
    assert "--expired-only" not in section.split("else", 1)[1]


def test_teardown_recovers_from_empty_outputs_and_verifies_before_emptying_audit():
    teardown = TEARDOWN_SCRIPT.read_text()
    for expected in (
        'state_key="demo/terraform.tfstate"',
        'bootstrap_state_key="bootstrap/terraform.tfstate"',
        'audit_bucket="tc4-mlops-demo-${account}-audit"',
        "Unexpected managed resource in demo state", "Unexpected AWS account",
        "DESTROY_APPROVED=DESTROY_DEMO", "--expired-only",
        'scripts/export-demo-evidence.sh', "manifest-before-destroy.json",
        "empty_audit_bucket", "list-object-versions", "delete-objects",
        'terraform -chdir="$demo_dir" plan -destroy',
        "Destroy plan is not delete-only", 'terraform -chdir="$demo_dir" apply -auto-approve "$plan_file"',
        'scripts/verify-demo-destroyed.sh --allow-active-demo-state',
        'aws s3api delete-object --bucket "$state_bucket" --key "$state_key"',
        "Demo lock remains after Terraform",
    ):
        assert expected in teardown
    assert "terraform -chdir=\"$demo_dir\" output" not in teardown
    assert 'key = "$bootstrap_state_key"' not in teardown
    assert 'terraform -chdir="infrastructure/environments/bootstrap" destroy' not in teardown


def test_exporter_is_allowlisted_hashed_and_does_not_export_raw_scenarios_or_credentials():
    exporter = EXPORT_SCRIPT.read_text()
    for expected in (
        "allowed = (", "manifest.json", "hashlib.sha256", "cloudwatch get-metric-data",
        "audit-object-index.json", "No Terraform state, credentials", "raw audit records",
        "scenario payloads", "Refusing a non-canonical audit bucket",
    ):
        assert expected in exporter
    assert "context_minimized" not in exporter
    assert 'jq ' not in exporter


def test_residue_verifier_checks_temporary_families_state_lock_and_bootstrap_budget():
    verifier = VERIFY_SCRIPT.read_text()
    for expected in (
        "s3-presentation", "s3-audit", "aws ecr describe-repositories",
        "aws lambda get-function", "aws apigatewayv2 get-apis",
        "aws cloudfront list-distributions", "list-origin-access-controls",
        "cloudwatch-log-group", "cloudwatch-dashboard", "cloudwatch-alarm",
        "demo-state", "demo-lock", "bootstrap/terraform.tfstate",
        "tc4-mlops-github-deploy", "list-open-id-connect-providers", "get-policy",
        "budgets describe-budget", "--allow-active-demo-state",
    ):
        assert expected in verifier


def test_bootstrap_budget_is_persistent_monthly_actual_alert_with_one_email_variable():
    bootstrap = BOOTSTRAP.read_text()
    assert 'resource "aws_budgets_budget" "monthly_demo_cost"' in bootstrap
    assert 'limit_amount = "30"' in bootstrap
    assert 'limit_unit   = "USD"' in bootstrap
    assert 'time_unit    = "MONTHLY"' in bootstrap
    assert bootstrap.count('notification_type          = "ACTUAL"') == 2
    assert BOOTSTRAP_VARIABLES.read_text().count("hgribeirolive@gmail.com") == 1
    assert "hgribeirolive@gmail.com" not in EXPORT_SCRIPT.read_text()
    assert "hgribeirolive@gmail.com" not in TEARDOWN_SCRIPT.read_text()
    assert 'prevent_destroy = true' in bootstrap
    assert 'force_destroy = false' in DEMO_TERRAFORM.read_text()
