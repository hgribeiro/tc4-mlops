output "audit_bucket_name" {
  value = aws_s3_bucket.audit.bucket
}

output "api_endpoint" {
  value = var.lambda_zip_path == null ? null : aws_api_gateway_stage.default[0].invoke_url
}

output "api_gateway_id" {
  value = var.lambda_zip_path == null ? null : aws_api_gateway_rest_api.http[0].id
}
