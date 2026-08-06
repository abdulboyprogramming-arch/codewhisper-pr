variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "codewhisper-pr"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "codewhisper"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "codewhisper"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.3"
}

variable "db_multi_az" {
  description = "Enable multi-AZ deployment"
  type        = bool
  default     = false
}

variable "db_backup_retention" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_groups" {
  description = "EKS node group configurations"
  type = list(object({
    name           = string
    instance_types = list(string)
    capacity       = string
    desired_size   = number
    min_size       = number
    max_size       = number
  }))
  default = [
    {
      name           = "primary"
      instance_types = ["t3.medium"]
      capacity       = "ON_DEMAND"
      desired_size   = 2
      min_size       = 1
      max_size       = 4
    }
  ]
}

variable "allowed_ingress_cidrs" {
  description = "Allowed ingress CIDR blocks"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}
