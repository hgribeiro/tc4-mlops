locals {
  project_name = "tc4-mlops"
  github_repo  = "hgribeiro/tc4-mlops"

  # These are deliberately exact GitHub OIDC subjects, not patterns. Pull
  # requests and main may plan; only the protected GitHub `demo` environment
  # may deploy.
  plan_subjects = [
    "repo:${local.github_repo}:pull_request",
    "repo:${local.github_repo}:ref:refs/heads/main",
  ]
  deploy_subjects = [
    "repo:${local.github_repo}:environment:demo",
  ]

  state_object_arn = "${aws_s3_bucket.terraform_state.arn}/${var.state_key}"
  lock_object_arn  = "${aws_s3_bucket.terraform_state.arn}/${var.state_key}.tflock"
  common_tags = {
    Project     = local.project_name
    Environment = "bootstrap"
    DataClass   = "terraform-state"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket        = var.state_bucket_name
  force_destroy = false
  tags          = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_ownership_controls" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "terraform_state_tls" {
  bucket = aws_s3_bucket.terraform_state.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyInsecureTransport"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [aws_s3_bucket.terraform_state.arn, "${aws_s3_bucket.terraform_state.arn}/*"]
      Condition = {
        Bool = { "aws:SecureTransport" = "false" }
      }
    }]
  })
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
  tags            = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_policy" "automation_boundary" {
  name        = "${local.project_name}-github-automation-boundary"
  description = "Limita as roles OIDC atuais ao state e lockfile do bootstrap; permissões demo exigem alteração revisada desta boundary."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListOnlyBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.terraform_state.arn]
        Condition = {
          StringLike = {
            "s3:prefix" = [var.state_key, "${var.state_key}.tflock"]
          }
        }
      },
      {
        Sid      = "ReadWriteBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject"]
        Resource = [local.state_object_arn]
      },
      {
        Sid      = "UseNativeS3Lockfile"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [local.lock_object_arn]
      },
    ]
  })
  tags = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role" "plan" {
  name                 = "${local.project_name}-github-plan"
  max_session_duration = 3600
  permissions_boundary = aws_iam_policy.automation_boundary.arn
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "GitHubActionsPlanOnly"
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = local.plan_subjects
        }
      }
    }]
  })
  tags = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role" "deploy" {
  name                 = "${local.project_name}-github-deploy"
  max_session_duration = 3600
  permissions_boundary = aws_iam_policy.automation_boundary.arn
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "GitHubActionsDemoEnvironmentOnly"
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = local.deploy_subjects
        }
      }
    }]
  })
  tags = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role_policy" "plan_backend" {
  name = "${local.project_name}-plan-bootstrap-state"
  role = aws_iam_role.plan.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion"]
        Resource = [local.state_object_arn]
      },
      {
        Sid      = "LockBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [local.lock_object_arn]
      },
      {
        Sid      = "ListBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.terraform_state.arn]
        Condition = {
          StringLike = {
            "s3:prefix" = [var.state_key, "${var.state_key}.tflock"]
          }
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "deploy_backend" {
  name = "${local.project_name}-deploy-bootstrap-state"
  role = aws_iam_role.deploy.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadWriteBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject"]
        Resource = [local.state_object_arn]
      },
      {
        Sid      = "LockBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [local.lock_object_arn]
      },
      {
        Sid      = "ListBootstrapState"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.terraform_state.arn]
        Condition = {
          StringLike = {
            "s3:prefix" = [var.state_key, "${var.state_key}.tflock"]
          }
        }
      },
    ]
  })
}
