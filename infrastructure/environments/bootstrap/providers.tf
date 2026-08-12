provider "aws" {
  region = var.aws_region

  # Authentication deliberately comes from the standard AWS SDK chain. For a
  # human bootstrap this is an IAM Identity Center/SSO profile, never keys in
  # Terraform variables, state, or repository files.
}
