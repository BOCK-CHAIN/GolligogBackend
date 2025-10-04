# AWS Deployment Guide

## Overview

This guide provides complete instructions for deploying the Golligog Search Engine on AWS infrastructure, including all components: backend API, SearXNG service, Flutter applications, and supporting services.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │ CloudFront  │ │     ALB     │ │    ECS      │ │   RDS  ││
│  │   (CDN)     │ │(Load Balancer)│ │  Fargate    │ │PostgreSQL││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │     S3      │ │    Route53  │ │   Lambda    │ │   ECR  ││
│  │ (Static)    │ │    (DNS)    │ │ (Functions) │ │(Docker)││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. AWS Account Setup

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: us-east-1
# Default output format: json
```

### 2. Required Tools Installation

```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER

# Install Node.js & npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Flutter
cd /tmp
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.13.0-stable.tar.xz
tar xf flutter_linux_3.13.0-stable.tar.xz
sudo mv flutter /opt/
echo 'export PATH="$PATH:/opt/flutter/bin"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Domain and SSL Prerequisites

- Register domain (e.g., golligog.com)
- Set up AWS Route 53 hosted zone
- Request SSL certificate via AWS Certificate Manager

## Infrastructure Setup with Terraform

### 1. Main Terraform Configuration

Create `infrastructure/main.tf`:

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "golligog.com"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "golligog-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "golligog-igw"
    Environment = var.environment
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "golligog-public-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = 2

  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "golligog-private-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "golligog-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name        = "golligog-nat-eip"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name        = "golligog-nat-gw"
    Environment = var.environment
  }

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name        = "golligog-private-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

data "aws_availability_zones" "available" {
  state = "available"
}
```

### 2. ECR Repositories

Create `infrastructure/ecr.tf`:

```hcl
# ECR Repository for Backend
resource "aws_ecr_repository" "backend" {
  name                 = "golligog-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "golligog-backend"
    Environment = var.environment
  }
}

# ECR Repository for SearXNG
resource "aws_ecr_repository" "searxng" {
  name                 = "golligog-searxng"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "golligog-searxng"
    Environment = var.environment
  }
}

# ECR Lifecycle Policies
resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "searxng" {
  repository = aws_ecr_repository.searxng.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
```

### 3. RDS Database

Create `infrastructure/rds.tf`:

```hcl
# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "golligog-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name        = "golligog-db-subnet-group"
    Environment = var.environment
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name_prefix = "golligog-rds-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "golligog-rds-sg"
    Environment = var.environment
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "golligog-db"

  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "golligog"
  username = "golligog_admin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name        = "golligog-db"
    Environment = var.environment
  }
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = "golligog/database-password"
  description = "Database password for Golligog"

  tags = {
    Name        = "golligog-db-password"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    password = random_password.db_password.result
    url      = "postgresql://${aws_db_instance.main.username}:${random_password.db_password.result}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
  })
}
```

### 4. ECS Cluster and Services

Create `infrastructure/ecs.tf`:

```hcl
# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "golligog-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "golligog-cluster"
    Environment = var.environment
  }
}

# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution" {
  name = "golligog-ecs-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role
resource "aws_iam_role" "ecs_task" {
  name = "golligog-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# ECS Security Group
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "golligog-ecs-tasks-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Backend API"
  }

  ingress {
    from_port       = 5001
    to_port         = 5001
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "SearXNG Proxy"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "golligog-ecs-tasks-sg"
    Environment = var.environment
  }
}

# Backend Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "golligog-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "golligog-backend"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NODE_ENV"
          value = "production"
        },
        {
          name  = "PORT"
          value = "5000"
        }
      ]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      essential = true
    }
  ])

  tags = {
    Name        = "golligog-backend-task"
    Environment = var.environment
  }
}

# SearXNG Task Definition
resource "aws_ecs_task_definition" "searxng" {
  family                   = "golligog-searxng"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "golligog-searxng"
      image = "${aws_ecr_repository.searxng.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 5001
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "FLASK_ENV"
          value = "production"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.searxng.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "golligog-searxng-task"
    Environment = var.environment
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/golligog-backend"
  retention_in_days = 14

  tags = {
    Name        = "golligog-backend-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "searxng" {
  name              = "/ecs/golligog-searxng"
  retention_in_days = 14

  tags = {
    Name        = "golligog-searxng-logs"
    Environment = var.environment
  }
}
```

### 5. Application Load Balancer

Create `infrastructure/alb.tf`:

```hcl
# ALB Security Group
resource "aws_security_group" "alb" {
  name_prefix = "golligog-alb-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "golligog-alb-sg"
    Environment = var.environment
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "golligog-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name        = "golligog-alb"
    Environment = var.environment
  }
}

