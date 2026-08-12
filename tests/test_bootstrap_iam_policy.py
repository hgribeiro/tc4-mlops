import re
from pathlib import Path


BOOTSTRAP = Path("infrastructure/environments/bootstrap/main.tf")
BUCKET_REFRESH_READS = {
    "s3:GetBucketCORS",
    "s3:GetBucketWebsite",
    "s3:GetBucketVersioning",
    "s3:GetAccelerateConfiguration",
    "s3:GetBucketRequestPayment",
    "s3:GetBucketLogging",
    "s3:GetLifecycleConfiguration",
    "s3:GetReplicationConfiguration",
    "s3:GetEncryptionConfiguration",
    "s3:GetObjectLockConfiguration",
}
RUNTIME_ROLE_REFRESH_READS = {
    "iam:ListAttachedRolePolicies",
    "iam:ListInstanceProfilesForRole",
}


def _resource_block(source: str, header: str) -> str:
    start = source.index(header)
    end = source.find('\nresource "', start + len(header))
    return source[start:] if end == -1 else source[start:end]


def _statement_actions_and_resource(policy: str, sid: str) -> tuple[set[str], str]:
    match = re.search(
        rf'Sid\s+=\s+"{sid}".*?Action\s+=\s+\[(.*?)\]\s+Resource\s+=\s+([^\n]+)',
        policy,
        flags=re.DOTALL,
    )
    assert match, f"missing {sid}"
    return set(re.findall(r'"([^"]+)"', match.group(1))), match.group(2).strip()


def test_provider_refresh_reads_are_exact_and_scoped_in_both_policy_layers():
    source = BOOTSTRAP.read_text()
    boundary = _resource_block(source, 'resource "aws_iam_policy" "automation_boundary"')
    deploy_policy = _resource_block(source, 'resource "aws_iam_role_policy" "deploy_demo"')

    for policy in (boundary, deploy_policy):
        bucket_actions, bucket_resource = _statement_actions_and_resource(
            policy, "ReadConcreteDemoBucketProviderRefreshState"
        )
        role_actions, role_resource = _statement_actions_and_resource(
            policy, "ReadConcreteDemoRuntimeRoleProviderRefreshState"
        )
        assert bucket_actions == BUCKET_REFRESH_READS
        assert bucket_resource == "local.demo_s3_arns"
        assert role_actions == RUNTIME_ROLE_REFRESH_READS
        assert role_resource == "[local.demo_runtime_role]"
        assert '"s3:Get*"' not in policy
        assert '"iam:List*"' not in policy


def test_s3_encryption_refresh_uses_the_iam_action_for_get_bucket_encryption():
    source = BOOTSTRAP.read_text()
    assert '"s3:GetBucketEncryption"' not in source
    assert '"s3:GetEncryptionConfiguration"' in source
