# 🚀 Customer Categorizer - Deployment Guide

Complete guide for deploying the Customer Categorizer ML application across multiple platforms.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Docker Compose](#docker-compose)
5. [AWS EC2 + Nginx](#aws-ec2--nginx)
6. [AWS ECS](#aws-ecs)
7. [Kubernetes](#kubernetes)
8. [AWS Lambda](#aws-lambda)
9. [GitHub Actions CI/CD](#github-actions-cicd)
10. [Monitoring & Logging](#monitoring--logging)
11. [Troubleshooting](#troubleshooting)
12. [Security Best Practices](#security-best-practices)

---

## Prerequisites

### Required Tools
- Docker & Docker Compose
- Git
- AWS CLI (for AWS deployments)
- kubectl (for Kubernetes)
- Python 3.8+

### Required Accounts
- MongoDB Atlas (or local MongoDB)
- AWS Account (optional, for cloud deployment)
- Docker Hub Account (optional, for image registry)

### Environment Variables
Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Fill in your credentials:
```env
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/database
```

---

## 1️⃣ Local Development

### Setup Virtual Environment
```bash
# Clone repository
git clone https://github.com/namanx815/Customer_Categorizer.git
cd Customer_Categorizer

# Create virtual environment
python -m venv venv

# Activate environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Application
```bash
# Set environment variables
export MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/database
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Run application
python app.py
```

### Access Application
- Web UI: http://localhost:5000
- Health Check: http://localhost:5000/health
- API Docs: http://localhost:5000/docs

### Deactivate Environment
```bash
deactivate
```

---

## 2️⃣ Docker Deployment

### Build Docker Image
```bash
# Build image
docker build -t customer-categorizer:latest .

# Build with build arguments
docker build \
  --build-arg AWS_ACCESS_KEY_ID=your_key \
  --build-arg AWS_SECRET_ACCESS_KEY=your_secret \
  -t customer-categorizer:latest .
```

### Run Container
```bash
# Run with environment variables
docker run -d \
  -p 5000:5000 \
  -e MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/database \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  --name customer_categorizer \
  customer-categorizer:latest

# Verify container is running
docker ps

# View logs
docker logs -f customer_categorizer

# Check health
curl http://localhost:5000/health
```

### Stop Container
```bash
docker stop customer_categorizer
docker rm customer_categorizer
```

### Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Tag image
docker tag customer-categorizer:latest your_username/customer-categorizer:latest

# Push image
docker push your_username/customer-categorizer:latest
```

---

## 3️⃣ Docker Compose

### Quick Start (3 commands)
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your credentials
nano .env

# 3. Start services
docker-compose up -d
```

### Verify Services
```bash
# Check running services
docker-compose ps

# Check API health
curl http://localhost:5000/health

# View application logs
docker-compose logs -f api

# View MongoDB logs
docker-compose logs -f mongo
```

### Useful Commands
```bash
# Stop services (keeps data)
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart api

# Remove services (deletes volumes)
docker-compose down -v

# Execute command in container
docker-compose exec api python -c "import pandas; print(pandas.__version__)"

# Scale services
docker-compose up -d --scale api=3
```

### Access Services
- API: http://localhost:5000
- Health Check: http://localhost:5000/health
- MongoDB: mongodb://admin:password@localhost:27017
- API Docs: http://localhost:5000/docs

---

## 4️⃣ AWS EC2 + Nginx

### 1. Launch EC2 Instance
```bash
# Launch Ubuntu 20.04 instance
# Instance type: t3.medium (2 CPU, 4GB RAM)
# Security group: Allow ports 22, 80, 443

# SSH into instance
ssh -i your_key.pem ubuntu@your_instance_ip
```

### 2. Install Dependencies
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Nginx
sudo apt-get install -y nginx

# Install git
sudo apt-get install -y git
```

### 3. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/namanx815/Customer_Categorizer.git
sudo chown -R ubuntu:ubuntu Customer_Categorizer
cd Customer_Categorizer
```

### 4. Configure Environment
```bash
cp .env.example .env
nano .env  # Add your credentials
```

### 5. Start Application
```bash
docker-compose up -d
docker-compose logs -f api
```

### 6. Configure Nginx Reverse Proxy
```bash
sudo nano /etc/nginx/sites-available/customer-categorizer
```

Paste this configuration:
```nginx
upstream api_backend {
    server localhost:5000;
}

server {
    listen 80;
    server_name your_domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /opt/Customer_Categorizer/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 7. Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/customer-categorizer /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 8. Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your_domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 9. Setup Auto-Start on Reboot
```bash
# Create systemd service
sudo nano /etc/systemd/system/customer-categorizer.service
```

Paste this:
```ini
[Unit]
Description=Customer Categorizer API
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/opt/Customer_Categorizer
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable customer-categorizer
sudo systemctl start customer-categorizer
```

### 10. Monitor Application
```bash
# View logs
docker-compose logs -f api

# Check health
curl https://your_domain.com/health

# Monitor system resources
docker stats

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 5️⃣ AWS ECS

### 1. Create ECR Repository
```bash
aws ecr create-repository --repository-name customer-categorizer --region us-east-1
```

### 2. Push Image to ECR
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t customer-categorizer:latest .
docker tag customer-categorizer:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/customer-categorizer:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/customer-categorizer:latest
```

### 3. Create Task Definition
```bash
# Create file: ecs-task-definition.json
{
  "family": "customer-categorizer",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "customer-categorizer",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/customer-categorizer:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MONGODB_URL",
          "value": "mongodb+srv://user:pass@cluster.mongodb.net/database"
        }
      ],
      "secrets": [
        {
          "name": "AWS_ACCESS_KEY_ID",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:customer-categorizer-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/customer-categorizer",
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

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

### 4. Create ECS Service
```bash
aws ecs create-service \
  --cluster customer-categorizer \
  --service-name customer-categorizer-service \
  --task-definition customer-categorizer \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=customer-categorizer,containerPort=5000
```

### 5. Monitor Service
```bash
# View services
aws ecs list-services --cluster customer-categorizer

# Describe service
aws ecs describe-services --cluster customer-categorizer --services customer-categorizer-service

# View logs
aws logs tail /ecs/customer-categorizer --follow
```

---

## 6️⃣ Kubernetes

### 1. Create Deployment
```bash
# File: k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-categorizer
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: customer-categorizer
  template:
    metadata:
      labels:
        app: customer-categorizer
    spec:
      containers:
      - name: customer-categorizer
        image: your_registry/customer-categorizer:latest
        ports:
        - containerPort: 5000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: customer-categorizer-secrets
              key: mongodb-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1024Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 2. Create Service
```bash
# File: k8s-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: customer-categorizer-service
spec:
  selector:
    app: customer-categorizer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

### 3. Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace customer-categorizer

# Create secrets
kubectl create secret generic customer-categorizer-secrets \
  --from-literal=mongodb-url="mongodb+srv://user:pass@cluster.mongodb.net/database" \
  -n customer-categorizer

# Deploy
kubectl apply -f k8s-deployment.yaml -n customer-categorizer
kubectl apply -f k8s-service.yaml -n customer-categorizer

# Verify deployment
kubectl get deployments -n customer-categorizer
kubectl get pods -n customer-categorizer
kubectl get services -n customer-categorizer

# View logs
kubectl logs -f deployment/customer-categorizer -n customer-categorizer

# Scale deployment
kubectl scale deployment customer-categorizer --replicas=5 -n customer-categorizer
```

---

## 7️⃣ AWS Lambda

### 1. Install Zappa
```bash
pip install zappa
```

### 2. Initialize Zappa
```bash
zappa init

# Choose settings:
# - Environment: dev
# - Bucket name: customer-categorizer-zappa
# - Whether to deploy VPC: no
```

### 3. Update zappa_settings.json
```json
{
    "dev": {
        "app_function": "app.app",
        "aws_region": "us-east-1",
        "runtime": "python3.8",
        "s3_bucket": "customer-categorizer-zappa",
        "environment_variables": {
            "MONGODB_URL": "mongodb+srv://user:pass@cluster.mongodb.net/database"
        },
        "stages": {
            "dev": {},
            "prod": {}
        }
    }
}
```

### 4. Deploy to Lambda
```bash
# Deploy
zappa deploy dev

# Update existing deployment
zappa update dev

# View logs
zappa tail dev

# Undeploy
zappa undeploy dev
```

---

## 8️⃣ GitHub Actions CI/CD

### 1. Create Workflow File
```bash
# Create directory
mkdir -p .github/workflows

# File: .github/workflows/deploy.yml
name: Deploy to AWS ECS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build, tag, and push image to Amazon ECR
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: customer-categorizer
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

    - name: Update ECS service
      run: |
        aws ecs update-service \
          --cluster customer-categorizer \
          --service customer-categorizer-service \
          --force-new-deployment

    - name: Wait for service to stabilize
      run: |
        aws ecs wait services-stable \
          --cluster customer-categorizer \
          --services customer-categorizer-service
```

### 2. Add GitHub Secrets
```
Settings → Secrets → Add:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
```

---

## 9️⃣ Monitoring & Logging

### Docker Logs
```bash
# View container logs
docker logs customer_categorizer

# Follow logs
docker logs -f customer_categorizer

# Show last 100 lines
docker logs --tail 100 customer_categorizer
```

### Application Logs
```bash
# Access logs from inside container
docker exec customer_categorizer tail -f /app/logs/app.log
```

### Health Monitoring
```bash
# Check health endpoint
curl http://localhost:5000/health

# Setup continuous monitoring
watch -n 5 'curl -s http://localhost:5000/health | jq'
```

### CloudWatch Monitoring (AWS)
```bash
# View logs
aws logs tail /ecs/customer-categorizer --follow

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name customer-categorizer-health \
  --alarm-description "Check application health" \
  --metric-name HealthCheckStatus \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 1 \
  --comparison-operator LessThanThreshold
```

---

## 🔟 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
docker run -p 5001:5000 customer-categorizer:latest
```

#### 2. MongoDB Connection Failed
```bash
# Check MongoDB is running
docker-compose ps mongo

# Test connection
mongosh mongodb://admin:password@localhost:27017

# Check connection string in .env
cat .env | grep MONGODB_URL
```

#### 3. Docker Image Build Failed
```bash
# Check disk space
df -h

# Clean up Docker
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t customer-categorizer:latest .
```

#### 4. Container Exits Immediately
```bash
# Check logs
docker logs customer_categorizer

# Run in interactive mode
docker run -it customer-categorizer:latest bash

# Check dependencies
pip list
```

#### 5. Out of Memory
```bash
# Increase Docker memory limit
docker run -m 2g customer-categorizer:latest

# Check current usage
docker stats

# Limit in docker-compose
services:
  api:
    mem_limit: 2g
```

#### 6. Slow Predictions
```bash
# Check system resources
docker stats

# Monitor database queries
db.setProfilingLevel(1)

# Check model file size
ls -lh models/

# Consider caching predictions
```

---

## 1️⃣1️⃣ Security Best Practices

### 1. Environment Variables
```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use AWS Secrets Manager
aws secretsmanager create-secret --name customer-categorizer-secrets \
  --secret-string "{\"mongodb_url\":\"...\"}"
```

### 2. Docker Security
```bash
# Run as non-root user in Dockerfile
RUN useradd -m -u 1000 appuser
USER appuser

# Use read-only filesystem where possible
docker run --read-only customer-categorizer:latest

# Scan image for vulnerabilities
docker scan customer-categorizer:latest
```

### 3. Network Security
```bash
# Use VPC for AWS deployments
# Restrict security groups to necessary ports only

# For Nginx:
# - Only allow HTTP/HTTPS (80, 443)
# - Hide Nginx version
# - Enable rate limiting
```

### 4. API Security
```bash
# Add API authentication
# Implement rate limiting
# Use HTTPS only
# Enable CORS properly
```

### 5. Data Security
```bash
# Encrypt data at rest in MongoDB
# Use TLS/SSL for connections
# Regular backups
# Monitor access logs
```

### 6. Code Security
```bash
# Scan dependencies
pip-audit

# Check for secrets
git-secrets install

# Code quality
bandit -r src/
```

---

## 1️⃣2️⃣ Performance Optimization

### 1. Application Level
```python
# Use connection pooling
# Implement caching
# Optimize database queries
# Use async where possible
```

### 2. Infrastructure Level
```bash
# Load balancing
# Horizontal scaling
# CDN for static files
# Database indexing
```

### 3. Monitoring
```bash
# Track response times
# Monitor resource usage
# Set up alerts
# Log slow queries
```

---

## Summary

| Deployment Method | Ease | Scalability | Cost | Best For |
|---|---|---|---|---|
| Local | ⭐⭐⭐⭐⭐ | ⭐ | Free | Development |
| Docker | ⭐⭐⭐⭐ | ⭐⭐ | Low | Testing |
| Docker Compose | ⭐⭐⭐⭐ | ⭐⭐ | Low | Local dev |
| EC2 + Nginx | ⭐⭐⭐ | ⭐⭐⭐ | Medium | Small projects |
| ECS | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium | Containers |
| Kubernetes | ⭐⭐ | ⭐⭐⭐⭐⭐ | High | Large scale |
| Lambda | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Very Low | Serverless |

Choose based on your project size, team expertise, and budget!

---

## Support & Resources

- 📚 [FastAPI Docs](https://fastapi.tiangolo.com)
- 🐳 [Docker Docs](https://docs.docker.com)
- ☸️ [Kubernetes Docs](https://kubernetes.io/docs)
- ☁️ [AWS Docs](https://docs.aws.amazon.com)
- 🆘 [GitHub Issues](https://github.com/namanx815/Customer_Categorizer/issues)

