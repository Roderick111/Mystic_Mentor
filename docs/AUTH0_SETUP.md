# Auth0 Setup Guide for Esoteric Vectors

This guide walks you through setting up Auth0 authentication for production deployment of the Esoteric Vectors system.

## 🚀 Quick Start

### 1. Create Auth0 Account

1. Go to [auth0.com](https://auth0.com) and sign up for a free account
2. Complete the onboarding process
3. Note your **Auth0 Domain** (e.g., `your-tenant.auth0.com`)

### 2. Configure Auth0 Applications

#### **Application 1: API (Machine-to-Machine)**

1. **Navigate to Applications** → **Create Application**
2. **Name**: `Esoteric Vectors API`
3. **Type**: `Machine to Machine Applications`
4. **Authorize**: Select your default API or create a new one
5. **Note the values**:
   - `Client ID`
   - `Client Secret`
   - `Domain`

#### **Application 2: Frontend (Single Page Application)**

1. **Navigate to Applications** → **Create Application**
2. **Name**: `Esoteric Vectors Frontend`
3. **Type**: `Single Page Applications`
4. **Configure Settings**:
   - **Allowed Callback URLs**: `https://yourdomain.com/callback, http://localhost:3000/callback`
   - **Allowed Logout URLs**: `https://yourdomain.com/, http://localhost:3000/`
   - **Allowed Web Origins**: `https://yourdomain.com, http://localhost:3000`
   - **Allowed Origins (CORS)**: `https://yourdomain.com, http://localhost:3000`

### 3. Create and Configure API

1. **Navigate to APIs** → **Create API**
2. **Name**: `Esoteric Vectors API`
3. **Identifier**: `https://api.esoteric-agent.com` (use your domain)
4. **Signing Algorithm**: `RS256`

#### **Configure API Scopes (Optional)**

Add these scopes for fine-grained access control:

```
read:profile    - Read user profile information
write:profile   - Update user profile information
read:sessions   - Read user sessions
write:sessions  - Create/modify user sessions
admin:commands  - Execute administrative commands
```

### 4. Set Up Custom Claims

#### **Create Auth0 Action (Rules)**

1. **Navigate to Actions** → **Flows** → **Login**
2. **Add Action** → **Build Custom**
3. **Name**: `Add Custom Claims`
4. **Code**:

```javascript
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://esoteric-agent.com/user_metadata';
  
  // Get user metadata or set defaults
  const userMetadata = event.user.user_metadata || {};
  
  // Add custom claims to the token
  api.idToken.setCustomClaim(namespace, {
    memory_preferences: userMetadata.memory_preferences || {},
    active_domains: userMetadata.active_domains || [],
    session_settings: userMetadata.session_settings || {}
  });
  
  // Also add to access token for API access
  api.accessToken.setCustomClaim(namespace, {
    memory_preferences: userMetadata.memory_preferences || {},
    active_domains: userMetadata.active_domains || [],
    session_settings: userMetadata.session_settings || {}
  });
};
```

5. **Deploy** the action
6. **Add to Login Flow** by dragging it into the flow

## 🔧 Environment Configuration

### 1. Update Your .env File

Copy the values from your Auth0 setup:

```bash
# From Auth0 Dashboard > Applications > API
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://api.esoteric-agent.com

# Production settings
PRODUCTION_MODE=true
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Install Dependencies

```bash
# Install the new Auth0 dependencies
uv sync
```

## 🧪 Testing Authentication

### 1. Start the API Server

```bash
python src/web_api.py
```

### 2. Test Health Check

```bash
curl http://localhost:8000/health
```

You should see Auth0 status in the response:

```json
{
  "status": "healthy",
  "components": {
    "auth0": {
      "enabled": true,
      "domain": "your-tenant.auth0.com",
      "audience": "https://api...",
      "validator_initialized": true
    }
  }
}
```

### 3. Test Public Endpoints

```bash
# Public endpoint (no auth required)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### 4. Test Protected Endpoints

First, get an access token from Auth0:

```bash
# Using Auth0 CLI or your frontend application
# Then test protected endpoint:

curl -X GET http://localhost:8000/auth/user \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🏗️ Frontend Integration

### React/Next.js Setup

1. **Install Auth0 SDK**:

```bash
npm install @auth0/auth0-react
```

2. **Configure Auth0Provider**:

```jsx
import { Auth0Provider } from '@auth0/auth0-react';

const domain = process.env.REACT_APP_AUTH0_DOMAIN;
const clientId = process.env.REACT_APP_AUTH0_CLIENT_ID;
const audience = process.env.REACT_APP_AUTH0_AUDIENCE;

function App() {
  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      audience={audience}
      redirectUri={window.location.origin}
      scope="openid profile email read:profile write:profile read:sessions write:sessions"
    >
      <MyApp />
    </Auth0Provider>
  );
}
```

3. **Use in Components**:

```jsx
import { useAuth0 } from '@auth0/auth0-react';

