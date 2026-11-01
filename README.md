# northstar-airlines-project

NorthStar Airlines is a Terraform-based infrastructure project focused on AWS multi-account governance and automated account provisioning with AWS Control Tower and Account Factory for Terraform (AFT).

## Overview

The project configures the AWS AFT module to support standardized account provisioning within an existing AWS Control Tower landing zone. It is intended as an Infrastructure as Code learning and portfolio project.

## Architecture

The configuration references the AWS Organizations management account, Log Archive account, Audit account, and AFT management account. AFT orchestrates account provisioning and customization workflows using Terraform.

## Prerequisites

- An existing AWS Control Tower landing zone and the required AWS accounts.
- Terraform and appropriately configured AWS credentials.
- AFT repositories and account identifiers configured for the target environment.

## Usage

```bash
terraform init
terraform validate
terraform plan
```




