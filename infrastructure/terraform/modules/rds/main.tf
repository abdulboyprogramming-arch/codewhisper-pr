variable "environment" { type = string }
variable "project_name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "db_name" { type = string }
variable "db_username" { type = string }
variable "db_password" { type = string }
variable "db_instance_class" { type = string }
variable "db_engine_version" { type = string }
variable "multi_az" { type = bool }
variable "backup_retention" { type = number }

locals {
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

output "db_endpoint" { value = aws_db_instance.main.endpoint }
output "db_name" { value = aws_db_instance.main.db_name }

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet"
  subnet_ids = var.subnet_ids

  tags = local.tags
}

resource "aws_security_group" "db" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "RDS security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.cluster.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-${var.environment}-db"
  engine         = "postgres"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class
  db_name        = var.db_name
  username       = var.db_username
  password       = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = var.backup_retention
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:05:00-sun:06:00"

  multi_az                = var.multi_az
  storage_encrypted       = true
  storage_type            = "gp3"
  allocated_storage       = 20
  max_allocated_storage   = 100

  skip_final_snapshot       = true
  deletion_protection       = false
  publicly_accessable       = false
  enabled_cloudwatch_logs_export = ["postgresql"]

  tags = local.tags
}
