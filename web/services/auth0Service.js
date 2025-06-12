/**
 * auth0Service.js - Auth0 Authentication Service
 * Purpose: Handles Auth0 authentication flow, token management, and user state.
 * Provides login, logout, and authentication status checking for the web interface.
 */
class Auth0Service {
    constructor() {
        // Your Auth0 configuration
        this.domain = 'dev-d2dttzao1vs6jrmf.us.auth0.com';
        this.clientId = 'TTfc367IPClXNSrHO00zbzuWgv732bl3';
        this.audience = 'https://dev-d2dttzao1vs6jrmf.us.auth0.com/api/v2/';
        this.redirectUri = window.location.origin;
        
        // State management
        this.isAuthenticated = false;
        this.user = null;
        this.accessToken = null;
        this.tokenExpiresAt = null;
        
        // Event listeners for auth state changes
        this.authStateListeners = [];
        
        // Initialize on construction
        this.init();
    }

    // Initialize Auth0 service
    async init() {
        // Check for tokens in URL (after redirect)
        this.handleAuthCallback();
        
        // Check for existing session
        await this.checkSession();
    }

    // Add listener for auth state changes
    onAuthStateChange(callback) {
        this.authStateListeners.push(callback);
    }

    // Remove auth state listener
    removeAuthStateListener(callback) {
        this.authStateListeners = this.authStateListeners.filter(cb => cb !== callback);
    }

    // Notify all listeners of auth state changes
    notifyAuthStateChange() {
        this.authStateListeners.forEach(callback => {
            callback({
                isAuthenticated: this.isAuthenticated,
                user: this.user,
                accessToken: this.accessToken
            });
        });
    }

    // Check if user has valid session
    async checkSession() {
        const token = localStorage.getItem('auth0_access_token');
        const expiresAt = localStorage.getItem('auth0_expires_at');
        const userStr = localStorage.getItem('auth0_user');

        if (token && expiresAt && userStr) {
            const now = Date.now();
            const expiration = parseInt(expiresAt);

            if (now < expiration) {
                // Token is still valid
                this.accessToken = token;
                this.tokenExpiresAt = expiration;
                this.user = JSON.parse(userStr);
                this.isAuthenticated = true;
                this.notifyAuthStateChange();
                return true;
            } else {
                // Token expired, clear storage
                this.clearSession();
            }
        }

        return false;
    }

    // Handle Auth0 callback after login
    handleAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const fragment = new URLSearchParams(window.location.hash.substring(1));
        
        // Check for access token in URL fragment (implicit flow)
        const accessToken = fragment.get('access_token');
        const idToken = fragment.get('id_token');
        const expiresIn = fragment.get('expires_in');
        const error = urlParams.get('error') || fragment.get('error');

        if (error) {
            console.error('Auth0 error:', error);
            const errorDescription = urlParams.get('error_description') || fragment.get('error_description');
            throw new Error(`Authentication failed: ${errorDescription || error}`);
        }

        if (accessToken && idToken) {
            // Parse the ID token to get user info
            try {
                const userInfo = this.parseJWT(idToken);
                const expiresAt = Date.now() + (parseInt(expiresIn) * 1000);

                // Store tokens and user info
                this.accessToken = accessToken;
                this.tokenExpiresAt = expiresAt;
                this.user = {
                    sub: userInfo.sub,
                    email: userInfo.email,
                    name: userInfo.name,
                    picture: userInfo.picture,
                    email_verified: userInfo.email_verified
                };
                this.isAuthenticated = true;

                // Save to localStorage
                localStorage.setItem('auth0_access_token', accessToken);
                localStorage.setItem('auth0_expires_at', expiresAt.toString());
                localStorage.setItem('auth0_user', JSON.stringify(this.user));

                // Clean up URL
                window.history.replaceState({}, document.title, window.location.pathname);

                // Notify listeners
                this.notifyAuthStateChange();

                return true;
            } catch (error) {
                console.error('Error parsing auth response:', error);
                throw error;
            }
        }

        return false;
    }

    // Parse JWT token (simple base64 decode - for ID token only)
    parseJWT(token) {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        return JSON.parse(jsonPayload);
    }

    // Login with Auth0
    login() {
        const params = new URLSearchParams({
            response_type: 'token id_token',
            client_id: this.clientId,
            redirect_uri: this.redirectUri,
            scope: 'openid profile email',
            audience: this.audience,
            nonce: this.generateNonce(),
            state: this.generateState()
        });

        const authUrl = `https://${this.domain}/authorize?${params.toString()}`;
        window.location.href = authUrl;
    }

    // Logout
    logout() {
        // Clear local session
        this.clearSession();

        // Redirect to Auth0 logout
        const params = new URLSearchParams({
            client_id: this.clientId,
            returnTo: this.redirectUri
        });

        const logoutUrl = `https://${this.domain}/v2/logout?${params.toString()}`;
        window.location.href = logoutUrl;
    }

    // Clear local session
    clearSession() {
        this.isAuthenticated = false;
        this.user = null;
        this.accessToken = null;
        this.tokenExpiresAt = null;

        // Clear localStorage
        localStorage.removeItem('auth0_access_token');
        localStorage.removeItem('auth0_expires_at');
        localStorage.removeItem('auth0_user');

        // Notify listeners
        this.notifyAuthStateChange();
    }

    // Check if token is expired
    isTokenExpired() {
        if (!this.tokenExpiresAt) return true;
        return Date.now() >= this.tokenExpiresAt;
    }

    // Get current access token (refresh if needed)
    async getAccessToken() {
        if (!this.isAuthenticated || this.isTokenExpired()) {
            return null;
        }
        return this.accessToken;
    }

    // Get user info
    getUser() {
        return this.user;
    }

    // Get authentication status
    getAuthStatus() {
        return {
            isAuthenticated: this.isAuthenticated,
            user: this.user,
            isLoading: false
        };
    }

    // Generate random nonce for security
    generateNonce() {
        return Array.from(crypto.getRandomValues(new Uint8Array(16)))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    // Generate random state for security
    generateState() {
        return Array.from(crypto.getRandomValues(new Uint8Array(16)))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    // Get authorization header for API calls
    getAuthHeader() {
        if (this.accessToken && !this.isTokenExpired()) {
            return { 'Authorization': `Bearer ${this.accessToken}` };
        }
        return {};
    }
}

// Create a default instance
const auth0Service = new Auth0Service();

// Export both class and instance
window.Auth0Service = Auth0Service;
window.auth0Service = auth0Service; 