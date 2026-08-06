terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }

  backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "codewhisper-pr"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}

data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

module "vpc" {
  source = "./modules/vpc"

  environment     = var.environment
  project_name    = var.project_name
  vpc_cidr        = var.vpc_cidr
  azs             = var.azs
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
}

module "eks" {
  source = "./modules/eks"

  environment             = var.environment
  project_name            = var.project_name
  vpc_id                  = module.vpc.vpc_id
  subnet_ids              = module.vpc.private_subnets
  node_groups             = var.node_groups
  cluster_version         = var.kubernetes_version
  additional_ingress_cidrs = var.allowed_ingress_cidrs
  tags                    = module.vpc.tags
}

module "rds" {
  source = "./modules/rds"

  environment       = var.environment
  project_name      = var.project_name
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnets
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password
  db_instance_class = var.db_instance_class
  db_engine_version = var.db_engine_version
  multi_az          = var.db_multi_az
  backup_retention  = var.db_backup_retention
}

module "alb" {
  source = "./modules/alb"

  environment   = var.environment
  project_name  = var.project_name
  vpc_id        = module.vpc.vpc_id
  subnet_ids    = module.vpc.public_subnets
  certificate_arn = var.certificate_arn
  allowed_cidrs = var.allowed_ingress_cidrs
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  value = module.eks.cluster_certificate_authority_data
}

output "db_endpoint" {
  value     = module.rds.db_endpoint
  sensitive = true
}

output "alb_dns_name" {
  value = module.alb.alb_dns_name
}
