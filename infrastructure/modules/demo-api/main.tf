resource "aws_s3_bucket" "audit" {
  bucket        = "${var.name_prefix}-audit"
  force_destroy = var.force_destroy_audit_bucket
  tags          = var.tags
}

resource "aws_s3_bucket_public_access_block" "audit" {
  bucket = aws_s3_bucket.audit.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_iam_role" "lambda" {
  count = var.lambda_zip_path == null ? 0 : 1
  name  = "${var.name_prefix}-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "audit_write" {
  count = var.lambda_zip_path == null ? 0 : 1
  name  = "${var.name_prefix}-audit-write"
  role  = aws_iam_role.lambda[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "WriteMinimizedAuditOnly"
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${aws_s3_bucket.audit.arn}/${var.audit_prefix}/*"
    }]
  })
}

resource "aws_lambda_function" "api" {
  count            = var.lambda_zip_path == null ? 0 : 1
  function_name    = "${var.name_prefix}-api"
  role             = aws_iam_role.lambda[0].arn
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)
  handler          = "responsible_next_step.api.handler"
  runtime          = "python3.12"
  architectures    = ["x86_64"]
  timeout          = 10

  environment {
    variables = merge({
      ADAPTIVE_ENABLED      = "true"
      AUDIT_BACKEND         = "s3"
      AUDIT_S3_BUCKET       = aws_s3_bucket.audit.bucket
      AUDIT_S3_PREFIX       = var.audit_prefix
      AWS_DEFAULT_REGION    = "us-east-1"
      AWS_ACCESS_KEY_ID     = "test"
      AWS_SECRET_ACCESS_KEY = "test"
      }, var.localstack_endpoint_url == null ? {} : {
      AUDIT_S3_ENDPOINT_URL = var.localstack_endpoint_url
    })
  }

  depends_on = [
    aws_iam_role_policy.audit_write,
    aws_s3_bucket_public_access_block.audit,
    aws_s3_bucket_server_side_encryption_configuration.audit,
  ]
  tags = var.tags
}

# API Gateway REST APIs are supported by LocalStack Community. HTTP APIs (v2)
# are not used here because that transport requires a paid LocalStack license.
resource "aws_api_gateway_rest_api" "http" {
  count = var.lambda_zip_path == null ? 0 : 1
  name  = "${var.name_prefix}-http"
  tags  = var.tags
}

resource "aws_api_gateway_resource" "v1" {
  count       = var.lambda_zip_path == null ? 0 : 1
  rest_api_id = aws_api_gateway_rest_api.http[0].id
  parent_id   = aws_api_gateway_rest_api.http[0].root_resource_id
  path_part   = "v1"
}

resource "aws_api_gateway_resource" "decisions" {
  count       = var.lambda_zip_path == null ? 0 : 1
  rest_api_id = aws_api_gateway_rest_api.http[0].id
  parent_id   = aws_api_gateway_resource.v1[0].id
  path_part   = "decisions"
}

resource "aws_api_gateway_method" "decision" {
  count         = var.lambda_zip_path == null ? 0 : 1
  rest_api_id   = aws_api_gateway_rest_api.http[0].id
  resource_id   = aws_api_gateway_resource.decisions[0].id
  http_method   = "POST"
  authorization = "NONE"
}

data "aws_region" "current" {}

resource "aws_api_gateway_integration" "api" {
  count                   = var.lambda_zip_path == null ? 0 : 1
  rest_api_id             = aws_api_gateway_rest_api.http[0].id
  resource_id             = aws_api_gateway_resource.decisions[0].id
  http_method             = aws_api_gateway_method.decision[0].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${data.aws_region.current.id}:lambda:path/2015-03-31/functions/${aws_lambda_function.api[0].arn}/invocations"
}

resource "aws_api_gateway_deployment" "current" {
  count       = var.lambda_zip_path == null ? 0 : 1
  rest_api_id = aws_api_gateway_rest_api.http[0].id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.v1[0].id,
      aws_api_gateway_resource.decisions[0].id,
      aws_api_gateway_method.decision[0].id,
      aws_api_gateway_integration.api[0].id,
      aws_api_gateway_integration.api[0].uri,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "default" {
  count         = var.lambda_zip_path == null ? 0 : 1
  rest_api_id   = aws_api_gateway_rest_api.http[0].id
  deployment_id = aws_api_gateway_deployment.current[0].id
  stage_name    = "local"
  tags          = var.tags
}

resource "aws_lambda_permission" "api_gateway" {
  count         = var.lambda_zip_path == null ? 0 : 1
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.http[0].execution_arn}/*/*"
}
