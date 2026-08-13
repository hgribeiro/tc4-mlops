locals {
  account_id  = data.aws_caller_identity.current.account_id
  name_prefix = "tc4-mlops-demo-${local.account_id}"
  expires_at  = coalesce(var.expires_at, timeadd(timestamp(), "4h"))
  common_tags = {
    Project     = "tc4-mlops"
    Environment = "demo"
    Commit      = var.commit_sha
    ExpiresAt   = local.expires_at
    ManagedBy   = "terraform"
    DataClass   = "synthetic-minimized"
  }
}

resource "aws_s3_bucket" "presentation" {
  bucket        = "${local.name_prefix}-presentation"
  force_destroy = true
  tags          = local.common_tags
}

resource "aws_s3_bucket" "audit" {
  bucket = "${local.name_prefix}-audit"
  # Teardown explicitly verifies evidence and empties this bucket before the
  # Terraform destroy; force_destroy must not silently discard audit records.
  force_destroy = false
  tags          = merge(local.common_tags, { DataClass = "synthetic-audit" })
}

resource "aws_s3_bucket_ownership_controls" "presentation" {
  bucket = aws_s3_bucket.presentation.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_ownership_controls" "audit" {
  bucket = aws_s3_bucket.audit.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_public_access_block" "presentation" {
  bucket                  = aws_s3_bucket.presentation.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "audit" {
  bucket                  = aws_s3_bucket.audit.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "presentation" {
  bucket = aws_s3_bucket.presentation.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudfront_origin_access_control" "presentation" {
  name                              = "${local.name_prefix}-presentation-oac"
  description                       = "OAC for the private tc4 MLOps presentation bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "presentation" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Temporary tc4-mlops synthetic demo"
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  tags                = local.common_tags

  origin {
    domain_name              = aws_s3_bucket.presentation.bucket_regional_domain_name
    origin_id                = "private-presentation-s3"
    origin_access_control_id = aws_cloudfront_origin_access_control.presentation.id
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "private-presentation-s3"

    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate { cloudfront_default_certificate = true }
}

resource "aws_s3_bucket_policy" "presentation" {
  bucket = aws_s3_bucket.presentation.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontReadOnly"
        Effect    = "Allow"
        Principal = { Service = "cloudfront.amazonaws.com" }
        Action    = ["s3:GetObject"]
        Resource  = "${aws_s3_bucket.presentation.arn}/*"
        Condition = { StringEquals = { "AWS:SourceArn" = aws_cloudfront_distribution.presentation.arn } }
      },
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.presentation.arn, "${aws_s3_bucket.presentation.arn}/*"]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.presentation]
}

