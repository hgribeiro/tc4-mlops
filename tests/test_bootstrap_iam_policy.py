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
    "s3:GetBucketObjectLockConfiguration",
}
RUNTIME_ROLE_REFRESH_READS = {
    "iam:ListAttachedRolePolicies",
    "iam:ListInstanceProfilesForRole",
}
CLOUDFRONT_DEMO_TAGS = {
    '"aws:RequestTag/Project"     = "tc4-mlops"',
    '"aws:RequestTag/Environment" = "demo"',
    '"aws:RequestTag/ManagedBy"   = "terraform"',
    '"aws:ResourceTag/Project"     = "tc4-mlops"',
    '"aws:ResourceTag/Environment" = "demo"',
    '"aws:ResourceTag/ManagedBy"   = "terraform"',
}
ECR_REPOSITORY_POLICY_ACTIONS = {
    "ecr:GetRepositoryPolicy",
    "ecr:SetRepositoryPolicy",
    "ecr:DeleteRepositoryPolicy",
}
ECR_IMAGE_PUSH_ACTIONS = {
    "ecr:BatchCheckLayerAvailability",
    "ecr:GetDownloadUrlForLayer",
    "ecr:InitiateLayerUpload",
    "ecr:UploadLayerPart",
    "ecr:CompleteLayerUpload",
    "ecr:PutImage",
}
TEARDOWN_DELETES = {
    "EcrLifecycle": (
        {"ecr:DeleteLifecyclePolicy"},
        "[local.demo_ecr_arn]",
    ),
    "DemoLogGroup": (
        {"logs:DeleteLogGroup"},
        "[local.demo_log_group_arn]",
    ),
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

    assert '"s3:GetObjectLockConfiguration"' not in source

    for policy in (boundary, deploy_policy):
        bucket_actions, bucket_resource = _statement_actions_and_resource(
            policy, "DemoBucketRefresh"
        )
        role_actions, role_resource = _statement_actions_and_resource(
            policy, "DemoRoleRefresh"
        )
        assert bucket_actions == BUCKET_REFRESH_READS
        assert bucket_resource == "local.demo_s3_arns"
        assert role_actions == RUNTIME_ROLE_REFRESH_READS
        assert role_resource == "[local.demo_runtime_role]"
        assert '"s3:Get*"' not in policy
        assert '"iam:List*"' not in policy


def test_cloudfront_tagging_is_exact_and_scoped_in_both_policy_layers():
    source = BOOTSTRAP.read_text()
    boundary = _resource_block(source, 'resource "aws_iam_policy" "automation_boundary"')
    deploy_policy = _resource_block(source, 'resource "aws_iam_role_policy" "deploy_demo"')

    for policy in (boundary, deploy_policy):
        request_actions, request_resource = _statement_actions_and_resource(
            policy, "CFTagCreate"
        )
        existing_actions, existing_resource = _statement_actions_and_resource(
            policy, "CFRetag"
        )
        assert request_actions == {"cloudfront:TagResource"}
        assert existing_actions == {
            "cloudfront:TagResource",
            "cloudfront:UntagResource",
        }
        assert request_resource == "[local.demo_cloudfront_distribution_arn]"
        assert existing_resource == "[local.demo_cloudfront_distribution_arn]"
        assert all(tag in policy for tag in CLOUDFRONT_DEMO_TAGS)


def test_s3_encryption_refresh_uses_the_iam_action_for_get_bucket_encryption():
    source = BOOTSTRAP.read_text()
    assert '"s3:GetBucketEncryption"' not in source
    assert '"s3:GetEncryptionConfiguration"' in source


def test_ecr_image_push_protocol_is_allowed_in_both_policy_layers():
    source = BOOTSTRAP.read_text()
    boundary = _resource_block(source, 'resource "aws_iam_policy" "automation_boundary"')
    deploy_policy = _resource_block(source, 'resource "aws_iam_role_policy" "deploy_demo"')

    boundary_actions, boundary_resource = _statement_actions_and_resource(
        boundary, "DemoOperations"
    )
    deploy_actions, deploy_resource = _statement_actions_and_resource(
        deploy_policy, "OperateConcreteEcrAndLambda"
    )

    assert ECR_IMAGE_PUSH_ACTIONS <= boundary_actions
    assert boundary_resource == '"*"'
    assert ECR_IMAGE_PUSH_ACTIONS <= deploy_actions
    assert deploy_resource == "[local.demo_ecr_arn]"


def test_api_gateway_tagging_and_ecr_repository_policy_are_allowed_in_both_layers():
    source = BOOTSTRAP.read_text()
    boundary = _resource_block(source, 'resource "aws_iam_policy" "automation_boundary"')
    deploy_policy = _resource_block(source, 'resource "aws_iam_role_policy" "deploy_demo"')

    boundary_actions, _ = _statement_actions_and_resource(
        boundary, "DemoOperations"
    )
    control_actions, control_resource = _statement_actions_and_resource(
        deploy_policy, "CreateAndReadOnlyRequiredControlPlaneResources"
    )
    ecr_actions, ecr_resource = _statement_actions_and_resource(
        deploy_policy, "OperateConcreteEcrAndLambda"
    )

    assert "apigateway:PUT" in boundary_actions
    assert "apigateway:PUT" in control_actions
    assert "apigateway:TagResource" not in source
    assert "apigateway:UntagResource" not in source
    assert control_resource == '"*"'
    assert ECR_REPOSITORY_POLICY_ACTIONS <= boundary_actions
    assert ECR_REPOSITORY_POLICY_ACTIONS <= ecr_actions
    assert ecr_resource == "[local.demo_ecr_arn]"

    for policy in (boundary, deploy_policy):
        service_linked_actions, service_linked_resource = _statement_actions_and_resource(
            policy, "ApiGwServiceRole"
        )
        assert service_linked_actions == {"iam:CreateServiceLinkedRole"}
        assert "ops.apigateway.amazonaws.com/AWSServiceRoleForAPIGateway" in service_linked_resource
        assert '"iam:AWSServiceName" = "ops.apigateway.amazonaws.com"' in policy

    bucket_actions, bucket_resource = _statement_actions_and_resource(
        deploy_policy, "OperateConcreteDataAndRuntimeResources"
    )
    assert "s3:ListTagsForResource" in bucket_actions
    assert bucket_resource == "local.demo_s3_arns"


def test_evidenced_teardown_deletes_are_exact_and_scoped_in_both_policy_layers():
    source = BOOTSTRAP.read_text()
    boundary = _resource_block(source, 'resource "aws_iam_policy" "automation_boundary"')
    deploy_policy = _resource_block(source, 'resource "aws_iam_role_policy" "deploy_demo"')

    for policy in (boundary, deploy_policy):
        for sid, (expected_actions, expected_resource) in TEARDOWN_DELETES.items():
            actions, resource = _statement_actions_and_resource(policy, sid)
            assert actions == expected_actions
            assert resource == expected_resource

    assert '"logs:DeleteLogGroup"' not in _statement_actions_and_resource(
        boundary, "DemoOperations"
    )[0]
