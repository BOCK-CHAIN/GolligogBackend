# AWS Deployment Guide
## Complete Deployment of Golligog Search Engine

### Table of Contents
1. [Overview](#overview)
2. [AWS Architecture](#aws-architecture)
3. [Prerequisites](#prerequisites)
4. [Backend Deployment](#backend-deployment)
5. [SearXNG Deployment](#searxng-deployment)
6. [Flutter App Deployment](#flutter-app-deployment)
7. [Database Setup](#database-setup)
8. [Domain & SSL Configuration](#domain--ssl-configuration)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Monitoring & Logging](#monitoring--logging)
11. [Cost Optimization](#cost-optimization)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the complete deployment of the Golligog Search Engine on AWS, including:
- **Backend API** (Node.js/Express with Prisma)
- **SearXNG Search Service** (Python Flask proxy)
- **Flutter Applications** (Android, iOS, Web, Desktop)
- **Database** (PostgreSQL on AWS RDS)
- **Infrastructure** (Load balancers, auto-scaling, monitoring)

### Architecture Components
```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │ CloudFront  │ │     ALB     │ │    EC2      │ │   RDS  ││
│  │   (CDN)     │ │(Load Balancer)│ │  Instances  │ │PostgreSQL││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │     S3      │ │    Route53  │ │   Lambda    │ │   ECR  ││
│  │ (Static)    │ │    (DNS)    │ │ (Functions) │ │(Docker)││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## AWS Architecture

### Production Architecture
```
Internet
    │
    ▼
┌─────────────────┐
│   CloudFront    │ ◄─── CDN for Flutter Web App
│   Distribution  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Route 53      │ ◄─── DNS Management
│   (DNS)         │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Application     │ ◄─── Load Balancer
│ Load Balancer   │
└─────────────────┘
    │
    ├─────────────────────┬─────────────────────┐
    ▼                     ▼                     ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   EC2 AZ-1  │  │   EC2 AZ-2  │  │   EC2 AZ-3  │
│ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │
│ │Node.js  │ │  │ │Node.js  │ │  │ │Node.js  │ │
│ │Backend  │ │  │ │Backend  │ │  │ │Backend  │ │
│ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │
│ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │
│ │SearXNG  │ │  │ │SearXNG  │ │  │ │SearXNG  │ │
│ │Service  │ │  │ │Service  │ │  │ │Service  │ │
│ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │
└─────────────┘  └─────────────┘  └─────────────┘
    │                     │                     │
    └─────────────────────┼─────────────────────┘
                          ▼
                  ┌─────────────┐
                  │   RDS       │
                  │ PostgreSQL  │
                  │ Multi-AZ    │
                  └─────────────┘
```

---

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

### 2. Required Tools
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

# Install Flutter (for building apps)
cd /tmp
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.13.0-stable.tar.xz
tar xf flutter_linux_3.13.0-stable.tar.xz
sudo mv flutter /opt/
echo 'export PATH="$PATH:/opt/flutter/bin"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Domain & SSL Prerequisites
- Register a domain (e.g., golligog.com)
- AWS Route 53 hosted zone
- SSL certificate via AWS Certificate Manager

---

## Backend Deployment

### 1. Dockerize Node.js Backend

Create `server/Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY prisma ./prisma/

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["npm", "start"]
```

Create `server/.dockerignore`:
```
node_modules
npm-debug.log
.env
.git
.gitignore
README.md
Dockerfile
.dockerignore
```

### 2. Build and Push to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name golligog-backend --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
cd /home/kali/search_engine/server
docker build -t golligog-backend .
docker tag golligog-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/golligog-backend:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/golligog-backend:latest
```

### 3. ECS Service Configuration

Create `infrastructure/backend-task-definition.json`:
```json
{
  "family": "golligog-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "golligog-backend",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/golligog-backend:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "PORT",
          "value": "5000"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:golligog/database-url"
        },
        {
          "name": "JWT_SECRET",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:golligog/jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/golligog-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

---

## SearXNG Deployment

### 1. Dockerize SearXNG Service

Create `backend/Dockerfile` for SearXNG proxy:
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

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

# Start application
CMD ["python", "searxng_proxy.py"]
```

Create `backend/requirements.txt`:
```
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

### 2. Deploy SearXNG Service

```bash
# Build and push SearXNG service
cd /home/kali/search_engine/backend

# Create ECR repository
aws ecr create-repository --repository-name golligog-searxng --region us-east-1

# Build and push
docker build -t golligog-searxng .
docker tag golligog-searxng:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/golligog-searxng:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/golligog-searxng:latest
```

### 3. SearXNG Task Definition

Create `infrastructure/searxng-task-definition.json`:
```json
{
  "family": "golligog-searxng",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "golligog-searxng",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/golligog-searxng:latest",
      "portMappings": [
        {
          "containerPort": 5001,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        },
        {
          "name": "SEARXNG_URL",
          "value": "http://searxng-internal:8080"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/golligog-searxng",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## Flutter App Deployment

### 1. Android App Deployment

#### Build Android APK/Bundle
```bash
cd /home/kali/search_engine/flutter/search_engine_app

# Configure environment
echo 'const String API_BASE_URL = "https://api.golligog.com";' > lib/config.dart
echo 'const String SEARXNG_URL = "https://search.golligog.com";' >> lib/config.dart

# Build release APK
flutter build apk --release

# Build App Bundle for Play Store
flutter build appbundle --release

# Files will be in:
# build/app/outputs/flutter-apk/app-release.apk
# build/app/outputs/bundle/release/app-release.aab
```

#### Google Play Store Deployment
```bash
# Create upload keystore (one-time setup)
keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload

# Configure signing in android/app/build.gradle
# Add to android/key.properties:
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=upload
storeFile=../upload-keystore.jks

# Upload to Google Play Console
# 1. Create app listing
# 2. Upload app-release.aab
# 3. Configure app details, screenshots, descriptions
# 4. Submit for review
```

### 2. iOS App Deployment

#### Build iOS App
```bash
cd /home/kali/search_engine/flutter/search_engine_app

# Note: iOS builds require macOS with Xcode
# If on Linux, use CI/CD or GitHub Actions with macOS runner

# Build iOS app (on macOS)
flutter build ios --release

# Archive for App Store (on macOS with Xcode)
# 1. Open ios/Runner.xcworkspace in Xcode
# 2. Select "Generic iOS Device"
# 3. Product → Archive
# 4. Upload to App Store Connect
```

#### GitHub Actions for iOS Build
Create `.github/workflows/ios-build.yml`:
```yaml
name: Build iOS App

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build_ios:
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
        flutter build ios --release --no-codesign
        
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ios-build
        path: flutter/search_engine_app/build/ios/iphoneos/
```

### 3. Web App Deployment

#### Build Flutter Web
```bash
cd /home/kali/search_engine/flutter/search_engine_app

# Build for web
flutter build web --release

# Files will be in build/web/
```

#### Deploy to AWS S3 + CloudFront
```bash
# Create S3 bucket for web app
aws s3 mb s3://golligog-web-app

# Enable static website hosting
aws s3 website s3://golligog-web-app --index-document index.html --error-document index.html

# Upload web files
aws s3 sync build/web/ s3://golligog-web-app --delete

# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config file://infrastructure/cloudfront-config.json
```

Create `infrastructure/cloudfront-config.json`:
```json
{
  "CallerReference": "golligog-web-app-2024",
  "Comment": "Golligog Flutter Web App",
  "DefaultCacheBehavior": {
    "TargetOriginId": "golligog-s3-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "MinTTL": 0,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "Compress": true
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "golligog-s3-origin",
        "DomainName": "golligog-web-app.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
```

### 4. Desktop App Distribution

#### Windows
```bash
# Build Windows app (on Windows or using CI/CD)
flutter build windows --release

# Create installer using Inno Setup or Advanced Installer
# Package and distribute through Microsoft Store or direct download
```

#### Linux
```bash
# Build Linux app
flutter build linux --release

# Create AppImage or Snap package
# Distribute through Snap Store or direct download
```

#### macOS
```bash
# Build macOS app (on macOS)
flutter build macos --release

# Code sign and notarize
# Distribute through Mac App Store or direct download
```

---

## Database Setup

### 1. RDS PostgreSQL Setup

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier golligog-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username golligog_admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-12345678 \
  --db-subnet-group-name golligog-db-subnet-group \
  --backup-retention-period 7 \
  --multi-az false \
  --storage-encrypted true
```

### 2. Database Migration

Create `server/scripts/deploy-db.js`:
```javascript
const { PrismaClient } = require('@prisma/client');

async function deployDatabase() {
  const prisma = new PrismaClient();
  
  try {
    console.log('Running database migrations...');
    
    // This will be handled by Prisma migrate in production
    // Run: npx prisma migrate deploy
    
    console.log('Database deployment completed');
  } catch (error) {
    console.error('Database deployment failed:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

deployDatabase();
```

### 3. Secrets Management

```bash
# Store database URL in AWS Secrets Manager
aws secretsmanager create-secret \
  --name golligog/database-url \
  --description "Database connection string for Golligog" \
  --secret-string "postgresql://golligog_admin:YOUR_PASSWORD@golligog-db.region.rds.amazonaws.com:5432/golligog"

# Store JWT secret
aws secretsmanager create-secret \
  --name golligog/jwt-secret \
  --description "JWT signing secret for Golligog" \
  --secret-string "your-super-secure-jwt-secret-key"
```

---

## Domain & SSL Configuration

### 1. Route 53 Setup

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name golligog.com \
  --caller-reference golligog-2024

# Get name servers and update domain registrar
aws route53 get-hosted-zone --id /hostedzone/YOUR_ZONE_ID
```

### 2. SSL Certificate

```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name golligog.com \
  --subject-alternative-names "*.golligog.com" \
  --validation-method DNS \
  --region us-east-1

# Note: Verify domain ownership via DNS
```

### 3. Load Balancer Configuration

Create `infrastructure/alb-target-groups.json`:
```json
{
  "backend": {
    "Name": "golligog-backend-tg",
    "Protocol": "HTTP",
    "Port": 5000,
    "VpcId": "vpc-12345678",
    "HealthCheckPath": "/health",
    "HealthCheckIntervalSeconds": 30,
    "HealthyThresholdCount": 2,
    "UnhealthyThresholdCount": 3,
    "TargetType": "ip"
  },
  "searxng": {
    "Name": "golligog-searxng-tg", 
    "Protocol": "HTTP",
    "Port": 5001,
    "VpcId": "vpc-12345678",
    "HealthCheckPath": "/health",
    "TargetType": "ip"
  }
}
```

---

## CI/CD Pipeline

### 1. GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

env:
  AWS_REGION: us-east-1
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
        
    - name: Login to Amazon ECR
      uses: aws-actions/amazon-ecr-login@v1
      
    - name: Build backend image
      run: |
        cd server
        docker build -t golligog-backend .
        docker tag golligog-backend:latest $ECR_REGISTRY/golligog-backend:latest
        
    - name: Push backend image
      run: |
        docker push $ECR_REGISTRY/golligog-backend:latest
        
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster golligog-cluster \
          --service golligog-backend-service \
          --force-new-deployment

  deploy-searxng:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
        
    - name: Build and deploy SearXNG
      run: |
        cd backend
        docker build -t golligog-searxng .
        docker tag golligog-searxng:latest $ECR_REGISTRY/golligog-searxng:latest
        docker push $ECR_REGISTRY/golligog-searxng:latest
        
        aws ecs update-service \
          --cluster golligog-cluster \
          --service golligog-searxng-service \
          --force-new-deployment

  deploy-web:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.13.0'
        
    - name: Build Flutter web
      run: |
        cd flutter/search_engine_app
        flutter pub get
        flutter build web --release
        
    - name: Deploy to S3
      run: |
        aws s3 sync flutter/search_engine_app/build/web/ s3://golligog-web-app --delete
        
    - name: Invalidate CloudFront
      run: |
        aws cloudfront create-invalidation \
          --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
          --paths "/*"

  build-android:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.13.0'
        
    - name: Setup Java
      uses: actions/setup-java@v3
      with:
        distribution: 'zulu'
        java-version: '17'
        
    - name: Build Android APK
      run: |
        cd flutter/search_engine_app
        flutter pub get
        flutter build apk --release
        flutter build appbundle --release
        
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: android-builds
        path: |
          flutter/search_engine_app/build/app/outputs/flutter-apk/
          flutter/search_engine_app/build/app/outputs/bundle/
```

---

## Monitoring & Logging

### 1. CloudWatch Setup

```bash
# Create log groups
aws logs create-log-group --log-group-name /ecs/golligog-backend
aws logs create-log-group --log-group-name /ecs/golligog-searxng

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "Golligog-Monitoring" \
  --dashboard-body file://infrastructure/dashboard-config.json
```

### 2. Application Monitoring

Add to `server/middleware/monitoring.js`:
```javascript
const express = require('express');
const AWS = require('aws-sdk');

const cloudwatch = new AWS.CloudWatch();

const monitoringMiddleware = express.Router();

// Request metrics
monitoringMiddleware.use((req, res, next) => {
  const startTime = Date.now();
  
  res.on('finish', () => {
    const responseTime = Date.now() - startTime;
    
    // Send metrics to CloudWatch
    const params = {
      Namespace: 'Golligog/API',
      MetricData: [
        {
          MetricName: 'ResponseTime',
          Value: responseTime,
          Unit: 'Milliseconds',
          Dimensions: [
            {
              Name: 'Endpoint',
              Value: req.path
            }
          ]
        },
        {
          MetricName: 'RequestCount',
          Value: 1,
          Unit: 'Count',
          Dimensions: [
            {
              Name: 'StatusCode',
              Value: res.statusCode.toString()
            }
          ]
        }
      ]
    };
    
    cloudwatch.putMetricData(params).promise()
      .catch(err => console.error('Failed to send metrics:', err));
  });
  
  next();
});

module.exports = monitoringMiddleware;
```

### 3. Health Checks

Add to `server/routes/health.js`:
```javascript
const express = require('express');
const { PrismaClient } = require('@prisma/client');

const router = express.Router();
const prisma = new PrismaClient();

router.get('/health', async (req, res) => {
  try {
    // Check database connection
    await prisma.$queryRaw`SELECT 1`;
    
    // Check external services
    const searxngResponse = await fetch(process.env.SEARXNG_URL + '/health')
      .catch(() => ({ ok: false }));
    
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'healthy',
        searxng: searxngResponse.ok ? 'healthy' : 'unhealthy'
      }
    };
    
    res.status(200).json(health);
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
```

---

## Flutter App Connection Configuration

### 1. Environment Configuration

Create `flutter/search_engine_app/lib/config/app_config.dart`:
```dart
class AppConfig {
  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://api.golligog.com',
  );
  
  static const String _searxngUrl = String.fromEnvironment(
    'SEARXNG_URL', 
    defaultValue: 'https://search.golligog.com',
  );
  
  // API Endpoints
  static const String apiBaseUrl = _baseUrl;
  static const String authEndpoint = '$_baseUrl/api/auth';
  static const String userEndpoint = '$_baseUrl/api/user';
  static const String searchEndpoint = '$_searxngUrl/api/search';
  
  // App Configuration
  static const String appName = 'Golligog';
  static const String appVersion = '1.0.0';
  
  // Timeouts
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration connectTimeout = Duration(seconds: 10);
  
  // Environment Detection
  static bool get isProduction => _baseUrl.contains('golligog.com');
  static bool get isDevelopment => !isProduction;
}
```

### 2. HTTP Client Configuration

Update `flutter/search_engine_app/lib/services/http_client.dart`:
```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../config/app_config.dart';

class HttpClient {
  static final HttpClient _instance = HttpClient._internal();
  factory HttpClient() => _instance;
  HttpClient._internal();

  late http.Client _client;
  
  void initialize() {
    _client = http.Client();
  }

  Future<http.Response> get(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, String>? queryParams,
  }) async {
    final uri = _buildUri(endpoint, queryParams);
    final finalHeaders = _buildHeaders(headers);
    
    try {
      final response = await _client
          .get(uri, headers: finalHeaders)
          .timeout(AppConfig.apiTimeout);
      
      _logRequest('GET', uri, response.statusCode);
      return response;
    } catch (e) {
      _logError('GET', uri, e);
      rethrow;
    }
  }

  Future<http.Response> post(
    String endpoint, {
    Map<String, String>? headers,
    dynamic body,
  }) async {
    final uri = _buildUri(endpoint);
    final finalHeaders = _buildHeaders(headers);
    
    try {
      final response = await _client
          .post(uri, headers: finalHeaders, body: body)
          .timeout(AppConfig.apiTimeout);
      
      _logRequest('POST', uri, response.statusCode);
      return response;
    } catch (e) {
      _logError('POST', uri, e);
      rethrow;
    }
  }

  Uri _buildUri(String endpoint, [Map<String, String>? queryParams]) {
    final baseUrl = endpoint.startsWith('http') 
        ? endpoint 
        : '${AppConfig.apiBaseUrl}$endpoint';
    
    final uri = Uri.parse(baseUrl);
    
    if (queryParams != null && queryParams.isNotEmpty) {
      return uri.replace(queryParameters: {
        ...uri.queryParameters,
        ...queryParams,
      });
    }
    
    return uri;
  }

  Map<String, String> _buildHeaders(Map<String, String>? customHeaders) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'Golligog-Flutter/${AppConfig.appVersion}',
    };
    
    if (customHeaders != null) {
      headers.addAll(customHeaders);
    }
    
    return headers;
  }

  void _logRequest(String method, Uri uri, int statusCode) {
    if (kDebugMode) {
      print('[$method] $uri -> $statusCode');
    }
  }

  void _logError(String method, Uri uri, dynamic error) {
    if (kDebugMode) {
      print('[$method] $uri -> ERROR: $error');
    }
  }

  void dispose() {
    _client.close();
  }
}
```

### 3. Service Integration

Update `flutter/search_engine_app/lib/services/auth_service.dart`:
```dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';
import 'http_client.dart';

class AuthService extends ChangeNotifier {
  final HttpClient _httpClient = HttpClient();
  
  String? _token;
  Map<String, dynamic>? _userData;
  bool _isLoading = false;

  // Getters
  String? get token => _token;
  Map<String, dynamic>? get userData => _userData;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _token != null && _userData != null;

  Future<bool> loginUser({
    required String email,
    required String password,
  }) async {
    _setLoading(true);
    
    try {
      final response = await _httpClient.post(
        '/auth/login',
        body: jsonEncode({
          'email': email.trim().toLowerCase(),
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _token = data['token'];
        _userData = data['user'];
        
        await _storeAuthData();
        _setLoading(false);
        return true;
      } else {
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setLoading(false);
      debugPrint('Login error: $e');
      return false;
    }
  }

  Future<void> _storeAuthData() async {
    final prefs = await SharedPreferences.getInstance();
    if (_token != null) {
      await prefs.setString('auth_token', _token!);
    }
    if (_userData != null) {
      await prefs.setString('user_data', jsonEncode(_userData!));
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
}
```

### 4. Network Error Handling

Create `flutter/search_engine_app/lib/utils/network_utils.dart`:
```dart
import 'dart:io';
import 'package:flutter/material.dart';

class NetworkUtils {
  static bool isNetworkError(dynamic error) {
    return error is SocketException ||
           error is HttpException ||
           error.toString().contains('SocketException') ||
           error.toString().contains('Failed host lookup');
  }

  static String getErrorMessage(dynamic error) {
    if (error is SocketException || error.toString().contains('SocketException')) {
      return 'No internet connection. Please check your network and try again.';
    }
    
    if (error is HttpException) {
      return 'Server error. Please try again later.';
    }
    
    if (error.toString().contains('TimeoutException')) {
      return 'Request timed out. Please try again.';
    }
    
    return 'An unexpected error occurred. Please try again.';
  }

  static void showNetworkError(BuildContext context, dynamic error) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(getErrorMessage(error)),
        backgroundColor: Colors.red,
        action: SnackBarAction(
          label: 'Retry',
          textColor: Colors.white,
          onPressed: () {
            // Implement retry logic
          },
        ),
      ),
    );
  }
}
```

---

## Cost Optimization

### 1. Resource Sizing
```bash
# Use appropriate instance sizes
# Development: t3.micro ($8/month)
# Production: t3.small ($17/month) or t3.medium ($33/month)

# Auto Scaling configuration
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name golligog-asg \
  --min-size 1 \
  --max-size 3 \
  --desired-capacity 1 \
  --target-group-arns arn:aws:elasticloadbalancing:us-east-1:account:targetgroup/...
```

### 2. Cost Monitoring
```bash
# Set up billing alerts
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://infrastructure/budget-config.json
```

### 3. Resource Cleanup Scripts
Create `scripts/cleanup-resources.sh`:
```bash
#!/bin/bash

# Stop unused services
aws ecs update-service --cluster golligog-cluster --service golligog-backend-service --desired-count 0

# Delete old ECR images
aws ecr list-images --repository-name golligog-backend --filter tagStatus=UNTAGGED \
  --query 'imageIds[?imageDigest!=null]' --output json | \
  aws ecr batch-delete-image --repository-name golligog-backend --image-ids file:///dev/stdin

echo "Cleanup completed"
```

---

## Troubleshooting

### 1. Common Issues

#### Connection Issues
```bash
# Test connectivity
curl -I https://api.golligog.com/health
curl -I https://search.golligog.com/health

# Check DNS resolution
nslookup api.golligog.com
nslookup search.golligog.com

# Test from Flutter app
flutter run --debug
# Check logs for connection errors
```

#### Authentication Issues
```bash
# Verify JWT token
echo "YOUR_JWT_TOKEN" | base64 -d

# Check database connection
psql -h golligog-db.region.rds.amazonaws.com -U golligog_admin -d golligog

# Test API endpoints
curl -X POST https://api.golligog.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### 2. Monitoring Commands
```bash
# Check ECS service status
aws ecs describe-services --cluster golligog-cluster --services golligog-backend-service

# View logs
aws logs get-log-events --log-group-name /ecs/golligog-backend --log-stream-name ecs/golligog-backend/...

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=golligog-backend-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average
```

### 3. Rollback Procedures
```bash
# Rollback ECS service
aws ecs update-service \
  --cluster golligog-cluster \
  --service golligog-backend-service \
  --task-definition golligog-backend:PREVIOUS_REVISION

# Rollback web app
aws s3 sync s3://golligog-web-app-backup/ s3://golligog-web-app --delete
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

---

## Estimated Monthly Costs

### Development Environment
- **EC2 t3.micro**: $8/month
- **RDS t3.micro**: $15/month  
- **S3 Storage**: $1/month
- **CloudFront**: $1/month
- **Route 53**: $0.50/month
- **Total**: ~$25/month

### Production Environment
- **ECS Fargate**: $30/month
- **RDS t3.small**: $25/month
- **ALB**: $22/month
- **S3 + CloudFront**: $5/month
- **Route 53**: $0.50/month
- **Secrets Manager**: $1/month
- **CloudWatch**: $3/month
- **Total**: ~$86/month

---

This comprehensive deployment guide covers all aspects of deploying your Golligog search engine to AWS, from backend services to mobile apps across all platforms. Follow the sections relevant to your deployment needs and customize the configurations based on your specific requirements.
