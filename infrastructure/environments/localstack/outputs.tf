output "api_endpoint" {
  description = "Endpoint HTTP emulado no host; só existe após o ZIP Lambda ser aplicado."
  value       = module.demo_api.api_gateway_id == null ? null : "${var.localstack_endpoint}/restapis/${module.demo_api.api_gateway_id}/local/_user_request_"
}

output "audit_bucket_name" {
  description = "Bucket privado LocalStack que contém objetos minimizados por decisão."
  value       = module.demo_api.audit_bucket_name
}