resource "aws_s3_bucket_policy" "audit" {
  bucket = aws_s3_bucket.audit.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyInsecureTransport"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [aws_s3_bucket.audit.arn, "${aws_s3_bucket.audit.arn}/*"]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.audit]
}

resource "aws_ecr_repository" "api" {
  name                 = "${local.name_prefix}-api"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true
  image_scanning_configuration { scan_on_push = true }
  tags = local.common_tags
}

resource "aws_ecr_repository_policy" "lambda_pull" {
  repository = aws_ecr_repository.api.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AllowLambdaToPullDemoImage"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
      Condition = {
        StringLike = {
          "aws:SourceArn" = "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${local.name_prefix}-api"
        }
      }
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only the current temporary tagged image"
      selection    = { tagStatus = "untagged", countType = "sinceImagePushed", countUnit = "days", countNumber = 1 }
      action       = { type = "expire" }
    }]
  })
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${local.name_prefix}-api"
  retention_in_days = 3
  tags              = local.common_tags
}

resource "aws_iam_role" "lambda" {
  name = "${local.name_prefix}-lambda"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "sts:AssumeRole", Principal = { Service = "lambda.amazonaws.com" } }]
  })
  tags = local.common_tags
}

resource "aws_iam_role_policy" "lambda_runtime" {
  name = "${local.name_prefix}-runtime"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "WriteMinimizedAuditOnly"
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.audit.arn}/decisions/*"
      },
      {
        Sid      = "WriteTechnicalLogsOnly"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "${aws_cloudwatch_log_group.api.arn}:*"
      },
      {
        Sid       = "PublishDemoMetricsOnly"
        Effect    = "Allow"
        Action    = ["cloudwatch:PutMetricData"]
        Resource  = "*"
        Condition = { StringEquals = { "cloudwatch:namespace" = "TC4MLOps/Demo" } }
      }
    ]
  })
}

resource "aws_lambda_function" "api" {
  count         = var.image_uri == null ? 0 : 1
  function_name = "${local.name_prefix}-api"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = var.image_uri
  architectures = ["x86_64"]
  timeout       = 10
  memory_size   = 512
  # New AWS accounts can retain the 10 unreserved account executions while a
  # quota increase is pending. In that explicit temporary mode, omit this
  # setting rather than attempting to reserve two executions.
  reserved_concurrent_executions = var.low_quota_mode ? null : 2

  environment {
    variables = {
      ADAPTIVE_ENABLED = "true"
      AUDIT_BACKEND    = "s3"
      AUDIT_S3_BUCKET  = aws_s3_bucket.audit.bucket
      AUDIT_S3_PREFIX  = "decisions"
    }
  }

  depends_on = [
    aws_ecr_repository_policy.lambda_pull,
    aws_iam_role_policy.lambda_runtime,
    aws_s3_bucket_server_side_encryption_configuration.audit,
    aws_cloudwatch_log_group.api,
  ]
  tags = local.common_tags
}

resource "aws_apigatewayv2_api" "http" {
  count         = var.image_uri == null ? 0 : 1
  name          = "${local.name_prefix}-http"
  protocol_type = "HTTP"
  description   = "Temporary API de Demonstração for official synthetic scenarios only"
  cors_configuration {
    allow_origins = ["https://${aws_cloudfront_distribution.presentation.domain_name}"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["content-type"]
    max_age       = 300
  }
  tags = local.common_tags
}

resource "aws_apigatewayv2_integration" "api" {
  count                  = var.image_uri == null ? 0 : 1
  api_id                 = aws_apigatewayv2_api.http[0].id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api[0].invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "decisions" {
  count     = var.image_uri == null ? 0 : 1
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "POST /v1/decisions"
  target    = "integrations/${aws_apigatewayv2_integration.api[0].id}"
}

resource "aws_apigatewayv2_route" "health" {
  count     = var.image_uri == null ? 0 : 1
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.api[0].id}"
}

resource "aws_apigatewayv2_route" "ready" {
  count     = var.image_uri == null ? 0 : 1
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "GET /ready"
  target    = "integrations/${aws_apigatewayv2_integration.api[0].id}"
}

resource "aws_apigatewayv2_stage" "default" {
  count       = var.image_uri == null ? 0 : 1
  api_id      = aws_apigatewayv2_api.http[0].id
  name        = "$default"
  auto_deploy = true
  default_route_settings {
    throttling_burst_limit = 10
    throttling_rate_limit  = 5
  }
  tags = local.common_tags
}

resource "aws_lambda_permission" "api_gateway" {
  count         = var.image_uri == null ? 0 : 1
  statement_id  = "AllowHttpApiInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http[0].execution_arn}/*/*"
}

resource "aws_cloudwatch_log_metric_filter" "decisions" {
  name           = "${local.name_prefix}-decisions"
  log_group_name = aws_cloudwatch_log_group.api.name
  pattern        = "{ $.event = \"decision\" }"
  metric_transformation {
    name      = "Decisions"
    namespace = "TC4MLOps/Demo"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "audit_failures" {
  name           = "${local.name_prefix}-audit-failures"
  log_group_name = aws_cloudwatch_log_group.api.name
  pattern        = "{ $.event = \"audit_unavailable\" }"
  metric_transformation {
    name      = "AuditFailures"
    namespace = "TC4MLOps/Demo"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.name_prefix}-lambda-errors"
  alarm_description   = "Temporary demo Lambda error signal"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  dimensions          = { FunctionName = "${local.name_prefix}-api" }
  treat_missing_data  = "notBreaching"
  tags                = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "audit_failures" {
  alarm_name          = "${local.name_prefix}-audit-failures"
  alarm_description   = "Audit persistence failed; the API fails closed"
  namespace           = "TC4MLOps/Demo"
  metric_name         = "AuditFailures"
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  tags                = local.common_tags
}

resource "aws_cloudwatch_dashboard" "demo" {
  dashboard_name = "${local.name_prefix}-dashboard"
  dashboard_body = jsonencode({
    widgets = [{
      type = "metric"
      properties = {
        title  = "API de Demonstração — decisões e erros"
        region = var.aws_region
        metrics = [
          ["TC4MLOps/Demo", "Decisions"],
          ["TC4MLOps/Demo", "AuditFailures"],
          ["AWS/Lambda", "Errors", "FunctionName", "${local.name_prefix}-api"],
          ["AWS/Lambda", "Duration", "FunctionName", "${local.name_prefix}-api"],
        ]
        period = 60
        stat   = "Sum"
      }
    }]
  })
}