function ChatComponent() {
  const { isAuthenticated, user, getAccessTokenSilently } = useAuth0();
  
  const sendMessage = async (message) => {
    let headers = { 'Content-Type': 'application/json' };
    
    if (isAuthenticated) {
      const token = await getAccessTokenSilently();
      headers.Authorization = `Bearer ${token}`;
    }
    
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers,
      body: JSON.stringify({ message })
    });
    
    return response.json();
  };
  
  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {user.name}!</p>
      ) : (
        <p>You can chat anonymously or log in for personalized experience.</p>
      )}
      {/* Chat interface */}
    </div>
  );
}
```

## 🔒 Security Best Practices

### 1. Token Validation

- ✅ **JWKS Caching**: Implemented with 1-hour cache duration
- ✅ **Signature Verification**: RS256 algorithm validation
- ✅ **Audience Validation**: Ensures tokens are for your API
- ✅ **Issuer Validation**: Validates Auth0 domain
- ✅ **Expiration Checking**: Automatic token expiry validation

### 2. Rate Limiting

Add rate limiting middleware (implement as needed):

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest, user: OptionalUser = None):
    # Implementation
```

### 3. CORS Configuration

Update CORS for production:

```python
origins = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
    # Add your production domains
]
```

### 4. HTTPS Only

Ensure all production deployments use HTTPS:

```bash
# Use a reverse proxy like nginx or deploy behind a load balancer
# Never deploy Auth0 integration over HTTP in production
```

## 📊 Monitoring & Logging

### Authentication Metrics

Monitor these metrics in production:

- **Token validation failures**
- **Authentication success/failure rates**
- **User session creation patterns**
- **API endpoint usage by authenticated vs anonymous users**

### Log Examples

The system logs authentication events:

```
✅ User authenticated: auth0|123456789
🔒 Optional auth failed: Invalid token
👤 User synced: auth0|123456789
📝 User metadata update: auth0|123456789 -> {...}
```

## 🚨 Troubleshooting

### Common Issues

1. **"Authentication service unavailable"**
   - Check AUTH0_DOMAIN is correct (no https:// prefix)
   - Verify network connectivity to Auth0

2. **"Invalid token"**
   - Ensure token is fresh (not expired)
   - Check AUTH0_AUDIENCE matches your API identifier

3. **"Unable to find appropriate signing key"**
   - Token might be from wrong Auth0 tenant
   - JWKS endpoint might be unreachable

4. **CORS errors in browser**
   - Add your frontend domain to Auth0 application settings
   - Update ALLOWED_ORIGINS in your .env file

### Debug Mode

Enable debug logging:

```bash
ENABLE_DEBUG_LOGS=true
LOG_LEVEL=DEBUG
```

### Health Check

Always check the health endpoint first:

```bash
curl http://your-api-domain/health | jq '.components.auth0'
```

## 🎯 Production Checklist

- [ ] Auth0 applications configured correctly
- [ ] Custom claims action deployed
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] CORS configured for production domains
- [ ] Rate limiting implemented
- [ ] Monitoring and logging set up
- [ ] Error handling tested
- [ ] User session isolation working
- [ ] Frontend integration tested

## 📚 Additional Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [Auth0 React SDK](https://auth0.com/docs/libraries/auth0-react)
- [JWT.io](https://jwt.io/) - Token decoder for debugging
- [Auth0 Community](https://community.auth0.com/) - Get help from the community

---

🎉 **Congratulations!** You now have production-ready Auth0 authentication integrated with your Esoteric Vectors system. Users can enjoy personalized experiences while maintaining the option for anonymous usage. 