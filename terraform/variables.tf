variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "db_username" {
  description = "Username for the RDS instance"
  type        = string
}

variable "db_password" {
  description = "Password for the RDS instance"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name for the RDS instance"
  type        = string
}