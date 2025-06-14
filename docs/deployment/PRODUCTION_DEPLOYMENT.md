# 🚀 Production Deployment Checklist

## ✅ **PRE-DEPLOYMENT CHECKLIST**

### **🔧 Environment Configuration**
- [ ] Copy `config/production.env.example` to `.env`
- [ ] Set `FRONTEND_URL` to your production domain
- [ ] Configure Auth0 production settings
- [ ] Replace Stripe test keys with live keys
- [ ] Set up Stripe webhook endpoint
- [ ] Configure production database (if applicable)

### **🔐 Security Configuration**
- [ ] Generate secure SSL certificates (not self-signed)
- [ ] Configure proper CORS origins
- [ ] Set up firewall rules
- [ ] Enable HTTPS redirect
- [ ] Configure secure headers

### **🧪 Testing**
- [ ] Run integration tests: `pytest tests/integration/`
- [ ] Run unit tests: `pytest tests/unit/`
- [ ] Test Auth0 setup: `python tests/integration/test_auth0_setup.py`
- [ ] Test Stripe integration: `python tests/integration/test_stripe_integration.py`

## 🚀 **DEPLOYMENT STEPS**

### **1. Server Setup**
```bash
# SSH into your production server
ssh -p 65002 u203148324@147.93.93.103

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y
```

### **2. Application Deployment**
```bash
# Clone repository
git clone <your-repo-url> esoteric-vectors
cd esoteric-vectors

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp config/production.env.example .env
nano .env  # Edit with your production values
```

### **3. Stripe Configuration**
```bash
# Test Stripe configuration
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Stripe Secret Key:', 'Present' if os.getenv('STRIPE_SECRET_KEY') else 'Missing')
print('Stripe Publishable Key:', 'Present' if os.getenv('STRIPE_PUBLISHABLE_KEY') else 'Missing')
print('Monthly Price ID:', 'Present' if os.getenv('STRIPE_MONTHLY_PRICE_ID') else 'Missing')
print('Lifetime Price ID:', 'Present' if os.getenv('STRIPE_LIFETIME_PRICE_ID') else 'Missing')
"
```

### **4. Auth0 Configuration**
```bash
# Test Auth0 setup
python tests/integration/test_auth0_setup.py
```

### **5. Start Production Services**
```bash
# Start API server
python start_web_api_https.py

# In another terminal, start frontend server
python start_https_server.py
```

## 🔍 **POST-DEPLOYMENT VERIFICATION**

### **API Health Checks**
- [ ] `curl https://your-domain.com/health` → 200 OK
- [ ] `curl https://your-domain.com/stripe/config` → Returns config
- [ ] `curl https://your-domain.com/auth/status` → Returns Auth0 status

### **Frontend Checks**
- [ ] Visit `https://your-domain.com` → Loads correctly
- [ ] Auth0 login works → User can sign in
- [ ] Stripe checkout works → Payment flow completes
- [ ] Premium features activate → User gets premium access

### **Integration Tests**
- [ ] End-to-end payment flow
- [ ] Auth0 JWT validation
- [ ] Webhook processing
- [ ] User role assignment

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

**"Stripe not configured"**
```bash
# Check environment variables
grep STRIPE .env
# Restart services after updating .env
```

**"Auth0 authentication failed"**
```bash
# Verify Auth0 configuration
python tests/integration/test_auth0_setup.py
# Check Auth0 Dashboard settings
```

**"SSL Certificate errors"**
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout
# Renew certificates if needed
```

**"Payment webhook not working"**
- Verify webhook URL in Stripe Dashboard
- Check webhook secret matches `.env`
- Ensure server is accessible from internet

## 📊 **MONITORING**

### **Log Files**
- Application logs: Check console output
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u your-service`

### **Health Monitoring**
- Set up uptime monitoring
- Configure error alerting
- Monitor payment success rates
- Track user authentication metrics

## 🔄 **MAINTENANCE**

### **Regular Tasks**
- [ ] Update dependencies monthly
- [ ] Rotate SSL certificates
- [ ] Monitor Stripe webhook health
- [ ] Review Auth0 logs
- [ ] Backup user data

### **Security Updates**
- [ ] Keep Python updated
- [ ] Update npm packages
- [ ] Monitor security advisories
- [ ] Review access logs

---

## 📞 **SUPPORT**

If you encounter issues during deployment:
1. Check the troubleshooting section above
2. Review application logs
3. Test individual components
4. Verify environment configuration

**Remember**: Always test in a staging environment before deploying to production! 