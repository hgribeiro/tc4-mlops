variable "aws_region" {
  description = "Região do backend persistente e das identidades de automação."
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}(-gov)?-[a-z]+-[0-9]+$", var.aws_region))
    error_message = "aws_region deve ser uma região AWS válida, como us-east-1 ou sa-east-1."
  }
}

variable "state_bucket_name" {
  description = "Nome globalmente único do bucket S3 persistente de state; inclua a conta e um sufixo não secreto."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.state_bucket_name)) && !can(regex("[.]", var.state_bucket_name))
    error_message = "state_bucket_name deve ter 3-63 caracteres, somente minúsculas, números e hífens, sem pontos."
  }
}

variable "state_key" {
  description = "Chave imutável do state do bootstrap; a demo terá backend e state próprios em uma issue posterior."
  type        = string
  default     = "bootstrap/terraform.tfstate"

  validation {
    condition     = var.state_key == "bootstrap/terraform.tfstate"
    error_message = "O bootstrap usa somente a chave bootstrap/terraform.tfstate para evitar mistura com state da demo."
  }
}