# Target Groups
resource "aws_lb_target_group" "backend" {
  name        = "golligog-backend-tg"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }

  tags = {
    Name        = "golligog-backend-tg"
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "searxng" {
  name        = "golligog-searxng-tg"
  port        = 5001
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }

  tags = {
    Name        = "golligog-searxng-tg"
    Environment = var.environment
  }
}

# SSL Certificate
resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "golligog-ssl-cert"
    Environment = var.environment
  }
}

# ALB Listeners
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.main.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Listener Rules
resource "aws_lb_listener_rule" "searxng" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.searxng.arn
  }

  condition {
    host_header {
      values = ["search.${var.domain_name}"]
    }
  }
}
```

## Container Image Building and Deployment

### 1. Backend Docker Configuration

Create `server/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy package files
COPY package*.json ./
COPY prisma ./prisma/

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["npm", "start"]
```

### 2. SearXNG Proxy Docker Configuration

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY searxng_proxy.py .

# Create non-root user
RUN useradd -m -u 1001 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

# Start application
CMD ["python", "searxng_proxy.py"]
```

### 3. Build and Push Script

Create `scripts/build-and-deploy.sh`:

```bash
#!/bin/bash

set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Login to ECR
echo_info "Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push backend
echo_info "Building backend image..."
cd server
docker build -t golligog-backend .
docker tag golligog-backend:latest $ECR_REGISTRY/golligog-backend:latest

echo_info "Pushing backend image..."
docker push $ECR_REGISTRY/golligog-backend:latest

# Build and push SearXNG
echo_info "Building SearXNG image..."
cd ../backend
docker build -t golligog-searxng .
docker tag golligog-searxng:latest $ECR_REGISTRY/golligog-searxng:latest

echo_info "Pushing SearXNG image..."
docker push $ECR_REGISTRY/golligog-searxng:latest

# Update ECS services
echo_info "Updating ECS services..."
aws ecs update-service \
    --cluster golligog-cluster \
    --service golligog-backend-service \
    --force-new-deployment \
    --region $AWS_REGION

aws ecs update-service \
    --cluster golligog-cluster \
    --service golligog-searxng-service \
    --force-new-deployment \
    --region $AWS_REGION

echo_info "Deployment completed successfully!"
```

## Flutter App Deployment

### 1. Web App Deployment to S3/CloudFront

Create `infrastructure/s3-cloudfront.tf`:

```hcl
# S3 Bucket for Web App
resource "aws_s3_bucket" "web_app" {
  bucket = "golligog-web-app-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "golligog-web-app"
    Environment = var.environment
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_public_access_block" "web_app" {
  bucket = aws_s3_bucket.web_app.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "web_app" {
  bucket = aws_s3_bucket.web_app.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_policy" "web_app" {
  bucket = aws_s3_bucket.web_app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.web_app.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.web_app]
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "web_app" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.web_app.website_endpoint
    origin_id   = "S3-golligog-web-app"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  aliases = ["www.${var.domain_name}"]

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-golligog-web-app"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.main.arn
    ssl_support_method  = "sni-only"
  }

  tags = {
    Name        = "golligog-web-app-cdn"
    Environment = var.environment
  }
}
```

### 2. Flutter Web Build Script

Create `scripts/deploy-web.sh`:

```bash
#!/bin/bash

set -e

# Configuration
BUCKET_NAME=$(terraform output -raw web_app_bucket_name)
DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)

echo "Building Flutter web app..."
cd flutter/search_engine_app

# Configure production environment
echo 'const String API_BASE_URL = "https://api.golligog.com";' > lib/config/environment.dart
echo 'const String SEARXNG_URL = "https://search.golligog.com";' >> lib/config/environment.dart

# Build for web
flutter clean
flutter pub get
flutter build web --release \
  --dart-define=API_BASE_URL=https://api.golligog.com \
  --dart-define=SEARXNG_URL=https://search.golligog.com

echo "Uploading to S3..."
aws s3 sync build/web/ s3://$BUCKET_NAME --delete

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"

echo "Web app deployment completed!"
```

### 3. Mobile App Build Pipeline

Create `.github/workflows/mobile-build.yml`:

