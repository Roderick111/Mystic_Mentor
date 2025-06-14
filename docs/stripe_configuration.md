# Stripe Payment Integration Configuration

This document outlines the complete Stripe payment integration setup for the Esoteric Vectors application.

## 📋 Overview

The application uses Stripe for premium subscription payments with two plan types:
- **Monthly Subscription**: Recurring monthly billing
- **Lifetime Access**: One-time payment for permanent access

## 🔧 Environment Variables

### Required Variables

Add these to your `.env` file:

```bash
# Stripe API Keys (get from Stripe Dashboard)
STRIPE_SECRET_KEY=sk_test_...          # Test: sk_test_... | Live: sk_...
STRIPE_PUBLISHABLE_KEY=pk_test_...     # Test: pk_test_... | Live: pk_...

# Stripe Price IDs (create in Stripe Dashboard)
STRIPE_MONTHLY_PRICE_ID=price_...      # Monthly subscription price ID
STRIPE_LIFETIME_PRICE_ID=price_...     # One-time payment price ID

# Webhook Secret (optional, for production webhooks)
STRIPE_WEBHOOK_SECRET=whsec_...        # Webhook endpoint secret
```

### Getting Stripe Keys

1. **Create Stripe Account**: Go to [stripe.com](https://stripe.com)
2. **Get API Keys**: Dashboard → Developers → API Keys
3. **Create Products**: Dashboard → Products → Add Product
4. **Get Price IDs**: Copy the price IDs from your products

## 🏗️ Architecture

### Backend Components

```
src/core/stripe_service.py          # Main Stripe service class
src/web_api.py                      # API endpoints (/stripe/*)
```

### Frontend Components

```
web/services/stripeService.js       # Frontend Stripe integration
web/components/PremiumModal.js      # Payment UI component
```

### API Endpoints

- `GET /stripe/config` - Get Stripe configuration
- `POST /stripe/create-checkout-session` - Create payment session
- `POST /stripe/webhook` - Handle Stripe webhooks

## 🔄 Payment Flow

1. **User clicks "Go Premium"** → Opens PremiumModal
2. **User selects plan** → Calls stripeService.createCheckoutSession()
3. **Frontend calls API** → POST /stripe/create-checkout-session
4. **Backend creates session** → Returns Stripe checkout URL
5. **User redirects to Stripe** → Completes payment
6. **Stripe redirects back** → With success/cancel status
7. **Webhook processes payment** → Updates user roles in Auth0

## 🧪 Testing

### Run Integration Tests

```bash
# Run all Stripe tests
pytest tests/integration/test_stripe_integration.py

# Run unit tests
pytest tests/unit/test_stripe_service.py

# Quick manual test
python tests/integration/test_stripe_integration.py
```

### Test Cards (Stripe Test Mode)

```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0025 0000 3155
```

## 🚀 Deployment

### Production Checklist

- [ ] Replace test keys with live keys
- [ ] Set up webhook endpoint in Stripe Dashboard
- [ ] Configure `STRIPE_WEBHOOK_SECRET`
- [ ] Test payment flow end-to-end
- [ ] Verify Auth0 role assignment works

### Webhook Configuration

1. **Stripe Dashboard** → Webhooks → Add Endpoint
2. **URL**: `https://yourdomain.com/stripe/webhook`
3. **Events**: Select these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

## 🔍 Troubleshooting

### Common Issues

**"Stripe not configured"**
- Check environment variables are set
- Restart the server after adding .env variables

**"Payment processing temporarily unavailable"**
- Verify STRIPE_SECRET_KEY is valid
- Check Stripe Dashboard for API key status

**"Invalid price configuration"**
- Ensure STRIPE_MONTHLY_PRICE_ID and STRIPE_LIFETIME_PRICE_ID are set
- Verify price IDs exist in your Stripe account

**Webhook not working**
- Check STRIPE_WEBHOOK_SECRET matches Stripe Dashboard
- Verify webhook URL is accessible from internet
- Check webhook event types are configured correctly

### Debug Commands

```bash
# Test Stripe configuration
python tests/integration/test_stripe_integration.py

# Check environment variables
python -c "import os; print('Stripe configured:', bool(os.getenv('STRIPE_SECRET_KEY')))"

# Test API endpoints
curl http://localhost:8000/stripe/config
```

## 📁 File Organization

```
├── src/core/stripe_service.py              # Backend service
├── src/web_api.py                          # API endpoints
├── web/services/stripeService.js           # Frontend service
├── web/components/PremiumModal.js          # Payment UI
├── tests/unit/test_stripe_service.py       # Unit tests
├── tests/integration/test_stripe_integration.py  # Integration tests
└── docs/stripe_configuration.md           # This documentation
```

## 🔒 Security Notes

- Never commit API keys to version control
- Use test keys for development
- Validate webhook signatures in production
- Implement proper error handling
- Log payment events for audit trail

## 📞 Support

For Stripe-specific issues:
- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Support](https://support.stripe.com)

For application-specific issues:
- Check logs in `src/utils/logger.py`
- Run test suite to verify configuration
- Review this documentation for setup steps 