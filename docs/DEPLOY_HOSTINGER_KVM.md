# 🚀 Deploy on Hostinger KVM

Complete guide to deploy your Background Removal API on your own Hostinger KVM server.

---

## 🎯 Advantages of Using Your Own Server

- ✅ **Save Money** - Already paying for it!
- ✅ **Full Control** - Root access to everything
- ✅ **Better Margins** - No platform fees
- ✅ **Multiple Apps** - Host multiple projects

---

## 📋 Prerequisites

### What You Need

- ✅ Hostinger KVM server (you have this!)
- ✅ Root/sudo access
- ✅ Domain name (optional but recommended for RapidAPI)
- ✅ SSH access to your server

### Recommended Server Specs

**Minimum:**
- 1 vCPU
- 2GB RAM
- 20GB Storage
- Ubuntu 20.04+ or Debian 11+

**Recommended for Production:**
- 2 vCPU
- 4GB RAM
- 40GB Storage

---

## 🔧 Option 1: Docker Deployment (Recommended)

Docker makes it easy to manage, update, and scale your API.

### Step 1: Connect to Your Server

```bash
ssh root@your-server-ip
# or
ssh your-username@your-server-ip
```

### Step 2: Install Docker & Docker Compose

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

### Step 3: Clone Your Repository

```bash
# Install git if needed
apt install git -y

# Clone your repo
cd /opt
git clone git@github.com:radoslav1992/image_edit_api.git
cd image_edit_api

# Or use HTTPS
git clone https://github.com/radoslav1992/image_edit_api.git
cd image_edit_api
```

### Step 4: Create Environment File

```bash
# Create .env file
nano .env
```

Add your configuration:
```bash
# Required
REPLICATE_API_TOKEN=r8_your_token_here

# Optional - customize if needed
RATE_LIMIT_DEFAULT=100/hour
CACHE_ENABLED=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 5: Create docker-compose.yml

```bash
nano docker-compose.yml
```

Add this configuration:

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: background_removal_api
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - PORT=8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Step 6: Create Nginx Configuration

```bash
nano nginx.conf
```

Add this:

```nginx
events {
    worker_connections 1024;
}

http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    # Upstream API
    upstream api {
        server api:8000;
    }

    # HTTP Server (redirects to HTTPS)
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        
        # For Let's Encrypt verification
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Redirect all HTTP to HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL Configuration (we'll set this up later)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API proxy
        location / {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffering
            proxy_buffering off;
        }
    }
}
```

### Step 7: Start the API

```bash
# Build and start
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f api
```

### Step 8: Test Your API

```bash
# Test from server
curl http://localhost:8000/health

# You should see:
# {"status":"healthy","version":"1.0.0",...}
```

---

## 🔐 Setup SSL Certificate (HTTPS)

RapidAPI **requires HTTPS**. Let's set it up with Let's Encrypt (free).

### Step 1: Install Certbot

```bash
apt install certbot python3-certbot-nginx -y
```

### Step 2: Point Your Domain to Server

Before getting SSL, configure your domain DNS:

1. Go to your domain registrar
2. Add/Update A record:
   ```
   Type: A
   Name: @ (or your-subdomain)
   Value: YOUR_SERVER_IP
   TTL: 300
   ```
3. Wait 5-15 minutes for DNS propagation

Verify:
```bash
# Check if domain points to your server
dig your-domain.com +short
# Should show your server IP
```

### Step 3: Get SSL Certificate

**Option A: If using Nginx in Docker:**

```bash
# Stop nginx temporarily
docker-compose stop nginx

# Get certificate
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates
mkdir -p ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/

# Start nginx
docker-compose up -d nginx
```

**Option B: Install Nginx directly (simpler):**

```bash
# Remove nginx from docker-compose.yml
# Install nginx on host
apt install nginx -y

# Copy nginx.conf to /etc/nginx/nginx.conf
cp nginx.conf /etc/nginx/nginx.conf

# Get certificate (easier with native nginx)
certbot --nginx -d your-domain.com -d www.your-domain.com

# Restart nginx
systemctl restart nginx
```

### Step 4: Auto-Renewal

```bash
# Test renewal
certbot renew --dry-run

# Certbot automatically adds renewal cron job
# Verify:
systemctl list-timers | grep certbot
```

---

## 🌐 Configure Firewall

```bash
# Install ufw if not installed
apt install ufw -y

# Allow SSH (IMPORTANT - do this first!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

---

## 🔄 Updates & Maintenance

### Update Your API

```bash
cd /opt/image_edit_api

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f api
```

### View Logs

```bash
# API logs
docker-compose logs -f api

# Nginx logs (if using docker)
docker-compose logs -f nginx

# System logs
journalctl -u nginx -f
```

### Backup

```bash
# Create backup script
nano /root/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup code
tar -czf $BACKUP_DIR/api_$DATE.tar.gz /opt/image_edit_api

# Backup SSL certificates
tar -czf $BACKUP_DIR/ssl_$DATE.tar.gz /etc/letsencrypt

# Keep only last 7 backups
ls -t $BACKUP_DIR/api_*.tar.gz | tail -n +8 | xargs rm -f
ls -t $BACKUP_DIR/ssl_*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x /root/backup.sh

# Add to crontab (daily backup at 2 AM)
crontab -e
# Add this line:
# 0 2 * * * /root/backup.sh >> /var/log/backup.log 2>&1
```

