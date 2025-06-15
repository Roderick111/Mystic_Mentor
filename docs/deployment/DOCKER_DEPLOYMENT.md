# Docker Deployment Guide for Mystical Mentor

This guide covers deploying the Esoteric Vectors application using Docker on your production server.

## Production Environment

- **Domain**: https://mystical-mentor.beautiful-apps.com
- **Server IP**: 31.97.153.220
- **SSH Access**: `ssh root@31.97.153.220`

## Quick Start

### 1. Upload Project to Server

```bash
# From your local machine, upload the project
scp -r . root@31.97.153.220:/opt/mystical-mentor/

# Or clone from your repository
ssh root@31.97.153.220
cd /opt
git clone <your-repo-url> mystical-mentor
cd mystical-mentor
```

### 2. Run Production Deployment

```bash
# SSH into your server
ssh root@31.97.153.220

# Navigate to project directory
cd /opt/mystical-mentor

# Run the production deployment script
./scripts/deploy-production.sh
```

The script will automatically:
- Install Docker if needed
- Configure firewall (UFW)
- Generate SSL certificates via Let's Encrypt
- Set up monitoring and backups
- Deploy the application

### 3. Configure Environment Variables

After deployment, update your production environment:

```bash
# Edit the environment file
nano .env

# Update these critical values:
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
SECRET_KEY=your_secure_32_char_secret
```

### 4. Restart Services

```bash
docker compose restart
```

## Architecture Overview

```
Internet → Nginx (Port 80/443) → FastAPI Backend (Port 8001)
                ↓
            Static Files (/web/)
```

### Services

1. **Nginx** (`esoteric-nginx`)
   - Reverse proxy and SSL termination
   - Serves static web files
   - Handles rate limiting and security headers
   - Ports: 80 (HTTP) → 443 (HTTPS)

2. **Backend** (`esoteric-backend`)
   - FastAPI application
   - Internal port: 8001
   - Handles API requests and authentication

### Volumes

- `app_data`: Persistent application data (`./data`)
- `app_logs`: Application logs (`./logs`)
- `nginx_logs`: Nginx access and error logs

## Configuration Files

### Environment Variables (.env)

Key production settings:

```bash
# Application URLs
FRONTEND_URL=https://mystical-mentor.beautiful-apps.com
BACKEND_URL=https://mystical-mentor.beautiful-apps.com/api

# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_AUDIENCE=https://mystical-mentor-api

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Security
SECRET_KEY=your_super_secure_secret_key_min_32_chars
CORS_ORIGINS=https://mystical-mentor.beautiful-apps.com,https://www.mystical-mentor.beautiful-apps.com

# SSL Certificates
SSL_CERT_PATH=/app/ssl/mystical-mentor.beautiful-apps.com.pem
SSL_KEY_PATH=/app/ssl/mystical-mentor.beautiful-apps.com-key.pem
```

### SSL Certificates

SSL certificates are automatically generated using Let's Encrypt:

- Certificate: `ssl/mystical-mentor.beautiful-apps.com.pem`
- Private Key: `ssl/mystical-mentor.beautiful-apps.com-key.pem`
- Auto-renewal: Daily cron job

## Management Commands

### Basic Operations

```bash
# View running services
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f backend
docker compose logs -f nginx

# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend

# Stop all services
docker compose down

# Start services
docker compose up -d

# Rebuild and restart
docker compose build --no-cache
docker compose up -d
```

### Health Checks

```bash
# Check application health
curl https://mystical-mentor.beautiful-apps.com/health

# Check backend directly
curl http://localhost:8001/health

# Check nginx status
curl http://localhost/health
```

### SSL Management

```bash
# Check SSL certificate status
./scripts/deploy-production.sh ssl

# Manual certificate renewal
certbot renew
./scripts/deploy-production.sh ssl
```

### Monitoring

```bash
# View monitoring logs
tail -f /var/log/mystical-mentor-monitor.log

# Manual health check
/usr/local/bin/mystical-mentor-monitor

# Check system resources
docker stats
```

### Backups

```bash
# Manual backup
/usr/local/bin/mystical-mentor-backup

# View backup files
ls -la /opt/mystical-mentor/backups/

# Restore from backup
cd /opt/mystical-mentor
tar -xzf backups/data_backup_YYYYMMDD_HHMMSS.tar.gz
```

## Security Features

### Firewall Configuration

```bash
# View firewall status
ufw status

# Allowed ports:
# - 22 (SSH)
# - 80 (HTTP)
# - 443 (HTTPS)
# - 8001 (Backend - for debugging)
```

### Nginx Security Headers

- **HSTS**: Force HTTPS connections
- **CSP**: Content Security Policy
- **X-Frame-Options**: Prevent clickjacking
- **X-Content-Type-Options**: Prevent MIME sniffing
- **X-XSS-Protection**: XSS filtering

### Rate Limiting

- **API endpoints**: 10 requests/second
- **Auth endpoints**: 5 requests/second
- **Burst capacity**: 20 requests (API), 10 requests (Auth)

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check logs
   docker compose logs
   
   # Check disk space
   df -h
   
   # Check memory
   free -h
   ```

2. **SSL certificate issues**
   ```bash
   # Regenerate certificates
   ./scripts/deploy-production.sh ssl
   
   # Check certificate validity
   openssl x509 -in ssl/mystical-mentor.beautiful-apps.com.pem -text -noout
   ```

3. **Database connection issues**
   ```bash
   # Check data directory permissions
   ls -la data/
   
   # Reset data directory
   docker compose down
   sudo chown -R 10001:10001 data/
   docker compose up -d
   ```

4. **Auth0 configuration**
   ```bash
   # Verify environment variables
   grep AUTH0 .env
   
   # Test Auth0 connection
   curl -X POST https://your-tenant.auth0.com/oauth/token \
     -H "Content-Type: application/json" \
     -d '{"client_id":"your_client_id","client_secret":"your_client_secret","audience":"https://mystical-mentor-api","grant_type":"client_credentials"}'
   ```

### Log Locations

- **Application logs**: `./logs/`
- **Nginx logs**: Docker volume `nginx_logs`
- **System logs**: `/var/log/mystical-mentor-monitor.log`
- **SSL renewal logs**: `/var/log/letsencrypt/`

### Performance Monitoring

```bash
# Container resource usage
docker stats

# System resources
htop

# Disk usage
du -sh data/
du -sh logs/

# Network connections
netstat -tulpn | grep :443
netstat -tulpn | grep :8001
```

## Production Checklist

Before going live:

- [ ] Update `.env` with production credentials
- [ ] Configure Auth0 with production domain
- [ ] Set up Stripe webhooks for production
- [ ] Test SSL certificate validity
- [ ] Verify all health endpoints
- [ ] Test authentication flow
- [ ] Test payment processing
- [ ] Configure monitoring alerts
- [ ] Set up backup verification
- [ ] Document emergency procedures

## Support

For issues or questions:

1. Check the logs: `docker compose logs -f`
2. Verify health endpoints: `curl https://mystical-mentor.beautiful-apps.com/health`
3. Review this documentation
4. Check firewall and SSL configuration

## URLs

After successful deployment:

- **Frontend**: https://mystical-mentor.beautiful-apps.com/web/
- **API**: https://mystical-mentor.beautiful-apps.com/api/
- **API Documentation**: https://mystical-mentor.beautiful-apps.com/api/docs
- **Health Check**: https://mystical-mentor.beautiful-apps.com/health 