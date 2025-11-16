# 🚀 Deploy on Your Hostinger KVM - Quick Guide

**5-Minute Deployment Guide for Your Own Server**

---

## ✅ Prerequisites

- Hostinger KVM server (you have this!)
- Root/SSH access
- Domain name (for HTTPS)
- Your server IP address

---

## 🚀 Quick Deployment (5 Steps)

### Step 1: Connect to Your Server

```bash
ssh root@YOUR_SERVER_IP
```

### Step 2: Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify
docker --version
```

### Step 3: Clone and Configure

```bash
# Clone repository
cd /opt
git clone https://github.com/radoslav1992/image_edit_api.git
cd image_edit_api

# Create environment file
nano .env
```

Add this content:
```bash
REPLICATE_API_TOKEN=r8_your_actual_token_here
```

Save (Ctrl+X, Y, Enter)

### Step 4: Start the API

```bash
# Build and start
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f api
```

Test it:
```bash
curl http://localhost:8000/health
```

### Step 5: Setup Domain & HTTPS

**A. Point Your Domain:**
- Go to your domain registrar
- Add A record: `your-domain.com` → `YOUR_SERVER_IP`
- Wait 5-15 minutes for DNS propagation

**B. Install Nginx & Get SSL:**

```bash
# Install Nginx
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
nano /etc/nginx/sites-available/api
```

Add this:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save and activate:
```bash
# Enable site
ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/

# Test config
nginx -t

# Restart Nginx
systemctl restart nginx

# Get SSL certificate (FREE)
certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts, select redirect HTTP to HTTPS
```

**C. Configure Firewall:**

```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable
```

---

## ✅ Test Your Deployment

```bash
# Test from your local machine
curl https://your-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "api_configured": true
}
```

---

## 🎯 Connect to RapidAPI

Now that your API is live at `https://your-domain.com`:

1. Go to [RapidAPI Provider Dashboard](https://rapidapi.com/provider)
2. Click "Add New API"
3. **Base URL**: `https://your-domain.com`
4. Import OpenAPI spec: `https://your-domain.com/openapi.json`
5. Configure pricing (see `docs/PRICING.md`)
6. Publish!

**Full RapidAPI setup guide:** `docs/RAPIDAPI_SETUP.md`

---

## 🔄 Update Your API

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Navigate to directory
cd /opt/image_edit_api

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f api
```

---

## 📊 Monitor Your API

```bash
# View logs
docker-compose logs -f api

# Check resource usage
docker stats

# Check if running
docker-compose ps
```

---

## 🐛 Troubleshooting

### API Not Starting

```bash
# Check logs
docker-compose logs api

# Restart
docker-compose restart api
```

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Domain Not Working

```bash
# Check DNS propagation
dig your-domain.com

# Check Nginx
nginx -t
systemctl status nginx

# Restart Nginx
systemctl restart nginx
```

### SSL Certificate Issues

```bash
# Renew certificate
certbot renew

# Check certificate
certbot certificates
```

---

## 📋 Useful Commands

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
cd /opt/image_edit_api && git pull && docker-compose up -d --build

# Backup
tar -czf /root/api-backup-$(date +%Y%m%d).tar.gz /opt/image_edit_api
```

---

## 💰 Cost Savings

**Your Hostinger KVM:**
- Hosting: $0 (already paying for it!)
- Replicate API: ~$20/month (1,000 images)
- **Total: ~$20/month**

**vs. Railway/Heroku:**
- Platform: $10-20/month
- Replicate API: ~$20/month
- **Total: ~$30-40/month**

**Your Savings: $120-240/year!** 💰

---

## 📚 Full Documentation

- **Detailed KVM Guide**: `docs/DEPLOY_HOSTINGER_KVM.md`
- **RapidAPI Setup**: `docs/RAPIDAPI_SETUP.md`
- **Pricing Strategy**: `docs/PRICING.md`
- **SLA Information**: `docs/SLA.md`
- **General Deployment**: `docs/DEPLOYMENT.md`

---

## 🆘 Need Help?

1. Check logs: `docker-compose logs api`
2. Review full guide: `docs/DEPLOY_HOSTINGER_KVM.md`
3. Test locally first: `QUICKSTART.md`
4. Open an issue on GitHub

---

## ✅ Deployment Checklist

- [ ] SSH access to KVM server
- [ ] Docker & Docker Compose installed
- [ ] Repository cloned to `/opt/image_edit_api`
- [ ] `.env` file created with `REPLICATE_API_TOKEN`
- [ ] API running: `docker-compose ps`
- [ ] Domain pointing to server IP
- [ ] Nginx installed and configured
- [ ] SSL certificate obtained (HTTPS working)
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] API accessible: `curl https://your-domain.com/health`
- [ ] Listed on RapidAPI
- [ ] Monitoring setup

---

## 🎉 You're Live!

Your API is now:
- ✅ Running on your own server (saving money!)
- ✅ Secured with HTTPS
- ✅ Ready for RapidAPI
- ✅ Production-ready

**API URL:** `https://your-domain.com`

**Next:** List on RapidAPI and start earning! 💰

---

**Questions?** Check the detailed guides in the `docs/` folder or open an issue on GitHub.

**Ready to monetize?** See `docs/RAPIDAPI_SETUP.md` for step-by-step RapidAPI listing guide.

