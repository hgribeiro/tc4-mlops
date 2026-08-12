terraform {
  required_version = ">= 1.10.0"

  # The first bootstrap apply uses `terraform init -backend=false`, then the
  # generated backend.hcl migrates this state into the bucket created here.
  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
