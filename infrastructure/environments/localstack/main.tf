locals {
  name_prefix = "responsible-next-step-local"
  common_tags = {
    Project     = "responsible-next-step-lab"
    Environment = "localstack"
    DataClass   = "synthetic-minimized"
  }
}

module "demo_api" {
  source = "../../modules/demo-api"

  name_prefix                = local.name_prefix
  lambda_zip_path            = var.lambda_zip_path
  localstack_endpoint_url    = "http://localstack:4566"
  force_destroy_audit_bucket = true
  tags                       = local.common_tags
}
