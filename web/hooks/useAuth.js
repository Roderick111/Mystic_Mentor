/**
 * useAuth.js - Authentication State Hook
 * Purpose: Provides authentication state and methods to React components.
 * Manages Auth0 state changes and provides login/logout functionality.
 */
const { useState, useEffect } = React;

const useAuth = () => {
    const [authState, setAuthState] = useState({
        isAuthenticated: false,
        isLoading: true,
        user: null,
        error: null
    });

    useEffect(() => {
        // Check if auth0Service is available
        if (!window.auth0Service) {
            console.error('Auth0 service not available');
            setAuthState(prev => ({ ...prev, isLoading: false, error: 'Auth service unavailable' }));
            return;
        }

        // Initial auth state
        const initialState = window.auth0Service.getAuthStatus();
        setAuthState({
            isAuthenticated: initialState.isAuthenticated,
            isLoading: false,
            user: initialState.user,
            error: null
        });

        // Listen for auth state changes
        const handleAuthStateChange = (newState) => {
            setAuthState({
                isAuthenticated: newState.isAuthenticated,
                isLoading: false,
                user: newState.user,
                error: null
            });
        };

        window.auth0Service.onAuthStateChange(handleAuthStateChange);

        // Cleanup listener on unmount
        return () => {
            if (window.auth0Service) {
                window.auth0Service.removeAuthStateListener(handleAuthStateChange);
            }
        };
    }, []);

    // Authentication methods
    const login = () => {
        if (window.auth0Service) {
            window.auth0Service.login();
        } else {
            console.error('Auth0 service not available');
        }
    };

    const logout = () => {
        if (window.auth0Service) {
            window.auth0Service.logout();
        } else {
            console.error('Auth0 service not available');
        }
    };

    const getAccessToken = async () => {
        if (window.auth0Service) {
            return await window.auth0Service.getAccessToken();
        }
        return null;
    };

    return {
        // State
        isAuthenticated: authState.isAuthenticated,
        isLoading: authState.isLoading,
        user: authState.user,
        error: authState.error,
        
        // Methods
        login,
        logout,
        getAccessToken
    };
};

// Export the hook
window.useAuth = useAuth; 