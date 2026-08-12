variable "aws_region" {
  description = "AWS region for the temporary demo."
  type        = string
  default     = "us-east-1"
}

variable "commit_sha" {
  description = "Immutable Git commit SHA used by the ECR image and resource tags."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-f]{7,64}$", var.commit_sha))
    error_message = "commit_sha must be a hexadecimal Git SHA."
  }
}

variable "image_uri" {
  description = "Immutable ECR image URI. Leave null in the ECR/bootstrap stage."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition     = var.image_uri == null || (!strcontains(var.image_uri, ":latest") && can(regex("@[a-z0-9:]+$|:[0-9a-f]{7,64}$", var.image_uri)))
    error_message = "image_uri must use a digest or commit-SHA tag, never latest."
  }
}

variable "expires_at" {
  description = "RFC3339 expiry tag. Defaults to four hours from the initial apply."
  type        = string
  default     = null
  nullable    = true
}

variable "low_quota_mode" {
  description = "Temporary exception for an account at 10 Lambda concurrent executions: omit function reserved concurrency. Defaults to false, which reserves 2 executions."
  type        = bool
  default     = false
}