---

## 📊 Monitoring

### Install monitoring tools

```bash
# Install htop for resource monitoring
apt install htop -y

# Check resource usage
htop

# Check Docker stats
docker stats

# Check disk usage
df -h
```

### Setup Simple Uptime Monitoring

Use external services (free):
- [Uptime Robot](https://uptimerobot.com) - Free, 5-minute checks
- [Better Stack](https://betterstack.com) - Free tier
- [Pingdom](https://www.pingdom.com) - Free trial

Configure to check: `https://your-domain.com/health`

---

## 🚀 Connect to RapidAPI

Now that your API is running on `https://your-domain.com`:

1. Go to [RapidAPI Provider Dashboard](https://rapidapi.com/provider)
2. Add New API
3. **Base URL:** `https://your-domain.com`
4. Import OpenAPI spec: `https://your-domain.com/openapi.json`
5. Configure pricing and publish!

See full RapidAPI setup: [docs/RAPIDAPI_SETUP.md](RAPIDAPI_SETUP.md)

---

## 💰 Cost Comparison

### Your Hostinger KVM
- **Monthly Cost:** $0 (already paying for it!)
- **Replicate API:** ~$20/month (for 1,000 images)
- **Total:** ~$20/month

### Railway Alternative
- **Platform Cost:** ~$10-20/month
- **Replicate API:** ~$20/month
- **Total:** ~$30-40/month

**Your Savings:** $10-20/month = $120-240/year! 💰

---

## 🐛 Troubleshooting

### API Not Starting

```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. Port already in use
sudo lsof -i :8000
# Kill process using port
sudo kill -9 <PID>

# 2. Environment variables not set
docker-compose exec api env | grep REPLICATE

# 3. Build failed
docker-compose build --no-cache api
```

### SSL Certificate Issues

```bash
# Check certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Renew certificate manually
certbot renew --force-renewal
```

### High Memory Usage

```bash
# Check memory
free -h

# Restart API
docker-compose restart api

# Add swap if needed (for 2GB+ RAM servers)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Domain Not Resolving

```bash
# Check DNS
dig your-domain.com

# Test with IP directly
curl http://YOUR_SERVER_IP:8000/health

# If IP works but domain doesn't, DNS propagation is still ongoing
# Wait 15-30 minutes
```

---

## 📈 Scaling on Your Server

### Vertical Scaling (Upgrade Server)

Upgrade your Hostinger KVM plan:
- More CPU cores
- More RAM
- More storage

### Horizontal Scaling (Multiple Instances)

```yaml
# docker-compose.yml
services:
  api:
    # ... existing config ...
    deploy:
      replicas: 3
```

Then use Nginx load balancing:

```nginx
upstream api {
    least_conn;
    server api:8000;
    server api:8001;
    server api:8002;
}
```

### Add Caching Layer (Redis)

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:alpine
    container_name: redis_cache
    restart: unless-stopped
    ports:
      - "6379:6379"
```

---

## 🔒 Security Best Practices

### 1. Disable Root Login

```bash
# Edit SSH config
nano /etc/ssh/sshd_config

# Change these lines:
PermitRootLogin no
PasswordAuthentication no

# Restart SSH
systemctl restart sshd
```

### 2. Setup Fail2Ban

```bash
# Install
apt install fail2ban -y

# Start
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Keep System Updated

```bash
# Auto-update security patches
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
```

---

## 🎯 Quick Reference Commands

```bash
# Start API
docker-compose up -d

# Stop API
docker-compose down

# Restart API
docker-compose restart api

# View logs
docker-compose logs -f api

# Update code
git pull && docker-compose up -d --build

# Check status
docker-compose ps

# Check resources
docker stats

# Clean up
docker system prune -a
```

---

## 📞 Need Help?

Common Hostinger KVM issues:
- **Port 8000 blocked?** Open in Hostinger panel firewall
- **Domain not working?** Check Hostinger DNS settings
- **Can't connect via SSH?** Check Hostinger panel for IP/credentials

---

## ✅ Deployment Checklist

- [ ] SSH access to server
- [ ] Docker & Docker Compose installed
- [ ] Repository cloned to `/opt/image_edit_api`
- [ ] `.env` file created with `REPLICATE_API_TOKEN`
- [ ] API running on port 8000
- [ ] Domain pointing to server IP
- [ ] SSL certificate installed (HTTPS)
- [ ] Nginx configured and running
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] API accessible via `https://your-domain.com`
- [ ] Health check passing: `https://your-domain.com/health`
- [ ] Listed on RapidAPI
- [ ] Backups configured
- [ ] Monitoring setup

---

## 🎉 You're Done!

Your API is now:
- ✅ Running on your own server
- ✅ Secured with HTTPS
- ✅ Protected by firewall
- ✅ Auto-restarting if it crashes
- ✅ Ready for RapidAPI
- ✅ Saving you $10-20/month!

**Your API URL:** `https://your-domain.com`

Now follow [RAPIDAPI_SETUP.md](RAPIDAPI_SETUP.md) to list it on RapidAPI! 🚀

