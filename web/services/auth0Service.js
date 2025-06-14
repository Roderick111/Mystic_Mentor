/**
 * auth0Service.js - Auth0 Authentication Service
 * Purpose: Handles Auth0 authentication flow, token management, and user state.
 * Provides login, logout, and authentication status checking for the web interface.
 */
// Auth0 SPA SDK wrapper for React SPA (no build step, uses CDN SDK)
window.auth0Client = null;
window.auth0InitPromise = null;
window.auth0InitError = null;
window.auth0Ready = false;

// Wait for Auth0 SDK to be available
async function waitForAuth0SDK() {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 20; // Increased attempts
    const checkInterval = 250; // Check every 250ms
    
    const checkAuth0 = () => {
      attempts++;
      console.log(`🔍 Checking Auth0 SDK availability (attempt ${attempts}/${maxAttempts})...`);
      
      if (typeof auth0 !== 'undefined' && auth0.createAuth0Client) {
        console.log('✅ Auth0 SDK is available');
        resolve(true);
      } else if (attempts >= maxAttempts) {
        const error = new Error(`Auth0 SDK not available after ${maxAttempts} attempts. Please check your internet connection and refresh the page.`);
        console.error('❌ Auth0 SDK timeout:', error);
        reject(error);
      } else {
        console.log(`⏳ Auth0 SDK not ready yet, retrying in ${checkInterval}ms...`);
        setTimeout(checkAuth0, checkInterval);
      }
    };
    
    checkAuth0();
  });
}

async function initAuth0() {
  // Prevent multiple initialization attempts
  if (window.auth0InitPromise) {
    return window.auth0InitPromise;
  }

  console.log('🚀 Starting Auth0 initialization...');

  window.auth0InitPromise = (async () => {
    try {
      // Step 1: Wait for Auth0 SDK to be available
      await waitForAuth0SDK();
      
      // Step 2: Validate Auth0 SDK
      if (typeof auth0 === 'undefined') {
        throw new Error('Auth0 global object not found after SDK load');
      }
      
      if (!auth0.createAuth0Client) {
        throw new Error('Auth0.createAuth0Client method not available');
      }

      // Step 3: Configure and create Auth0 client
      const redirectUri = `${window.location.origin}/web/`;

      // Create Auth0 client with CORS-friendly configuration
      window.auth0Client = await auth0.createAuth0Client({
        domain: 'dev-d2dttzao1vs6jrmf.us.auth0.com',
        clientId: 'TTfc367IPClXNSrHO00zbzuWgv732bl3',
        audience: 'https://mystical-mentor-api',
        cacheLocation: 'localstorage',
        useRefreshTokens: true,
        // Skip CORS preflight checks where possible
        skipRedirectCallback: false,
        authorizationParams: {
          redirect_uri: redirectUri,
          scope: 'openid profile email',
          // Force JWT tokens by explicitly requesting the audience
          audience: 'https://mystical-mentor-api'
        }
      });

      // Step 4: Validate client creation
      if (!window.auth0Client) {
        throw new Error('Auth0 client creation returned null/undefined');
      }

      // Step 5: Test basic functionality (skip network-dependent tests)
      try {
        const testResult = await window.auth0Client.isAuthenticated();
      } catch (testError) {
        console.warn('⚠️ Auth0 client test failed, but continuing:', testError);
        // Don't fail initialization for test issues - CORS might block this
      }

      // Step 6: Handle redirect callback if present
      if (window.location.search.includes('code=') && window.location.search.includes('state=')) {
        console.log('🔄 Processing Auth0 callback...');
        
        try {
          // Add timeout to prevent hanging on CORS issues
          const callbackPromise = window.auth0Client.handleRedirectCallback();
          const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Callback timeout - possible CORS issue')), 10000)
          );
          
          const result = await Promise.race([callbackPromise, timeoutPromise]);
          console.log('✅ Auth0 callback processed:', result);
          
          // Clean up URL
          window.history.replaceState({}, document.title, '/web/');
          
          // Refresh page to update auth state
          setTimeout(() => {
            window.location.reload();
          }, 100);
        } catch (callbackError) {
          console.error('❌ Auth0 callback error:', callbackError);
          
          // Check if it's a CORS/network issue
          const isCorsIssue = callbackError.message.includes('fetch') || 
                             callbackError.message.includes('CORS') || 
                             callbackError.message.includes('timeout') ||
                             callbackError.message.includes('Network');
          
          if (isCorsIssue) {
            console.log('🌐 Detected CORS/network issue, trying alternative approach...');
            
            // For CORS issues, try to manually check authentication after a delay
            // The tokens might have been stored despite the error
            setTimeout(async () => {
              try {
                const isAuth = await window.auth0Client.isAuthenticated();
                if (isAuth) {
                  console.log('✅ Authentication successful! Reloading page...');
                  window.location.reload();
                  return;
                }
              } catch (checkError) {
                console.log('❌ Authentication check failed:', checkError);
              }
              
              // If still not authenticated, show error
              alert('Login callback failed due to network restrictions. Please try again or use a different network connection.');
            }, 2000);
          } else {
            // For other errors, show generic message
            alert('Login callback failed. Please try logging in again.');
          }
          
          // Clean up URL regardless
          window.history.replaceState({}, document.title, '/web/');
        }
      }

      // Step 7: Mark as ready
      window.auth0Ready = true;
      console.log('✅ Auth0 initialization completed successfully!');
      
      return window.auth0Client;
    } catch (error) {
      console.error('❌ Auth0 initialization failed:', error);
      window.auth0InitError = error;
      window.auth0Ready = false;
      throw error;
    }
  })();

  return window.auth0InitPromise;
}

