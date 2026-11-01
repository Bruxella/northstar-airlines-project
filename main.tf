provider "aws" {
  region 	= "us-east-1"
}

//Configure the Pipeline based on Terraform to create accounts to AWS Control Tower
module "aft_pipeline" {
  source = "github.com/aws-ia/terraform-aws-control_tower_account_factory"

  # Required Variables
  ct_management_account_id                         = "015561744800"
  log_archive_account_id                           = "143990330421"
  audit_account_id                                 = "876276749712"
  aft_management_account_id                        = "733438121387"
  ct_home_region                                   = "us-east-1"
  tf_backend_secondary_region                      = "us-west-2"

  # Terraform variables
  terraform_version                                = "1.6.0"
  terraform_distribution                           = "oss"

  # VCS Vars
  vcs_provider                                     = "github"
  account_request_repo_name                        = "{{Org}}/aft-account-request" //This is the folder where the Git Push will place the file for the account request
  global_customizations_repo_name                  = "{{Org}}/aft-global-customizations" //whatever we put in this folder, will change for all accounts
  account_customizations_repo_name                 = "{{Org}}/aft-account-customizations"
  account_provisioning_customizations_repo_name    = "{{Org}}/aft-account-provisioning-customizations"

  # AFT Feature flags
  aft_feature_cloudtrail_data_events               = false
  aft_feature_enterprise_support                   = false
  aft_feature_delete_default_vpcs_enabled          = true

  # AFT Additional Configurations
  aft_enable_vpc                                   = false
  backup_recovery_point_retention                  = 1
  log_archive_bucket_object_expiration_days        = 1
}