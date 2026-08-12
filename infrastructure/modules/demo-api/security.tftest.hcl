mock_provider "aws" {}

variables {
  name_prefix     = "responsible-next-step-local"
  lambda_zip_path = "fixtures/lambda.zip"
  tags = {
    Environment = "localstack"
  }
}

override_resource {
  target = aws_iam_role.lambda[0]
  values = {
    arn = "arn:aws:iam::000000000000:role/responsible-next-step-local-lambda"
  }
}

override_resource {
  target = aws_api_gateway_rest_api.http[0]
  values = {
    execution_arn = "arn:aws:execute-api:us-east-1:000000000000:example"
  }
}

run "keeps_audit_private_and_encrypted" {
  command = plan

  assert {
    condition     = aws_s3_bucket_public_access_block.audit.block_public_acls && aws_s3_bucket_public_access_block.audit.block_public_policy && aws_s3_bucket_public_access_block.audit.ignore_public_acls && aws_s3_bucket_public_access_block.audit.restrict_public_buckets
    error_message = "O bucket de auditoria deve bloquear toda exposição pública."
  }

  assert {
    condition     = one([for rule in aws_s3_bucket_server_side_encryption_configuration.audit.rule : one([for encryption in rule.apply_server_side_encryption_by_default : encryption.sse_algorithm])]) == "AES256"
    error_message = "O bucket de auditoria deve usar criptografia server-side."
  }
}

run "uses_community_supported_rest_api_and_zip_lambda" {
  command = apply

  assert {
    condition     = aws_lambda_function.api[0].runtime == "python3.12" && aws_lambda_function.api[0].handler == "responsible_next_step.api.handler" && aws_lambda_function.api[0].timeout == 10
    error_message = "A API local deve usar o handler Mangum no transporte ZIP Python 3.12."
  }

  assert {
    condition     = aws_api_gateway_method.decision[0].http_method == "POST" && aws_api_gateway_resource.decisions[0].path_part == "decisions"
    error_message = "O contrato emulado deve expor POST /v1/decisions."
  }

  assert {
    condition     = strcontains(aws_iam_role_policy.audit_write[0].policy, "s3:PutObject") && strcontains(aws_iam_role_policy.audit_write[0].policy, "/decisions/*")
    error_message = "A role Lambda deve escrever somente o prefixo de auditoria."
  }
}
