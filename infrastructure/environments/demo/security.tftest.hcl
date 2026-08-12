mock_provider "aws" {}

override_resource {
  target = aws_iam_role.lambda
  values = { arn = "arn:aws:iam::969212888717:role/tc4-mlops-demo-969212888717-lambda" }
}

override_resource {
  target = aws_apigatewayv2_api.http[0]
  values = {
    execution_arn = "arn:aws:execute-api:us-east-1:969212888717:example"
    id            = "example"
  }
}

override_resource {
  target = aws_cloudfront_distribution.presentation
  values = {
    arn         = "arn:aws:cloudfront::969212888717:distribution/E1234567890"
    domain_name = "d111111abcdef8.cloudfront.net"
    id          = "E1234567890"
  }
}

variables {
  commit_sha = "0123456789abcdef0123456789abcdef01234567"
  expires_at = "2030-01-01T04:00:00Z"
  image_uri  = "969212888717.dkr.ecr.us-east-1.amazonaws.com/tc4-mlops-demo-969212888717-api:0123456789abcdef0123456789abcdef01234567"
}

run "keeps_presentation_and_audit_private_and_encrypted" {
  command = apply

  assert {
    condition     = aws_s3_bucket_public_access_block.presentation.block_public_acls && aws_s3_bucket_public_access_block.presentation.block_public_policy && aws_s3_bucket_public_access_block.audit.block_public_acls && aws_s3_bucket_public_access_block.audit.block_public_policy
    error_message = "Presentation and audit buckets must block public access."
  }

  assert {
    condition     = strcontains(aws_s3_bucket_policy.presentation.policy, "cloudfront.amazonaws.com") && strcontains(aws_s3_bucket_policy.presentation.policy, "DenyInsecureTransport") && strcontains(aws_s3_bucket_policy.audit.policy, "DenyInsecureTransport")
    error_message = "Only CloudFront OAC may read the presentation and both buckets require TLS."
  }

  assert {
    condition     = aws_cloudfront_distribution.presentation.default_cache_behavior[0].viewer_protocol_policy == "redirect-to-https"
    error_message = "CloudFront must redirect viewers to HTTPS."
  }
}

run "uses_immutable_image_and_conservative_public_api_limits" {
  command = apply

  assert {
    condition     = aws_ecr_repository.api.image_tag_mutability == "IMMUTABLE" && aws_lambda_function.api[0].package_type == "Image" && aws_lambda_function.api[0].timeout == 10 && aws_lambda_function.api[0].reserved_concurrent_executions == 2
    error_message = "The Lambda container must use immutable ECR tags, timeout 10 and reserved concurrency 2."
  }

  assert {
    condition     = aws_apigatewayv2_stage.default[0].default_route_settings[0].throttling_rate_limit == 5 && aws_apigatewayv2_stage.default[0].default_route_settings[0].throttling_burst_limit == 10
    error_message = "HTTP API must throttle at 5/s with burst 10."
  }

  assert {
    condition     = strcontains(jsonencode(aws_apigatewayv2_api.http[0].cors_configuration), "cloudfront.net") && !strcontains(jsonencode(aws_apigatewayv2_api.http[0].cors_configuration), "*")
    error_message = "CORS must be restricted to the generated CloudFront origin."
  }
}

run "tags_temporary_resources_and_limits_runtime_role" {
  command = apply

  assert {
    condition     = aws_s3_bucket.presentation.tags["Project"] == "tc4-mlops" && aws_s3_bucket.presentation.tags["Environment"] == "demo" && aws_s3_bucket.presentation.tags["Commit"] == var.commit_sha && aws_s3_bucket.presentation.tags["ExpiresAt"] == var.expires_at
    error_message = "Temporary resources require project, environment, commit and expiry tags."
  }

  assert {
    condition     = strcontains(aws_iam_role_policy.lambda_runtime.policy, "s3:PutObject") && strcontains(aws_iam_role_policy.lambda_runtime.policy, "/decisions/*") && !strcontains(aws_iam_role_policy.lambda_runtime.policy, "s3:GetObject")
    error_message = "Lambda may write only minimized audit objects and may not read them."
  }
}
