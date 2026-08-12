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
  demo_state_key   = "demo/terraform.tfstate"
  demo_state_arn   = "${aws_s3_bucket.terraform_state.arn}/${local.demo_state_key}"
  demo_lock_arn    = "${aws_s3_bucket.terraform_state.arn}/${local.demo_state_key}.tflock"
  # The concrete temporary demo naming convention is account-bound. It is not
  # a wildcard for arbitrary repositories, accounts or resource families.
  demo_prefix        = "tc4-mlops-demo-969212888717"
  demo_s3_arns       = ["arn:aws:s3:::${local.demo_prefix}-presentation", "arn:aws:s3:::${local.demo_prefix}-presentation/*", "arn:aws:s3:::${local.demo_prefix}-audit", "arn:aws:s3:::${local.demo_prefix}-audit/*"]
  demo_lambda_arn    = "arn:aws:lambda:us-east-1:969212888717:function:${local.demo_prefix}-api"
  demo_ecr_arn       = "arn:aws:ecr:us-east-1:969212888717:repository/${local.demo_prefix}-api"
  demo_runtime_role  = "arn:aws:iam::969212888717:role/${local.demo_prefix}-lambda"
  demo_log_group_arn = "arn:aws:logs:us-east-1:969212888717:log-group:/aws/lambda/${local.demo_prefix}-api:*"
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
      {
        Sid      = "UseSeparateDemoStateAndLockfile"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject", "s3:DeleteObject"]
        Resource = [local.demo_state_arn, local.demo_lock_arn]
      },
      {
        Sid       = "ListSeparateDemoState"
        Effect    = "Allow"
        Action    = ["s3:ListBucket"]
        Resource  = [aws_s3_bucket.terraform_state.arn]
        Condition = { StringLike = { "s3:prefix" = [local.demo_state_key, "${local.demo_state_key}.tflock"] } }
      },
      {
        Sid    = "ManageNamedTemporaryDemoResources"
        Effect = "Allow"
        Action = [
          "apigateway:GET", "apigateway:POST", "apigateway:PATCH", "apigateway:DELETE",
          "cloudfront:CreateDistribution", "cloudfront:GetDistribution", "cloudfront:GetDistributionConfig", "cloudfront:UpdateDistribution", "cloudfront:DeleteDistribution", "cloudfront:CreateOriginAccessControl", "cloudfront:GetOriginAccessControl", "cloudfront:UpdateOriginAccessControl", "cloudfront:DeleteOriginAccessControl", "cloudfront:CreateInvalidation", "cloudfront:GetInvalidation", "cloudfront:ListDistributions", "cloudfront:ListOriginAccessControls", "cloudfront:ListTagsForResource",
          "cloudwatch:PutDashboard", "cloudwatch:GetDashboard", "cloudwatch:DeleteDashboards", "cloudwatch:PutMetricAlarm", "cloudwatch:DescribeAlarms", "cloudwatch:DeleteAlarms", "cloudwatch:GetMetricData", "cloudwatch:ListTagsForResource", "cloudwatch:TagResource", "cloudwatch:UntagResource", "tag:GetResources",
          "ecr:CreateRepository", "ecr:DeleteRepository", "ecr:DescribeRepositories", "ecr:DescribeImages", "ecr:PutLifecyclePolicy", "ecr:GetLifecyclePolicy", "ecr:PutImageScanningConfiguration", "ecr:GetAuthorizationToken", "ecr:BatchGetImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage", "ecr:ListTagsForResource", "ecr:TagResource", "ecr:UntagResource",
          "lambda:CreateFunction", "lambda:GetFunction", "lambda:GetPolicy", "lambda:ListVersionsByFunction", "lambda:UpdateFunctionCode", "lambda:UpdateFunctionConfiguration", "lambda:DeleteFunction", "lambda:AddPermission", "lambda:RemovePermission", "lambda:ListTags", "lambda:TagResource", "lambda:UntagResource",
          "logs:CreateLogGroup", "logs:DeleteLogGroup", "logs:PutRetentionPolicy", "logs:DescribeLogGroups", "logs:PutMetricFilter", "logs:DeleteMetricFilter", "logs:DescribeMetricFilters", "logs:FilterLogEvents", "logs:ListTagsForResource", "logs:TagResource", "logs:UntagResource",
          "s3:CreateBucket", "s3:DeleteBucket", "s3:GetBucketLocation", "s3:GetBucketAcl", "s3:GetBucketPolicy", "s3:GetBucketCORS", "s3:PutBucketPolicy", "s3:DeleteBucketPolicy", "s3:GetBucketPublicAccessBlock", "s3:PutBucketPublicAccessBlock", "s3:GetBucketEncryption", "s3:PutEncryptionConfiguration", "s3:GetBucketOwnershipControls", "s3:PutBucketOwnershipControls", "s3:GetBucketTagging", "s3:PutBucketTagging", "s3:ListBucket", "s3:ListBucketVersions", "s3:GetObject", "s3:PutObject", "s3:DeleteObject",
          "iam:CreateRole", "iam:DeleteRole", "iam:GetRole", "iam:GetRolePolicy", "iam:PutRolePolicy", "iam:DeleteRolePolicy", "iam:ListAttachedRolePolicies", "iam:ListRolePolicies", "iam:ListRoleTags", "iam:TagRole", "iam:UntagRole", "iam:PassRole"
        ]
        Resource = "*"
      },
      {
        Sid      = "ReadPersistentTeardownSurvivors"
        Effect   = "Allow"
        Action   = ["budgets:ViewBudget", "budgets:ViewNotificationsForBudget", "budgets:ViewSubscribersForNotification", "iam:GetPolicy", "iam:ListOpenIDConnectProviders"]
        Resource = "*"
      },
    ]
  })
  tags = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_budgets_budget" "monthly_demo_cost" {
  # Budget alerts are advisory notifications, never a hard spending stop.
  name         = "tc4-mlops-demo-monthly-usd30"
  budget_type  = "COST"
  limit_amount = "30"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }

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
      # A Terraform plan writes only its native lockfile. Its plan uses
      # -refresh=false, so it needs no permission to inspect or alter demo
      # resources and cannot write the demo state.
      {
        Sid      = "ReadDemoState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion"]
        Resource = [local.demo_state_arn]
      },
      {
        Sid      = "LockDemoState"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [local.demo_lock_arn]
      },
      {
        Sid       = "ListDemoState"
        Effect    = "Allow"
        Action    = ["s3:ListBucket"]
        Resource  = [aws_s3_bucket.terraform_state.arn]
        Condition = { StringLike = { "s3:prefix" = [local.demo_state_key, "${local.demo_state_key}.tflock"] } }
      },
    ]
  })
}