// Make initAuth0 globally available
window.initAuth0 = initAuth0;

// Enhanced state getter with better error handling
window.getAuth0State = async function() {
  try {
    // Wait for initialization if it's in progress
    if (window.auth0InitPromise && !window.auth0Ready) {
      try {
        await window.auth0InitPromise;
      } catch (initError) {
        console.error('❌ Auth0 initialization failed during state check:', initError);
        return { 
          isAuthenticated: false, 
          user: null, 
          accessToken: null, 
          error: initError
        };
      }
    }
    
    if (!window.auth0Client) {
      const error = window.auth0InitError || new Error('Auth0 client not initialized');
      console.error('❌ Auth0 client not available:', error);
      return { 
        isAuthenticated: false, 
        user: null, 
        accessToken: null, 
        error
      };
    }
    
    const isAuthenticated = await window.auth0Client.isAuthenticated();
    
    let user = null;
    let accessToken = null;
    
    if (isAuthenticated) {
      try {
        user = await window.auth0Client.getUser();
        accessToken = await window.auth0Client.getTokenSilently();
      } catch (tokenError) {
        console.warn('⚠️ Failed to get user info or token:', tokenError);
        // Don't fail the whole state check for token issues - might be CORS related
      }
    }
    
    const state = { isAuthenticated, user, accessToken, error: null };
    return state;
  } catch (error) {
    console.error('❌ Error getting Auth0 state:', error);
    return { isAuthenticated: false, user: null, accessToken: null, error };
  }
};

// Enhanced login with better error handling
window.auth0Login = async function() {
  try {
    console.log('🚀 Starting login process...');
    
    // Wait for initialization if needed
    if (window.auth0InitPromise && !window.auth0Ready) {
      console.log('⏳ Waiting for Auth0 to initialize before login...');
      await window.auth0InitPromise;
    }
    
    if (!window.auth0Client) {
      throw new Error('Auth0 client not initialized. Please refresh the page and try again.');
    }
    
    console.log('🔐 Redirecting to Auth0 login...');
    // This should work even with CORS issues since it's a redirect
    await window.auth0Client.loginWithRedirect();
  } catch (error) {
    console.error('❌ Login error:', error);
    
    let userMessage = 'Login failed. ';
    if (error.message.includes('not initialized')) {
      userMessage += 'Please refresh the page and try again.';
    } else if (error.message.includes('network') || error.message.includes('fetch')) {
      userMessage += 'Please check your internet connection and try again.';
    } else {
      userMessage += 'Please try again or contact support if the issue persists.';
    }
    
    alert(userMessage);
  }
};

// Enhanced logout with better error handling
window.auth0Logout = async function() {
  try {
    console.log('👋 Starting logout process...');
    
    // Wait for initialization if needed
    if (window.auth0InitPromise && !window.auth0Ready) {
      console.log('⏳ Waiting for Auth0 to initialize before logout...');
      await window.auth0InitPromise;
    }
    
    if (!window.auth0Client) {
      throw new Error('Auth0 client not initialized. Please refresh the page and try again.');
    }
    
    const returnTo = `${window.location.origin}/web/`;
    console.log('🔗 Logging out with return URL:', returnTo);
    
    // This should work even with CORS issues since it's a redirect
    await window.auth0Client.logout({ 
      logoutParams: { 
        returnTo: returnTo
      } 
    });
  } catch (error) {
    console.error('❌ Logout error:', error);
    
    let userMessage = 'Logout failed. ';
    if (error.message.includes('not initialized')) {
      userMessage += 'Please refresh the page and try again.';
    } else {
      userMessage += 'Please try again or contact support if the issue persists.';
    }
    
    alert(userMessage);
  }
};

