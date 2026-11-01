# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
module "dev_account_01" {
  source = "./modules/aft-account-request" #must have done first the pull from 'aft-account-request' repo'

  control_tower_parameters = {
    AccountEmail = "dev@northstar-airlines.com"
    AccountName  = "northstart-account-dev"
    # Syntax for top-level OU
    ManagedOrganizationalUnit = "Workloads/Dev"
    # Syntax for nested OU
    # ManagedOrganizationalUnit = "Sandbox (ou-xfe5-a8hb8ml8)"
    SSOUserEmail     = "dev@northstar-airlines.com"
    SSOUserFirstName = "John"
    SSOUserLastName  = "Smith"
  }

}