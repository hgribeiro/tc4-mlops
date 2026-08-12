from pathlib import Path


WORKFLOW = Path(".github/workflows/demo-quality-and-deploy.yml")
DEPLOY_SCRIPT = Path("scripts/deploy-demo-aws.sh")
PLAN_SCRIPT = Path("scripts/plan-demo-aws.sh")
BOOTSTRAP = Path("infrastructure/environments/bootstrap/main.tf")


def test_demo_workflow_uses_only_exact_oidc_roles_and_approved_environment():
    workflow = WORKFLOW.read_text()

    assert "id-token: write" in workflow
    assert "arn:aws:iam::969212888717:role/tc4-mlops-github-plan" in workflow
    assert "arn:aws:iam::969212888717:role/tc4-mlops-github-deploy" in workflow
    assert "name: demo" in workflow
    assert "workflow_dispatch" in workflow
    assert "github.ref == 'refs/heads/main'" in workflow
    assert "AWS_ACCESS_KEY_ID" not in workflow
    assert "AWS_SECRET_ACCESS_KEY" not in workflow
    assert "access-key-id" not in workflow


def test_demo_workflow_event_matrix_promotes_only_main_push_to_deploy():
    workflow = WORKFLOW.read_text()

    # The quality/plan gates run on the promotion PR and resulting main push.
    assert "pull_request:" in workflow
    assert "push:" in workflow
    assert "branches: [main]" in workflow
    assert "if: github.event_name == 'pull_request' || github.ref == 'refs/heads/main'" in workflow

    # A merge is the human promotion approval: only a push to main may deploy.
    assert "github.event_name == 'push'" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "github.event_name == 'pull_request'" not in workflow.split("  deploy:", 1)[1]
    assert "github.ref == 'refs/heads/develop'" not in workflow

    deploy_condition = workflow.split("  deploy:", 1)[1].split("\n    runs-on:", 1)[0]
    assert "github.event_name == 'push'" in deploy_condition
    assert "github.ref == 'refs/heads/main'" in deploy_condition
    assert "github.event_name == 'pull_request'" not in deploy_condition


def test_deploy_keeps_low_quota_safe_when_event_has_no_dispatch_inputs():
    workflow = WORKFLOW.read_text()
    deploy_section = workflow.split("  deploy:", 1)[1]

    assert "LOW_QUOTA_MODE: ${{ inputs.low_quota_mode || 'true' }}" in deploy_section
    assert "LOW_QUOTA_MODE: \"true\"" in workflow


def test_demo_workflow_validates_all_release_seams_before_plan_or_deploy():
    workflow = WORKFLOW.read_text()

    for required in (
        "python -m pytest",
        "evaluate-golden-set",
        "validate-experiment-artifacts",
        "npx playwright install --with-deps chromium && npm test",
        "docker build --platform linux/amd64 -f Dockerfile.lambda",
        "terraform fmt -check -recursive",
        "terraform -chdir=\"$directory\" validate",
        "terraform -chdir=\"$directory\" test",
        "needs: quality",
        "needs: [quality, plan]",
    ):
        assert required in workflow


def test_plan_and_deploy_reuse_safe_scripts_with_immutable_sha_and_low_quota_default():
    workflow = WORKFLOW.read_text()
    plan = PLAN_SCRIPT.read_text()
    deploy = DEPLOY_SCRIPT.read_text()

    assert "scripts/plan-demo-aws.sh" in workflow
    assert "scripts/deploy-demo-aws.sh" in workflow
    assert "-refresh=false" in plan
    assert 'low_quota_mode="${LOW_QUOTA_MODE:-true}"' in plan
    assert 'low_quota_mode="${LOW_QUOTA_MODE:-true}"' in deploy
    assert ':latest' not in plan
    assert ':latest' not in deploy
    assert 'docker push "$ecr_url:$commit_sha"' in deploy
    assert "Policy version: ${policy_version}" in deploy
    assert "ExpiresAt: ${expires_at}" in deploy


def test_oidc_plan_state_access_is_separate_and_deploy_permissions_remain_bounded():
    bootstrap = BOOTSTRAP.read_text()

    assert 'Sid      = "ReadDemoState"' in bootstrap
    assert 'Sid      = "LockDemoState"' in bootstrap
    assert 'Sid       = "ListDemoState"' in bootstrap
    assert "tc4-mlops-demo-969212888717" in bootstrap
    assert '"logs:FilterLogEvents"' in bootstrap
    assert '"cloudfront:GetInvalidation"' in bootstrap
    assert '"iam:*"' not in bootstrap
    assert "AdministratorAccess" not in bootstrap
