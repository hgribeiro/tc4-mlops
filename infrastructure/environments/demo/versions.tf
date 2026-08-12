terraform {
  required_version = ">= 1.10.0"

  # This backend is initialized with the persistent bootstrap bucket but always
  # uses demo/terraform.tfstate; it never shares the bootstrap lifecycle.
  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
