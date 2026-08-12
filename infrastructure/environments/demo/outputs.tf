output "state_key" {
  value       = "demo/terraform.tfstate"
  description = "State key distinct from the persistent bootstrap state."
}

output "expires_at" {
  value       = local.expires_at
  description = "Exact RFC3339 expiry tag for the temporary resources."
}

output "presentation_bucket_name" {
  value       = aws_s3_bucket.presentation.bucket
  description = "Private S3 bucket; only CloudFront OAC can read presentation objects."
}

output "audit_bucket_name" {
  value       = aws_s3_bucket.audit.bucket
  description = "Private encrypted bucket containing minimized audit objects."
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.api.repository_url
  description = "Temporary private ECR repository; tag images with commit_sha only."
}

output "cloudfront_url" {
  value       = "https://${aws_cloudfront_distribution.presentation.domain_name}"
  description = "Published HTTPS-only presentation URL."
}

output "api_url" {
  value       = var.image_uri == null ? null : aws_apigatewayv2_stage.default[0].invoke_url
  description = "Temporary API Gateway HTTP API URL after the image stage."
}

output "lambda_function_name" {
  value = var.image_uri == null ? null : aws_lambda_function.api[0].function_name
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.presentation.id
}
