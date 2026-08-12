output "state_bucket_name" {
  description = "Bucket persistente do state do bootstrap; não pertence ao ciclo de vida da demo."
  value       = aws_s3_bucket.terraform_state.bucket
}

output "backend_config" {
  description = "Conteúdo não sensível para backend.hcl, usado somente após o primeiro apply local e a migração de state."
  value       = <<-EOT
    bucket       = "${aws_s3_bucket.terraform_state.bucket}"
    key          = "${var.state_key}"
    region       = "${var.aws_region}"
    encrypt      = true
    use_lockfile = true
  EOT
}

output "github_actions_role_arns" {
  description = "ARNs a configurar nos workflows GitHub Actions; não são credenciais."
  value = {
    plan   = aws_iam_role.plan.arn
    deploy = aws_iam_role.deploy.arn
  }
}