resource "aws_iam_role_policy" "deploy_demo" {
  name = "${local.project_name}-deploy-temporary-demo"
  role = aws_iam_role.deploy.id
  # The actions below are deliberately enumerated for the concrete #25 names.
  # Some AWS control-plane Create APIs cannot scope Resource below "*"; the
  # accompanying permissions boundary still allows no IAM administration and
  # no service family outside this temporary demo.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "DemoStateOnly"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject", "s3:DeleteObject"]
        Resource = [local.demo_state_arn, local.demo_lock_arn]
      },
      {
        Sid       = "ListDemoStateOnly"
        Effect    = "Allow"
        Action    = ["s3:ListBucket"]
        Resource  = [aws_s3_bucket.terraform_state.arn]
        Condition = { StringLike = { "s3:prefix" = [local.demo_state_key, "${local.demo_state_key}.tflock"] } }
      },
      {
        Sid    = "OperateConcreteDataAndRuntimeResources"
        Effect = "Allow"
        Action = [
          "s3:DeleteBucket", "s3:GetBucketLocation", "s3:GetBucketAcl", "s3:GetBucketPolicy", "s3:GetBucketCORS", "s3:PutBucketPolicy", "s3:DeleteBucketPolicy", "s3:GetBucketPublicAccessBlock", "s3:PutBucketPublicAccessBlock", "s3:GetBucketEncryption", "s3:PutEncryptionConfiguration", "s3:GetBucketOwnershipControls", "s3:PutBucketOwnershipControls", "s3:GetBucketTagging", "s3:PutBucketTagging", "s3:ListBucket", "s3:ListBucketVersions", "s3:GetObject", "s3:PutObject", "s3:DeleteObject"
        ]
        Resource = local.demo_s3_arns
      },
      {
        Sid      = "OperateConcreteEcrAndLambda"
        Effect   = "Allow"
        Action   = ["ecr:DeleteRepository", "ecr:DescribeRepositories", "ecr:DescribeImages", "ecr:PutLifecyclePolicy", "ecr:GetLifecyclePolicy", "ecr:PutImageScanningConfiguration", "ecr:BatchGetImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage", "ecr:ListTagsForResource", "ecr:TagResource", "ecr:UntagResource"]
        Resource = [local.demo_ecr_arn]
      },
      {
        Sid      = "OperateConcreteLambda"
        Effect   = "Allow"
        Action   = ["lambda:GetFunction", "lambda:GetPolicy", "lambda:UpdateFunctionCode", "lambda:UpdateFunctionConfiguration", "lambda:DeleteFunction", "lambda:AddPermission", "lambda:RemovePermission", "lambda:ListTags", "lambda:TagResource", "lambda:UntagResource"]
        Resource = [local.demo_lambda_arn]
      },
      {
        Sid      = "ManageOnlyDemoRuntimeRole"
        Effect   = "Allow"
        Action   = ["iam:CreateRole", "iam:DeleteRole", "iam:GetRole", "iam:GetRolePolicy", "iam:PutRolePolicy", "iam:DeleteRolePolicy", "iam:ListAttachedRolePolicies", "iam:ListRolePolicies", "iam:ListRoleTags", "iam:TagRole", "iam:UntagRole", "iam:PassRole"]
        Resource = [local.demo_runtime_role]
      },
      {
        Sid      = "ReadPersistentTeardownSurvivors"
        Effect   = "Allow"
        Action   = ["budgets:ViewBudget", "budgets:ViewNotificationsForBudget", "budgets:ViewSubscribersForNotification", "iam:GetRole", "iam:GetPolicy", "iam:ListOpenIDConnectProviders"]
        Resource = "*"
      },
      {
        Sid      = "CreateAndReadOnlyRequiredControlPlaneResources"
        Effect   = "Allow"
        Action   = ["s3:CreateBucket", "ecr:CreateRepository", "ecr:GetAuthorizationToken", "lambda:CreateFunction", "lambda:ListVersionsByFunction", "logs:CreateLogGroup", "logs:DescribeLogGroups", "logs:PutRetentionPolicy", "logs:PutMetricFilter", "logs:DeleteMetricFilter", "logs:DescribeMetricFilters", "logs:FilterLogEvents", "logs:ListTagsForResource", "logs:TagResource", "logs:UntagResource", "cloudwatch:PutDashboard", "cloudwatch:GetDashboard", "cloudwatch:DeleteDashboards", "cloudwatch:PutMetricAlarm", "cloudwatch:DescribeAlarms", "cloudwatch:DeleteAlarms", "cloudwatch:GetMetricData", "cloudwatch:ListTagsForResource", "cloudwatch:TagResource", "cloudwatch:UntagResource", "tag:GetResources", "apigateway:GET", "apigateway:POST", "apigateway:PATCH", "apigateway:DELETE", "cloudfront:CreateDistribution", "cloudfront:GetDistribution", "cloudfront:GetDistributionConfig", "cloudfront:UpdateDistribution", "cloudfront:DeleteDistribution", "cloudfront:CreateOriginAccessControl", "cloudfront:GetOriginAccessControl", "cloudfront:UpdateOriginAccessControl", "cloudfront:DeleteOriginAccessControl", "cloudfront:CreateInvalidation", "cloudfront:GetInvalidation", "cloudfront:ListDistributions", "cloudfront:ListOriginAccessControls", "cloudfront:ListTagsForResource"]
        Resource = "*"
      }
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
