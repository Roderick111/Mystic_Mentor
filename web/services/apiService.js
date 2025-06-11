/**
 * apiService.js - Backend Communication Layer
 * Purpose: Centralized HTTP client for all API calls with unified error handling.
 * Single source of truth for backend communication and request/response processing.
 */
class ApiService {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    // Helper method for making HTTP requests
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    }

    // System Status API
    async fetchSystemStatus() {
        try {
            return await this.makeRequest('/status');
        } catch (error) {
            console.error('Error fetching system status:', error);
            throw error;
        }
    }

    // Sessions API
    async fetchSessions() {
        try {
            return await this.makeRequest(`/sessions?_t=${Date.now()}`, {
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
        } catch (error) {
            console.error('Error fetching sessions:', error);
            throw error;
        }
    }

    async loadSessionMessages(sessionId) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}/history?_t=${Date.now()}`, {
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
        } catch (error) {
            console.error(`Error loading session messages for ${sessionId}:`, error);
            throw error;
        }
    }

    async updateSessionTitle(sessionId, title) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}/title`, {
                method: 'PUT',
                body: JSON.stringify({ title })
            });
        } catch (error) {
            console.error('Error updating session title:', error);
            throw error;
        }
    }

    async archiveSession(sessionId) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}/archive`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error archiving session:', error);
            throw error;
        }
    }

    async deleteSession(sessionId) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Error deleting session:', error);
            throw error;
        }
    }

    async fetchArchivedSessions() {
        try {
            return await this.makeRequest(`/sessions/archived?_t=${Date.now()}`, {
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
        } catch (error) {
            console.error('Error fetching archived sessions:', error);
            throw error;
        }
    }

    async unarchiveSession(sessionId) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}/unarchive`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error unarchiving session:', error);
            throw error;
        }
    }

    // Chat API
    async sendMessage(message, sessionId = null) {
        try {
            return await this.makeRequest('/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    // Domain API
    async toggleDomain(domainName, enable) {
        try {
            return await this.makeRequest(`/domains/${domainName}/toggle?enable=${enable}`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error toggling domain:', error);
            throw error;
        }
    }

    // Lunar API
    async fetchLunarInfo() {
        try {
            return await this.makeRequest('/lunar');
        } catch (error) {
            console.error('Error fetching lunar information:', error);
            throw error;
        }
    }
}

// Create a default instance for easy importing
const apiService = new ApiService();

// Export both the class and the default instance
window.ApiService = ApiService;
window.apiService = apiService; 