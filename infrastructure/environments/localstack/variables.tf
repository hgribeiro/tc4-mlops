variable "aws_region" {
  description = "Região sintética usada pelo LocalStack."
  type        = string
  default     = "us-east-1"
}

variable "localstack_endpoint" {
  description = "Endpoint exposto no host, sem alterar perfil ou credenciais AWS reais."
  type        = string
  default     = "http://localhost:4566"
}

variable "lambda_zip_path" {
  description = "ZIP local para transporte Lambda no LocalStack Community."
  type        = string
  nullable    = true
  default     = null
}