```yaml
name: Build Mobile Apps

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-android:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Java
      uses: actions/setup-java@v3
      with:
        distribution: 'zulu'
        java-version: '17'
        
    - name: Setup Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.13.0'
        
    - name: Install dependencies
      run: |
        cd flutter/search_engine_app
        flutter pub get
        
    - name: Configure signing
      run: |
        cd flutter/search_engine_app/android
        echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > app/keystore.jks
        echo "storePassword=${{ secrets.KEYSTORE_PASSWORD }}" > key.properties
        echo "keyPassword=${{ secrets.KEY_PASSWORD }}" >> key.properties
        echo "keyAlias=${{ secrets.KEY_ALIAS }}" >> key.properties
        echo "storeFile=keystore.jks" >> key.properties
        
    - name: Build APK
      run: |
        cd flutter/search_engine_app
        flutter build apk --release \
          --dart-define=API_BASE_URL=https://api.golligog.com \
          --dart-define=SEARXNG_URL=https://search.golligog.com
          
    - name: Build App Bundle
      run: |
        cd flutter/search_engine_app
        flutter build appbundle --release \
          --dart-define=API_BASE_URL=https://api.golligog.com \
          --dart-define=SEARXNG_URL=https://search.golligog.com
          
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: android-builds
        path: |
          flutter/search_engine_app/build/app/outputs/flutter-apk/
          flutter/search_engine_app/build/app/outputs/bundle/

  build-ios:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.13.0'
        
    - name: Install dependencies
      run: |
        cd flutter/search_engine_app
        flutter pub get
        
    - name: Build iOS
      run: |
        cd flutter/search_engine_app
        flutter build ios --release --no-codesign \
          --dart-define=API_BASE_URL=https://api.golligog.com \
          --dart-define=SEARXNG_URL=https://search.golligog.com
          
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ios-build
        path: flutter/search_engine_app/build/ios/iphoneos/
```

## Monitoring and Logging

### 1. CloudWatch Dashboard

Create `infrastructure/monitoring.tf`:

```hcl
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "Golligog-Monitoring"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "golligog-backend-service"],
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "golligog-backend-service"],
            ["AWS/ECS", "CPUUtilization", "ServiceName", "golligog-searxng-service"],
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "golligog-searxng-service"]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ECS Service Metrics"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.main.arn_suffix],
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Load Balancer Metrics"
        }
      }
    ]
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "golligog-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ecs cpu utilization"

  dimensions = {
    ServiceName = "golligog-backend-service"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "golligog-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ecs memory utilization"

  dimensions = {
    ServiceName = "golligog-backend-service"
  }
}
```

## Deployment Process

### 1. Infrastructure Deployment

```bash
# Initialize Terraform
cd infrastructure
terraform init

# Plan deployment
terraform plan -var="domain_name=your-domain.com"

# Apply infrastructure
terraform apply -var="domain_name=your-domain.com"
```

### 2. Application Deployment

```bash
# Make build script executable
chmod +x scripts/build-and-deploy.sh

# Deploy applications
./scripts/build-and-deploy.sh

# Deploy web app
chmod +x scripts/deploy-web.sh
./scripts/deploy-web.sh
```

### 3. DNS Configuration

```bash
# Get ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)

# Create Route 53 records
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_HOSTED_ZONE_ID \
  --change-batch file://dns-records.json
```

Create `dns-records.json`:

```json
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.golligog.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "ALB_DNS_NAME_HERE",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "ALB_HOSTED_ZONE_ID"
        }
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "search.golligog.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "ALB_DNS_NAME_HERE",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "ALB_HOSTED_ZONE_ID"
        }
      }
    }
  ]
}
```

## Cost Optimization

### 1. Resource Sizing

- **ECS Tasks**: Start with small sizes (0.25 vCPU, 512 MB)
- **RDS**: Use db.t3.micro for development, scale as needed
- **ALB**: Consider Network Load Balancer for lower costs

### 2. Cost Monitoring

```hcl
# Cost Budget
resource "aws_budgets_budget" "golligog" {
  name         = "golligog-monthly-budget"
  budget_type  = "COST"
  limit_amount = "50"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = ["Amazon Elastic Container Service", "Amazon Relational Database Service"]
  }
}
```

## Troubleshooting

### Common Issues

1. **ECS Service Won't Start**
   - Check CloudWatch logs
   - Verify security group rules
   - Ensure task definition is valid

2. **Database Connection Issues**
   - Check RDS security group
   - Verify connection string
   - Ensure database is accessible from ECS tasks

3. **Load Balancer Health Checks Failing**
   - Verify health check endpoint
   - Check application logs
   - Ensure proper port configuration

### Debug Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster golligog-cluster --services golligog-backend-service

# View CloudWatch logs
aws logs describe-log-streams --log-group-name /ecs/golligog-backend
aws logs get-log-events --log-group-name /ecs/golligog-backend --log-stream-name STREAM_NAME

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn TARGET_GROUP_ARN
```

This comprehensive deployment guide provides everything needed to deploy the Golligog Search Engine on AWS infrastructure with proper monitoring, logging, and cost optimization.
