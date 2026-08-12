variable "name_prefix" {
  description = "Prefixo estável dos recursos temporários da API de Demonstração."
  type        = string
}

variable "lambda_zip_path" {
  description = "Caminho local do ZIP Python 3.12 com FastAPI, Mangum e dependências. Nulo cria somente o bucket de auditoria."
  type        = string
  nullable    = true
  default     = null
}

variable "audit_prefix" {
  description = "Prefixo privado dos objetos de auditoria minimizada."
  type        = string
  default     = "decisions"
}

variable "force_destroy_audit_bucket" {
  description = "Permite apagar objetos sintéticos durante o cleanup local; mantenha falso em ambientes AWS."
  type        = bool
  default     = false
}

variable "localstack_endpoint_url" {
  description = "Endpoint que o runtime Lambda local usa para acessar o LocalStack."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags comuns exigidas pela configuração compartilhada."
  type        = map(string)
  default     = {}
}
