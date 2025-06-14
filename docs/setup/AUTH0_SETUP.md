# Auth0 Dashboard Configuration

## Required Settings

Go to your Auth0 Dashboard → Applications → Your App → Settings

### Allowed Callback URLs
Add these URLs (comma-separated):
```
http://localhost:8080/web/,https://mystical-mentor.beautiful-apps.com/web/
```

### Allowed Logout URLs  
Add these URLs (comma-separated):
```
http://localhost:8080/web/,https://mystical-mentor.beautiful-apps.com/web/
```

### Allowed Web Origins
Add these URLs (comma-separated):
```
http://localhost:8080,https://mystical-mentor.beautiful-apps.com
```

### Allowed Origins (CORS)
Add these URLs (comma-separated):
```
http://localhost:8080,https://mystical-mentor.beautiful-apps.com
```

## Current Configuration
- **Domain**: `dev-d2dttzao1vs6jrmf.us.auth0.com`
- **Client ID**: `TTfc367IPClXNSrHO00zbzuWgv732bl3`
- **Redirect URI**: `http://localhost:8080/web/` (for local development)

## Testing Steps
1. Update Auth0 Dashboard with the URLs above
2. Go to `http://localhost:8080/web/`
3. Click "Sign In"
4. Complete Auth0 login
5. You should be redirected back to `/web/` and logged in

## Troubleshooting
- If you get "Callback URL mismatch", double-check the URLs in Auth0 Dashboard
- Make sure there are no extra spaces or typos in the URLs
- The URLs must match exactly (including trailing slashes) 