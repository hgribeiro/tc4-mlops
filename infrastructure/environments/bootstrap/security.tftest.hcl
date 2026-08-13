mock_provider "aws" {}

variables {
  aws_region         = "us-east-1"
  state_bucket_name  = "tc4-mlops-tfstate-123456789012-example"
  budget_alert_email = "budget-alert@example.invalid"
}

override_resource {
  target = aws_s3_bucket.terraform_state
  values = {
    arn = "arn:aws:s3:::tc4-mlops-tfstate-123456789012-example"
  }
}

override_resource {
  target = aws_iam_openid_connect_provider.github
  values = {
    arn = "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
  }
}

override_resource {
  target = aws_iam_policy.automation_boundary
  values = {
    arn = "arn:aws:iam::123456789012:policy/tc4-mlops-github-automation-boundary"
  }
}

run "keeps_persistent_state_private_versioned_and_non_destructible" {
  command = apply

  assert {
    condition     = aws_s3_bucket.terraform_state.force_destroy == false
    error_message = "O backend persistente não pode remover objetos ao destruir."
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.terraform_state.block_public_acls && aws_s3_bucket_public_access_block.terraform_state.block_public_policy && aws_s3_bucket_public_access_block.terraform_state.ignore_public_acls && aws_s3_bucket_public_access_block.terraform_state.restrict_public_buckets
    error_message = "O backend deve bloquear toda exposição pública."
  }

  assert {
    condition     = one([for rule in aws_s3_bucket_versioning.terraform_state.versioning_configuration : rule.status]) == "Enabled"
    error_message = "O backend deve manter versões do state."
  }

  assert {
    condition     = one([for rule in aws_s3_bucket_server_side_encryption_configuration.terraform_state.rule : one([for encryption in rule.apply_server_side_encryption_by_default : encryption.sse_algorithm])]) == "AES256"
    error_message = "O backend deve usar criptografia server-side."
  }

  assert {
    condition     = one([for rule in aws_s3_bucket_ownership_controls.terraform_state.rule : rule.object_ownership]) == "BucketOwnerEnforced"
    error_message = "O backend não deve aceitar ownership por ACL."
  }

  assert {
    condition     = strcontains(aws_s3_bucket_policy.terraform_state_tls.policy, "aws:SecureTransport") && strcontains(aws_s3_bucket_policy.terraform_state_tls.policy, "Deny")
    error_message = "O backend deve negar transporte sem TLS."
  }

  assert {
    condition     = strcontains(output.backend_config, "use_lockfile = true") && strcontains(output.backend_config, "encrypt      = true")
    error_message = "A configuração gerada do backend deve habilitar criptografia e lockfile S3 nativo."
  }
}

run "creates_monthly_advisory_budget_without_a_spend_stop" {
  command = apply

  assert {
    condition     = aws_budgets_budget.monthly_demo_cost.limit_amount == "30" && aws_budgets_budget.monthly_demo_cost.limit_unit == "USD" && aws_budgets_budget.monthly_demo_cost.time_unit == "MONTHLY"
    error_message = "O budget da demo deve ser mensal e limitado a USD 30."
  }

  assert {
    condition     = length(aws_budgets_budget.monthly_demo_cost.notification) == 2 && alltrue([for notification in aws_budgets_budget.monthly_demo_cost.notification : notification.notification_type == "ACTUAL" && notification.threshold_type == "PERCENTAGE"])
    error_message = "O budget deve enviar apenas alertas de custo realizado em percentual."
  }
}

run "restricts_oidc_to_repository_refs_and_demo_environment" {
  command = apply

  assert {
    condition     = strcontains(aws_iam_role.plan.assume_role_policy, "repo:hgribeiro/tc4-mlops:pull_request") && strcontains(aws_iam_role.plan.assume_role_policy, "repo:hgribeiro/tc4-mlops:ref:refs/heads/main") && !strcontains(aws_iam_role.plan.assume_role_policy, "*")
    error_message = "A trust de plan deve aceitar somente o repositório e refs esperados."
  }

  assert {
    condition     = strcontains(aws_iam_role.deploy.assume_role_policy, "repo:hgribeiro/tc4-mlops:environment:demo") && !strcontains(aws_iam_role.deploy.assume_role_policy, "*")
    error_message = "A trust de deploy deve exigir o ambiente GitHub demo sem wildcard."
  }

  assert {
    condition     = strcontains(aws_iam_role.plan.assume_role_policy, "sts.amazonaws.com") && strcontains(aws_iam_role.deploy.assume_role_policy, "sts.amazonaws.com")
    error_message = "As roles OIDC devem validar a audience STS."
  }
}

