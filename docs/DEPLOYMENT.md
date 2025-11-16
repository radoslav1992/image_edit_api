# 🚀 Deployment Guide

Complete deployment guides for various platforms. Choose the one that best fits your needs.

---

## Quick Platform Comparison

| Platform | Difficulty | Cost | Auto-scaling | Best For |
|----------|-----------|------|--------------|----------|
| Railway | ⭐ Easy | $5+/mo | ✅ Yes | Quick start, small apps |
| Heroku | ⭐ Easy | Free-$25+/mo | ✅ Yes | Prototypes, MVP |
| DigitalOcean | ⭐⭐ Medium | $5+/mo | ✅ Yes | Production apps |
| Google Cloud Run | ⭐⭐ Medium | Pay-per-use | ✅ Yes | Serverless, scale to zero |
| AWS Lambda | ⭐⭐⭐ Hard | Pay-per-use | ✅ Yes | Enterprise, high scale |
| Docker/VPS | ⭐⭐⭐ Hard | $5+/mo | ❌ Manual | Full control needed |

---

## Table of Contents

1. [Railway (Recommended for Beginners)](#1-railway-recommended)
2. [Heroku](#2-heroku)
3. [DigitalOcean App Platform](#3-digitalocean-app-platform)
4. [Google Cloud Run](#4-google-cloud-run)
5. [AWS Lambda with API Gateway](#5-aws-lambda)
6. [Docker + Any VPS](#6-docker-on-vps)
7. [RapidAPI Hosting](#7-rapidapi-hosting)

---

## 1. Railway (Recommended)

**Pros:** Easiest deployment, automatic HTTPS, great free tier  
**Cons:** Can be expensive at scale

### Step-by-Step

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
# or
brew install railway
```

2. **Login to Railway**
```bash
railway login
```

3. **Initialize Project**
```bash
railway init
```

4. **Set Environment Variables**
```bash
railway variables set REPLICATE_API_TOKEN=your_token_here
```

5. **Deploy**
```bash
railway up
```

6. **Get Your URL**
```bash
railway domain
```

### Configuration File

Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Environment Variables
- `REPLICATE_API_TOKEN` (required)
- `PORT` (auto-set by Railway)

**Estimated Cost:** $5-20/month

---

## 2. Heroku

**Pros:** Simple, generous free tier, good for MVP  
**Cons:** Slower cold starts on free tier

### Step-by-Step

1. **Install Heroku CLI**
```bash
brew install heroku/brew/heroku
# or
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login**
```bash
heroku login
```

3. **Create App**
```bash
heroku create your-background-api
```

4. **Add Procfile**

Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. **Set Environment Variables**
```bash
heroku config:set REPLICATE_API_TOKEN=your_token_here
```

6. **Deploy**
```bash
git push heroku main
```

7. **Scale**
```bash
heroku ps:scale web=1
```

8. **View Logs**
```bash
heroku logs --tail
```

### Configuration

Create `runtime.txt`:
```
python-3.11
```

**Estimated Cost:** Free (with limits) or $7-25/month

---

## 3. DigitalOcean App Platform

**Pros:** Affordable, good performance, simple scaling  
**Cons:** Limited free tier

### Step-by-Step

1. **Connect GitHub Repository**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"
   - Connect your GitHub repository

2. **Configure App**
   - Select repository and branch
   - App Platform auto-detects Python app

3. **Set Environment Variables**
   - Add `REPLICATE_API_TOKEN`

4. **Configure Resources**
   - Set to "Basic" plan ($5/month)
   - 1 GB RAM, 1 vCPU

5. **Deploy**
   - Click "Create Resources"
   - Wait for deployment (~5 minutes)

### App Spec YAML

Create `.do/app.yaml`:
```yaml
name: background-removal-api
services:
- name: web
  github:
    repo: your-username/your-repo
    branch: main
    deploy_on_push: true
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080
  http_port: 8080
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: REPLICATE_API_TOKEN
    scope: RUN_TIME
    type: SECRET
  health_check:
    http_path: /health
```

**Estimated Cost:** $5-12/month

---

## 4. Google Cloud Run

**Pros:** Serverless, scales to zero, pay per use  
**Cons:** More complex setup, potential cold starts

### Step-by-Step

1. **Install gcloud CLI**
```bash
brew install google-cloud-sdk
```

2. **Initialize**
```bash
gcloud init
gcloud auth login
```

3. **Create Dockerfile**

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

4. **Build and Push**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/background-api
```

5. **Deploy**
```bash
gcloud run deploy background-api \
  --image gcr.io/YOUR_PROJECT_ID/background-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars REPLICATE_API_TOKEN=your_token_here
```

6. **Get URL**
```bash
gcloud run services describe background-api --region us-central1
```

### Configuration Options

```bash
# Increase memory
--memory 1Gi

# Set max instances
--max-instances 10

# Set timeout
--timeout 60

# Set concurrency
--concurrency 80
```

**Estimated Cost:** $0-10/month (pay per use)

---

## 5. AWS Lambda with API Gateway

**Pros:** True serverless, massive scale, pay per request  
**Cons:** Most complex setup, cold starts

### Step-by-Step

1. **Install Serverless Framework**
```bash
npm install -g serverless
```

2. **Create serverless.yml**

```yaml
service: background-removal-api

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    REPLICATE_API_TOKEN: ${env:REPLICATE_API_TOKEN}
  timeout: 60
  memorySize: 1024

functions:
  api:
    handler: lambda_handler.handler
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY
```

3. **Create lambda_handler.py**

```python
from mangum import Mangum
from main import app

handler = Mangum(app)
```

4. **Update requirements.txt**

Add:
```
mangum==0.17.0
```

5. **Deploy**
```bash
serverless deploy
```

### Alternative: AWS SAM

Create `template.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 60
    MemorySize: 1024

Resources:
  BackgroundRemovalFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.handler
      Runtime: python3.11
      Environment:
        Variables:
          REPLICATE_API_TOKEN: !Ref ReplicateApiToken
      Events:
        ApiEvent:
          Type: HttpApi

Parameters:
  ReplicateApiToken:
    Type: String
    NoEcho: true
```

Deploy:
```bash
sam build
sam deploy --guided
```

**Estimated Cost:** $0-20/month (pay per request)

---

## 6. Docker on VPS

**Pros:** Full control, portable, affordable  
**Cons:** Manual setup and maintenance

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN}
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - api
    restart: unless-stopped
```

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
```

### Deploy on VPS

1. **SSH into VPS**
```bash
ssh user@your-server-ip
```

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

3. **Clone Repository**
```bash
git clone your-repo-url
cd background_removal_api
```

4. **Set Environment Variables**
```bash
echo "REPLICATE_API_TOKEN=your_token" > .env
```

5. **Start Services**
```bash
docker-compose up -d
```

6. **View Logs**
```bash
docker-compose logs -f
```

### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Estimated Cost:** $5-20/month (VPS cost)

---

## 7. RapidAPI Hosting

RapidAPI doesn't host your API directly. You need to:

1. **Deploy on any platform above**
2. **Get your public URL** (e.g., `https://your-api.railway.app`)
3. **List on RapidAPI**

### Listing on RapidAPI

1. **Go to** [RapidAPI Provider Dashboard](https://rapidapi.com/provider)
2. **Click "Add New API"**
3. **Enter API Details:**
   - Name: Background Removal API
   - Base URL: Your deployed URL
   - OpenAPI Spec: Import from `/openapi.json`

4. **Configure Authentication:**
   - Type: Header Authentication
   - Header: X-RapidAPI-Key
   - Your API will receive headers from RapidAPI

5. **Set Pricing Plans**
   - Use the plans from `/pricing`

6. **Test Endpoints**
   - RapidAPI tests all endpoints

7. **Publish**
   - Submit for review
   - Make public once approved

---

## Post-Deployment Checklist

### ✅ Required

- [ ] Environment variables set correctly
- [ ] HTTPS enabled
- [ ] Health check endpoint responding
- [ ] API documentation accessible
- [ ] Rate limiting configured
- [ ] Error logging enabled

### ✅ Recommended

- [ ] Custom domain configured
- [ ] Monitoring setup (e.g., Sentry, DataDog)
- [ ] Automated backups
- [ ] Load testing completed
- [ ] Security headers configured
- [ ] CORS configured properly

### ✅ Production

- [ ] Auto-scaling configured
- [ ] Database for usage tracking (if needed)
- [ ] CDN for static assets
- [ ] Log aggregation (e.g., Papertrail)
- [ ] Uptime monitoring (e.g., Uptimerobot)
- [ ] Incident response plan

---

## Environment Variables Reference

Required:
```bash
REPLICATE_API_TOKEN=r8_your_token_here
```

Optional:
```bash
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/hour

# Caching
CACHE_ENABLED=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_REQUESTS=true

# Security
ALLOWED_API_KEYS=key1,key2,key3

# Features
WEBHOOK_ENABLED=true
MAX_IMAGE_SIZE_MB=10
```

---

## Monitoring and Logs

### Log Aggregation Services

- **Papertrail:** Free tier, easy setup
- **Loggly:** Good for small teams
- **DataDog:** Enterprise-grade
- **CloudWatch:** AWS native

### Uptime Monitoring

- **Uptimerobot:** Free, 5-minute checks
- **Pingdom:** More features, paid
- **StatusCake:** Good free tier
- **Better Uptime:** Modern interface

### Error Tracking

- **Sentry:** Best error tracking
- **Rollbar:** Good alternative
- **Bugsnag:** Simple setup

---

## Scaling Tips

### Horizontal Scaling

- Use load balancer
- Multiple instances
- Shared cache (Redis)

### Vertical Scaling

- Increase RAM
- More CPU cores
- Faster disk I/O

### Performance Optimization

- Enable caching
- Use CDN for assets
- Optimize image sizes
- Database connection pooling
- Async processing for webhooks

---

## Troubleshooting

### Common Issues

**API not responding:**
```bash
# Check if service is running
docker ps
# or
railway logs
```

**Environment variables not set:**
```bash
# Verify variables
echo $REPLICATE_API_TOKEN
```

**Port conflicts:**
```bash
# Check what's using port
lsof -i :8000
```

**Out of memory:**
```bash
# Increase memory limit
docker run -m 2g ...
```

---

## Cost Optimization

1. **Enable caching** - Reduce API calls
2. **Set rate limits** - Prevent abuse
3. **Scale to zero** - Use serverless when possible
4. **Monitor usage** - Track unexpected spikes
5. **Choose right plan** - Don't over-provision

---

## Security Hardening

1. **Use HTTPS** - Always encrypt traffic
2. **Rotate API keys** - Regularly change keys
3. **Rate limiting** - Prevent brute force
4. **Input validation** - Sanitize all inputs
5. **Security headers** - Add recommended headers
6. **Keep dependencies updated** - Regular updates
7. **Monitor logs** - Watch for suspicious activity

---

## Getting Help

- **Documentation:** `/docs` endpoint
- **Issues:** GitHub issues
- **Community:** Discord/Slack
- **Support:** support@backgroundremoval.api

---

**Recommended:** Start with Railway or Heroku, then move to DigitalOcean or GCP as you scale.

Good luck with your deployment! 🚀

