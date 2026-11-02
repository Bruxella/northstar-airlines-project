variable "namespace" { type = string }
variable "environment" { type = string }
variable "log_retention" { type = number }

# Account-wide preventive baseline. Production deployment additionally
# requires org-level SCPs, AWS Config and Security Hub outside this module.
resource "aws_s3_account_public_access_block" "enforced" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_ebs_encryption_by_default" "enforced" { enabled = true }
resource "aws_cloudwatch_log_group" "governance" {
  name              = "/${var.namespace}/${var.environment}/governance"
  retention_in_days = var.log_retention
}