// Enhanced debug helper
window.debugAuth0 = function() {
  console.log('🔍 Auth0 Debug Info:');
  console.log('- auth0 global:', typeof auth0 !== 'undefined' ? '✅ Available' : '❌ Missing');
  console.log('- auth0.createAuth0Client:', typeof auth0 !== 'undefined' && auth0.createAuth0Client ? '✅ Available' : '❌ Missing');
  console.log('- auth0Client:', window.auth0Client ? '✅ Initialized' : '❌ Not initialized');
  console.log('- auth0Ready:', window.auth0Ready ? '✅ Ready' : '❌ Not ready');
  console.log('- initPromise:', window.auth0InitPromise ? '✅ Present' : '❌ Missing');
  console.log('- initError:', window.auth0InitError || 'None');
  console.log('- Current URL:', window.location.href);
  console.log('- Has callback params:', window.location.search.includes('code=') && window.location.search.includes('state='));
  console.log('- Expected redirect URI:', `${window.location.origin}/web/`);
  
  // Test direct login URL
  const directLoginUrl = 'https://dev-d2dttzao1vs6jrmf.us.auth0.com/authorize?' + 
    'client_id=TTfc367IPClXNSrHO00zbzuWgv732bl3&' +
    'redirect_uri=' + encodeURIComponent(`${window.location.origin}/web/`) + '&' +
    'scope=openid+profile+email&' +
    'response_type=code&' +
    'state=debug-test-' + Date.now();
  
  console.log('🔗 Direct login URL (copy and test in new tab):');
  console.log(directLoginUrl);
  
  return {
    auth0Global: typeof auth0 !== 'undefined',
    auth0CreateClient: typeof auth0 !== 'undefined' && !!auth0.createAuth0Client,
    auth0Client: !!window.auth0Client,
    auth0Ready: window.auth0Ready,
    initPromise: !!window.auth0InitPromise,
    initError: window.auth0InitError,
    currentUrl: window.location.href,
    hasCallbackParams: window.location.search.includes('code=') && window.location.search.includes('state='),
    expectedRedirectUri: `${window.location.origin}/web/`,
    directLoginUrl: directLoginUrl
  };
};

// Comprehensive Auth0 cache clearing function
window.clearAuth0CacheAndReauth = async function() {
  console.log('🧹 Starting comprehensive Auth0 cache clearing...');
  
  try {
    // Step 1: Clear all localStorage entries related to Auth0
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (
        key.includes('auth0') || 
        key.includes('@@auth0spajs@@') ||
        key.includes('a0.spajs') ||
        key.includes('auth0.') ||
        key.includes('Auth0')
      )) {
        keysToRemove.push(key);
      }
    }
    
    console.log(`🗑️ Removing ${keysToRemove.length} Auth0 localStorage entries:`, keysToRemove);
    keysToRemove.forEach(key => localStorage.removeItem(key));
    
    // Step 2: Clear sessionStorage as well
    const sessionKeysToRemove = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      if (key && (
        key.includes('auth0') || 
        key.includes('@@auth0spajs@@') ||
        key.includes('a0.spajs') ||
        key.includes('auth0.') ||
        key.includes('Auth0')
      )) {
        sessionKeysToRemove.push(key);
      }
    }
    
    console.log(`🗑️ Removing ${sessionKeysToRemove.length} Auth0 sessionStorage entries:`, sessionKeysToRemove);
    sessionKeysToRemove.forEach(key => sessionStorage.removeItem(key));
    
    // Step 3: Reset Auth0 global state
    window.auth0Client = null;
    window.auth0InitPromise = null;
    window.auth0InitError = null;
    window.auth0Ready = false;
    
    console.log('🔄 Reset Auth0 global state');
    
    // Step 4: Force logout from Auth0 domain (this clears server-side session)
    const logoutUrl = 'https://dev-d2dttzao1vs6jrmf.us.auth0.com/v2/logout?' +
      'client_id=TTfc367IPClXNSrHO00zbzuWgv732bl3&' +
      'returnTo=' + encodeURIComponent(`${window.location.origin}/web/`);
    
    console.log('🚪 Redirecting to Auth0 logout to clear server session...');
    console.log('Logout URL:', logoutUrl);
    
    // Redirect to logout, which will then redirect back to our app
    window.location.href = logoutUrl;
    
  } catch (error) {
    console.error('❌ Error during cache clearing:', error);
    alert('Cache clearing failed. Please manually clear your browser cache and try again.');
  }
};

// Force fresh login with JWT tokens
window.forceJWTLogin = async function() {
  console.log('🔐 Starting forced JWT login...');
  
  // Clear all cache first
  await window.clearAuth0CacheAndReauth();
  
  // The logout redirect will bring us back, then we can login fresh
};

// Console helper for easy access
console.log('🔧 Auth0 Debug Commands Available:');
console.log('- window.clearAuth0CacheAndReauth() - Clear all Auth0 cache and force logout/login');
console.log('- window.forceJWTLogin() - Same as above, but with clearer name');
console.log('- window.debugAuth0() - Show detailed Auth0 debug information');
console.log('- window.getAuth0State() - Get current authentication state');
console.log('💡 Quick fix for opaque tokens: Run "clearAuth0CacheAndReauth()" in console'); 