# 🔐 Auth0 Authentication Testing Guide

## Overview
This guide will help you test the complete Auth0 authentication integration in your Esoteric Vectors application.

## 🚀 Quick Test Steps

### 1. Start the Backend API
```bash
# Make sure your backend is running with Auth0 enabled
python start_web_api.py
```

### 2. Verify Auth0 Backend Configuration
```bash
# Test auth status endpoint
curl http://localhost:8000/auth/status | python -m json.tool
```

**Expected Response:**
```json
{
    "auth0_enabled": true,
    "status": {
        "enabled": true,
        "domain": "dev-d2dttzao1vs6jrmf.us.auth0.com",
        "audience": "https://de...",
        "validator_initialized": true
    },
    "timestamp": "2025-06-11T21:39:58.061022"
}
```

### 3. Test Frontend Integration
Open your web browser and navigate to:
- **Main App**: `http://localhost:8000/web/index.html`
- **Auth Test Page**: `http://localhost:8000/web/test_auth_integration.html`

## 🧪 Authentication Test Scenarios

### Scenario 1: Anonymous User Experience
1. **Open the main app** without signing in
2. **Verify you see**:
   - Blue authentication banner at the top
   - "Sign In" button in the top-right corner
   - Chat functionality works normally
   - Sessions are temporary (local only)

### Scenario 2: Login Flow Test
1. **Click "Sign In"** from either:
   - The authentication banner
   - The auth button in top-right corner
2. **Verify redirect** to Auth0 login page:
   - Should show your Auth0 domain: `dev-d2dttzao1vs6jrmf.us.auth0.com`
   - Login options (email/password, Google, etc.)
3. **Complete login** with your test account
4. **Verify redirect back** to your app
5. **Check authenticated state**:
   - Authentication banner disappears
   - User avatar/name appears in top-right
   - User dropdown shows profile info

### Scenario 3: Authenticated User Experience
1. **After successful login**, verify:
   - User info displayed correctly
   - Sessions are now persistent
   - API calls include authentication headers
   - User preferences can be saved

### Scenario 4: Logout Flow Test
1. **Click user avatar** in top-right corner
2. **Select "Sign Out"** from dropdown
3. **Verify logout**:
   - Redirected to Auth0 logout
   - Returned to app in anonymous state
   - Authentication banner reappears
   - Local session cleared

## 🔍 Debugging Authentication Issues

### Common Issues and Solutions

#### Issue: "Auth0 service not available"
**Solution**: Check browser console for JavaScript errors
```javascript
// Open browser console and check:
console.log(window.auth0Service);
console.log(window.useAuth);
```

#### Issue: Infinite redirect loop
**Solution**: Check Auth0 configuration
- Verify callback URL is set to your domain
- Check allowed origins in Auth0 dashboard

#### Issue: "Invalid audience" error
**Solution**: Verify API audience matches
```bash
# Check your .env file:
grep AUTH0_AUDIENCE .env
```

#### Issue: Token validation errors
**Solution**: Check browser network tab
- Look for 401/403 responses
- Verify Authorization header is being sent

### Debug Tools

#### 1. Auth0 Service Console Commands
Open browser console and run:
```javascript
// Check auth status
window.auth0Service.getAuthStatus()

// Check token
window.auth0Service.getAccessToken()

// Check user info
window.auth0Service.getUser()
```

#### 2. Backend API Test
```bash
# Test with manual token (after login)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/auth/user
```

## 📱 Mobile Testing

### iOS Safari
1. Test login flow on iPhone/iPad
2. Verify redirects work properly
3. Check token persistence

### Android Chrome
1. Test on Android device
2. Verify popup blocking doesn't interfere
3. Check localStorage persistence

## 🎯 Feature Testing Checklist

### Anonymous User Features ✅
- [ ] Can access chat without login
- [ ] Sees authentication banner
- [ ] Can create temporary sessions
- [ ] Basic functionality works

### Authentication Flow ✅
- [ ] Login button triggers Auth0
- [ ] Successful redirect after login
- [ ] Token stored in localStorage
- [ ] User info displayed correctly

### Authenticated User Features ✅
- [ ] User avatar shows in top-right
- [ ] Dropdown menu appears on click
- [ ] User preferences accessible
- [ ] Sessions are persistent
- [ ] API calls include auth headers

### Session Management ✅
- [ ] Anonymous sessions work
- [ ] Authenticated sessions persist
- [ ] Session switching works
- [ ] Session data is user-specific

### Logout Flow ✅
- [ ] Logout button works
- [ ] Redirected to Auth0 logout
- [ ] Returns to anonymous state
- [ ] Local storage cleared

## 🚨 Security Verification

### Token Security
- [ ] Tokens stored securely (localStorage)
- [ ] Tokens have expiration
- [ ] Expired tokens are handled
- [ ] Logout clears all tokens

### API Security
- [ ] Protected endpoints require auth
- [ ] Invalid tokens are rejected
- [ ] User isolation works correctly
- [ ] CORS configured properly

## 📊 Performance Testing

### Load Time
- [ ] Auth service initializes quickly
- [ ] No blocking during auth check
- [ ] Smooth transition to authenticated state

### User Experience
- [ ] No UI flickering during auth
- [ ] Loading states are smooth
- [ ] Error states are handled gracefully

## 🎉 Success Criteria

Your Auth0 integration is working correctly when:

1. **Anonymous users** can use the app normally
2. **Login flow** redirects to Auth0 and back smoothly
3. **Authenticated users** see personalized interface
4. **Sessions persist** across browser refreshes
5. **Logout** properly clears authentication state
6. **API calls** include proper authentication headers
7. **Error handling** is graceful and informative

## 🆘 Need Help?

If you encounter issues:

1. **Check browser console** for JavaScript errors
2. **Verify Auth0 configuration** in dashboard
3. **Test backend endpoints** directly with curl
4. **Check network tab** for failed requests
5. **Review .env file** for correct values

Happy testing! 🚀 