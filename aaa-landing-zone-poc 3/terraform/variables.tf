variable "account_id" { type = string }
variable "environment" {
  type = string
  validation {
    condition = contains(["development", "testing", "production"], var.environment)
    error_message = "Unknown environment"
  }
}
variable "aws_region" { type = string, default = "eu-west-1" }
variable "execution_role" { type = string, default = "LandingZoneExecutionRole" }
variable "namespace" { type = string, default = "aaa" }
