terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "benedict_terraform_demo" {
  bucket = "benedict-geology-terraform-demo-8554"
  tags = {
    Name = "Benedict Terraform Demo"
    Project = "GeoDevOps-Day11"
  }
}
