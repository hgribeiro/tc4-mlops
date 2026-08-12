from pathlib import Path


BOOTSTRAP = Path("infrastructure/environments/bootstrap/main.tf")


def _resource_block(source: str, header: str) -> str:
    start = source.index(header)
    end = source.find('\nresource "', start + len(header))
    return source[start:] if end == -1 else source[start:end]


def test_deploy_refresh_reads_are_exact_and_allowed_by_both_policy_layers():
    source = BOOTSTRAP.read_text()
    boundary = _resource_block(source, 'resource "aws_iam_policy" "automation_boundary"')
    deploy_policy = _resource_block(source, 'resource "aws_iam_role_policy" "deploy_demo"')

    for policy in (boundary, deploy_policy):
        assert '"s3:GetBucketCORS"' in policy
        assert '"iam:ListAttachedRolePolicies"' in policy
        assert '"s3:Get*"' not in policy
        assert '"iam:List*"' not in policy

    assert "Resource = local.demo_s3_arns" in deploy_policy
    assert "Resource = [local.demo_runtime_role]" in deploy_policy