run "separates_plan_and_deploy_and_limits_them_to_bootstrap_and_concrete_demo_operations" {
  command = apply

  assert {
    condition     = aws_iam_role.plan.permissions_boundary == aws_iam_policy.automation_boundary.arn && aws_iam_role.deploy.permissions_boundary == aws_iam_policy.automation_boundary.arn
    error_message = "As roles de automação devem manter uma permissions boundary explícita."
  }

  assert {
    condition = alltrue([
      for statement in jsondecode(aws_iam_role_policy.plan_backend.policy).Statement :
      !(contains(statement.Action, "s3:PutObject") && contains(statement.Resource, "arn:aws:s3:::tc4-mlops-tfstate-123456789012-example/bootstrap/terraform.tfstate"))
    ])
    error_message = "Plan deve gravar somente o lockfile, não o state."
  }

  assert {
    condition = alltrue([
      for statement in jsondecode(aws_iam_role_policy.plan_backend.policy).Statement :
      !(contains(statement.Action, "s3:PutObject") && contains(statement.Resource, "arn:aws:s3:::tc4-mlops-tfstate-123456789012-example/demo/terraform.tfstate"))
    ]) && strcontains(aws_iam_role_policy.plan_backend.policy, "demo/terraform.tfstate.tflock")
    error_message = "Plan pode bloquear a demo, mas nunca gravar seu state."
  }

  assert {
    condition     = strcontains(aws_iam_role_policy.deploy_backend.policy, "bootstrap/terraform.tfstate") && strcontains(aws_iam_role_policy.deploy_backend.policy, "bootstrap/terraform.tfstate.tflock")
    error_message = "Deploy deve ter acesso explícito ao state e lockfile do bootstrap."
  }

  assert {
    condition     = strcontains(aws_iam_role_policy.deploy_demo.policy, "demo/terraform.tfstate") && strcontains(aws_iam_role_policy.deploy_demo.policy, "tc4-mlops-demo-969212888717") && !strcontains(aws_iam_role_policy.deploy_demo.policy, "AdministratorAccess")
    error_message = "Deploy pode operar apenas o state e os nomes concretos da demo, nunca administração ampla."
  }

  assert {
    condition     = strcontains(aws_iam_policy.automation_boundary.policy, "DemoStateRW") && !strcontains(aws_iam_policy.automation_boundary.policy, "iam:*")
    error_message = "A boundary deve permitir o state separado da demo sem liberar IAM amplo."
  }
}

