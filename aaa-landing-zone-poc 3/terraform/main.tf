locals {
  environment_settings = {
    development = { log_retention = 30, access_tier = "developer", approved_regions = ["eu-west-1", "us-east-1"] }
    testing     = { log_retention = 90, access_tier = "tester", approved_regions = ["eu-west-1"] }
    production  = { log_retention = 365, access_tier = "read-only", approved_regions = ["eu-west-1"] }
  }
  settings = local.environment_settings[var.environment]
  common_tags = { ManagedBy = "Terraform", Organization = "AAA-Airlines", Environment = var.environment }
}

provider "aws" {
  region = var.aws_region
  assume_role { role_arn = "arn:aws:iam::${var.account_id}:role/${var.execution_role}" }
  default_tags { tags = local.common_tags }
}

module "account_baseline" {
  source = "./modules/account-baseline"
  namespace = var.namespace
  environment = var.environment
  log_retention = local.settings.log_retention
}

output "account_governance" {
  value = { account_id = var.account_id, environment = var.environment, access_tier = local.settings.access_tier, approved_regions = local.settings.approved_regions, retention_days = local.settings.log_retention }
}