run "permits_evidenced_provider_refresh_reads_on_exact_demo_resources" {
  command = apply

  assert {
    condition = alltrue([
      for policy in [jsondecode(aws_iam_policy.automation_boundary.policy).Statement, jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement] :
      length([for statement in policy : statement if statement.Sid == "DemoBucketRefresh"]) == 1 &&
      toset(one([for statement in policy : statement.Action if statement.Sid == "DemoBucketRefresh"])) == toset(["s3:GetBucketCORS", "s3:GetBucketWebsite", "s3:GetBucketVersioning", "s3:GetAccelerateConfiguration", "s3:GetBucketRequestPayment", "s3:GetBucketLogging", "s3:GetLifecycleConfiguration", "s3:GetReplicationConfiguration", "s3:GetEncryptionConfiguration", "s3:GetBucketObjectLockConfiguration"]) &&
      toset(one([for statement in policy : statement.Resource if statement.Sid == "DemoBucketRefresh"])) == toset(local.demo_s3_arns)
    ])
    error_message = "As duas camadas devem permitir exatamente os reads S3 do refresh somente nos buckets concretos da demo."
  }

  assert {
    condition = alltrue([
      for policy in [jsondecode(aws_iam_policy.automation_boundary.policy).Statement, jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement] :
      length([for statement in policy : statement if statement.Sid == "DemoRoleRefresh"]) == 1 &&
      toset(one([for statement in policy : statement.Action if statement.Sid == "DemoRoleRefresh"])) == toset(["iam:ListAttachedRolePolicies", "iam:ListInstanceProfilesForRole"]) &&
      toset(one([for statement in policy : statement.Resource if statement.Sid == "DemoRoleRefresh"])) == toset([local.demo_runtime_role])
    ])
    error_message = "As duas camadas devem permitir exatamente os reads IAM do refresh somente na role runtime concreta."
  }

  assert {
    condition = alltrue([
      for policy in [jsondecode(aws_iam_policy.automation_boundary.policy).Statement, jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement] :
      length([for statement in policy : statement if statement.Sid == "CFTagCreate"]) == 1 &&
      toset(one([for statement in policy : statement.Action if statement.Sid == "CFTagCreate"])) == toset(["cloudfront:TagResource"]) &&
      toset(one([for statement in policy : statement.Resource if statement.Sid == "CFTagCreate"])) == toset([local.demo_cloudfront_distribution_arn]) &&
      one([for statement in policy : statement.Condition.StringEquals if statement.Sid == "CFTagCreate"]) == { "aws:RequestTag/Project" = "tc4-mlops", "aws:RequestTag/Environment" = "demo", "aws:RequestTag/ManagedBy" = "terraform" } &&
      length([for statement in policy : statement if statement.Sid == "CFRetag"]) == 1 &&
      toset(one([for statement in policy : statement.Action if statement.Sid == "CFRetag"])) == toset(["cloudfront:TagResource", "cloudfront:UntagResource"]) &&
      toset(one([for statement in policy : statement.Resource if statement.Sid == "CFRetag"])) == toset([local.demo_cloudfront_distribution_arn]) &&
      one([for statement in policy : statement.Condition.StringEquals if statement.Sid == "CFRetag"]) == { "aws:ResourceTag/Project" = "tc4-mlops", "aws:ResourceTag/Environment" = "demo", "aws:ResourceTag/ManagedBy" = "terraform" }
    ])
    error_message = "As duas camadas devem permitir tagging CloudFront somente quando as tags identificam a demo gerenciada."
  }

  assert {
    condition = alltrue([
      contains(one([for statement in jsondecode(aws_iam_policy.automation_boundary.policy).Statement : statement.Action if statement.Sid == "DemoOperations"]), "apigateway:PUT"),
      contains(one([for statement in jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement : statement.Action if statement.Sid == "CreateAndReadOnlyRequiredControlPlaneResources"]), "apigateway:PUT"),
      length([for statement in jsondecode(aws_iam_policy.automation_boundary.policy).Statement : statement if statement.Sid == "ApiGwServiceRole" && statement.Condition.StringEquals["iam:AWSServiceName"] == "ops.apigateway.amazonaws.com"]) == 1,
      length([for statement in jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement : statement if statement.Sid == "ApiGwServiceRole" && statement.Condition.StringEquals["iam:AWSServiceName"] == "ops.apigateway.amazonaws.com"]) == 1,
      contains(one([for statement in jsondecode(aws_iam_policy.automation_boundary.policy).Statement : statement.Action if statement.Sid == "DemoOperations"]), "ecr:SetRepositoryPolicy"),
      contains(one([for statement in jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement : statement.Action if statement.Sid == "OperateConcreteEcrAndLambda"]), "ecr:SetRepositoryPolicy"),
      contains(one([for statement in jsondecode(aws_iam_policy.automation_boundary.policy).Statement : statement.Action if statement.Sid == "DemoOperations"]), "ecr:BatchCheckLayerAvailability"),
      contains(one([for statement in jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement : statement.Action if statement.Sid == "OperateConcreteEcrAndLambda"]), "ecr:BatchCheckLayerAvailability"),
      contains(one([for statement in jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement : statement.Action if statement.Sid == "OperateConcreteEcrAndLambda"]), "ecr:GetDownloadUrlForLayer"),
      contains(one([for statement in jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement : statement.Action if statement.Sid == "OperateConcreteDataAndRuntimeResources"]), "s3:ListTagsForResource"),
      toset(one([for statement in jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement : statement.Resource if statement.Sid == "OperateConcreteEcrAndLambda"])) == toset([local.demo_ecr_arn]),
    ])
    error_message = "As duas camadas devem permitir o protocolo de push ECR, mantendo a policy inline restrita ao repositório concreto da demo."
  }

  assert {
    condition = alltrue([
      for policy in [jsondecode(aws_iam_policy.automation_boundary.policy).Statement, jsondecode(aws_iam_role_policy.deploy_demo.policy).Statement] :
      length([for statement in policy : statement if statement.Sid == "EcrLifecycle"]) == 1 &&
      toset(one([for statement in policy : statement.Action if statement.Sid == "EcrLifecycle"])) == toset(["ecr:DeleteLifecyclePolicy"]) &&
      toset(one([for statement in policy : statement.Resource if statement.Sid == "EcrLifecycle"])) == toset([local.demo_ecr_arn]) &&
      length([for statement in policy : statement if statement.Sid == "DemoLogGroup"]) == 1 &&
      toset(one([for statement in policy : statement.Action if statement.Sid == "DemoLogGroup"])) == toset(["logs:DeleteLogGroup"]) &&
      toset(one([for statement in policy : statement.Resource if statement.Sid == "DemoLogGroup"])) == toset([local.demo_log_group_arn])
    ])
    error_message = "As duas camadas devem permitir os dois deletes evidenciados somente nos recursos concretos da demo."
  }
}
