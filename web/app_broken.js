const { useState, useEffect, useRef } = React;

// API base URL - update this to match your server
const API_BASE = 'http://localhost:8000';

// Main Chat Application Component
function App() {
    // State management
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [systemStatus, setSystemStatus] = useState(null);
    const [activeTab, setActiveTab] = useState('chat');
    const [lunarInfo, setLunarInfo] = useState(null);
    
    // Refs
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Scroll to bottom of messages
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Fetch system status
    const fetchSystemStatus = async () => {
        try {
            const response = await fetch(`${API_BASE}/status`);
            const data = await response.json();
            setSystemStatus(data);
        } catch (error) {
            console.error('Error fetching system status:', error);
        }
    };

    // Fetch lunar information
    const fetchLunarInfo = async () => {
        try {
            const response = await fetch(`${API_BASE}/lunar`);
            const data = await response.json();
            setLunarInfo(data);
        } catch (error) {
            console.error('Error fetching lunar info:', error);
        }
    };

    // Fetch sessions
    const fetchSessions = async () => {
        try {
            // Add cache-busting parameter to prevent stale data
            const response = await fetch(`${API_BASE}/sessions?_t=${Date.now()}`);
            const data = await response.json();
            console.log('Fetched sessions:', data); // Debug logging
            setSessions(data);
        } catch (error) {
            console.error('Error fetching sessions:', error);
        }
    };

    // Initial data load
    useEffect(() => {
        fetchSystemStatus();
        fetchLunarInfo();
        fetchSessions();
    }, []);

    // Load session history automatically when switching to a session with existing messages
    useEffect(() => {
        if (currentSessionId && sessions.length > 0) {
            // Check if this session exists in our sessions list and has messages
            const existingSession = sessions.find(s => s.session_id === currentSessionId);
            if (existingSession && existingSession.message_count > 0 && messages.length === 0) {
                console.log('Auto-loading history for session:', currentSessionId);
                
                // Load history without triggering session refresh to avoid infinite loop
                const loadHistoryOnly = async () => {
                    try {
                        const response = await fetch(`${API_BASE}/sessions/${currentSessionId}/history?_t=${Date.now()}`);
                        if (response.ok) {
                            const data = await response.json();
                            console.log('Auto-loaded session history:', data);
                            
                            const formattedMessages = data.messages.map(msg => ({
                                role: msg.role,
                                content: msg.content,
                                timestamp: msg.timestamp || new Date().toISOString(),
                                metadata: msg.metadata || {}
                            }));
                            
                            setMessages(formattedMessages);
                        }
                    } catch (error) {
                        console.error('Error auto-loading session history:', error);
                    }
                };
                
                loadHistoryOnly();
            }
        }
    }, [currentSessionId, sessions, messages.length]);

    // Send message to chat API
    const sendMessage = async (message) => {
        if (!message.trim()) return;

        const userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: currentSessionId,
                }),
            });

            const data = await response.json();
            
            if (response.ok) {
                const assistantMessage = {
                    role: 'assistant',
                    content: data.response,
                    timestamp: data.timestamp,
                    metadata: {
                        message_type: data.message_type,
                        rag_used: data.rag_used,
                        cache_hit: data.cache_hit,
                    }
                };

                setMessages(prev => [...prev, assistantMessage]);
                setCurrentSessionId(data.session_id);
            } else {
                throw new Error(data.detail || 'Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                role: 'assistant',
                content: `❌ Error: ${error.message}`,
                timestamp: new Date().toISOString(),
                isError: true,
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();
        sendMessage(inputValue);
    };

    // Toggle domain
    const toggleDomain = async (domainName, enable) => {
        try {
            const response = await fetch(`${API_BASE}/domains/${domainName}/toggle?enable=${enable}`, {
                method: 'POST',
            });
            
            if (response.ok) {
                fetchSystemStatus(); // Refresh status
            }
        } catch (error) {
            console.error('Error toggling domain:', error);
        }
    };

    // Create new session
    const createNewSession = async () => {
        try {
            // Clear current messages and session
            setMessages([]);
            setCurrentSessionId(null);
            
            // Refresh sessions list to show the new session will be created
            await fetchSessions();
            
        } catch (error) {
            console.error('Error creating new session:', error);
        }
    };

    // Load messages for a specific session
    const loadSessionMessages = async (sessionId) => {
        console.log('Loading session messages for:', sessionId);
        
        // First, switch to the session immediately and clear messages
        setCurrentSessionId(sessionId);
        setMessages([]);
        
        try {
            // Add cache-busting parameter to ensure fresh data
            const response = await fetch(`${API_BASE}/sessions/${sessionId}/history?_t=${Date.now()}`);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Session history loaded:', data);
                
                // Transform API response to match our message format
                const formattedMessages = data.messages.map(msg => ({
                    role: msg.role,
                    content: msg.content,
                    timestamp: msg.timestamp || new Date().toISOString(),
                    metadata: msg.metadata || {}
                }));
                
                console.log('Formatted messages:', formattedMessages);
                setMessages(formattedMessages);
                
            } else if (response.status === 404) {
                console.log('Session not found, treating as new session');
                // Session not found, keep it as a new session with empty messages
            } else {
                console.error('Error loading session history:', response.status, response.statusText);
                // Other error, keep empty messages
            }
            
        } catch (error) {
            console.error('Error loading session messages:', error);
            // Keep empty messages on error
        }
        
        // Refresh sessions list to ensure we have the latest data
        await fetchSessions();
    };

    // Execute command
    const executeCommand = async (command) => {
        try {
            const response = await fetch(`${API_BASE}/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    session_id: currentSessionId,
                }),
            });

            const data = await response.json();
            console.log('Command result:', data);
            
            // Refresh relevant data
            if (command.startsWith('session')) {
                fetchSessions();
            }
        } catch (error) {
            console.error('Error executing command:', error);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Header */}
            <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <span className="text-2xl">🌙</span>
                        <h1 className="text-xl font-bold">Esoteric AI Agent</h1>
                    </div>
                    <div className="flex space-x-2">
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`px-3 py-1 rounded text-sm ${
                                activeTab === 'chat' 
                                    ? 'bg-blue-600 text-white' 
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                        >
                            Chat
                        </button>
                        <button
                            onClick={() => setActiveTab('settings')}
                            className={`px-3 py-1 rounded text-sm ${
                                activeTab === 'settings' 
                                    ? 'bg-blue-600 text-white' 
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                        >
                            Settings
                        </button>
                        <button
                            onClick={() => setActiveTab('lunar')}
                            className={`px-3 py-1 rounded text-sm ${
                                activeTab === 'lunar' 
                                    ? 'bg-blue-600 text-white' 
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                        >
                            Lunar
                        </button>
                    </div>
                </div>
            </header>

            <div className="flex h-screen">
                {/* Sidebar */}
                <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
                    {/* Session Info */}
                    <div className="p-4 border-b border-gray-700">
                        <h3 className="text-sm font-semibold text-gray-400 mb-2">Current Session</h3>
                        <div className="text-xs text-gray-500">
                            {currentSessionId ? (
                                <span>ID: {currentSessionId.slice(0, 8)}...</span>
                            ) : (
                                <span>No active session</span>
                            )}
                        </div>
                        <button
                            onClick={createNewSession}
                            className="mt-2 w-full px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                        >
                            New Session
                        </button>
                    </div>

                    {/* System Status */}
                    {systemStatus && (
                        <div className="p-4 border-b border-gray-700">
                            <h3 className="text-sm font-semibold text-gray-400 mb-2">System Status</h3>
                            <div className="space-y-1 text-xs">
                                <div>Documents: {systemStatus.total_documents}</div>
                                <div>Cache: {systemStatus.cache_size} entries</div>
                                <div className="flex items-center space-x-2">
                                    <span>Short Memory:</span>
                                    <span className={`px-1 rounded ${
                                        systemStatus.memory_enabled.short_term 
                                            ? 'bg-green-600' : 'bg-red-600'
                                    }`}>
                                        {systemStatus.memory_enabled.short_term ? 'ON' : 'OFF'}
                                    </span>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <span>Medium Memory:</span>
                                    <span className={`px-1 rounded ${
                                        systemStatus.memory_enabled.medium_term 
                                            ? 'bg-green-600' : 'bg-red-600'
                                    }`}>
                                        {systemStatus.memory_enabled.medium_term ? 'ON' : 'OFF'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Active Domains */}
                    {systemStatus && (
                        <div className="p-4 border-b border-gray-700">
                            <h3 className="text-sm font-semibold text-gray-400 mb-2">Active Domains</h3>
                            <div className="space-y-1">
                                {systemStatus.available_domains.map(domain => (
                                    <div key={domain} className="flex items-center justify-between text-xs">
                                        <span className="capitalize">{domain}</span>
                                        <button
                                            onClick={() => toggleDomain(domain, !systemStatus.active_domains.includes(domain))}
                                            className={`px-2 py-1 rounded text-xs ${
                                                systemStatus.active_domains.includes(domain)
                                                    ? 'bg-green-600 hover:bg-green-700'
                                                    : 'bg-gray-600 hover:bg-gray-500'
                                            }`}
                                        >
                                            {systemStatus.active_domains.includes(domain) ? 'ON' : 'OFF'}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Recent Sessions */}
                    <div className="p-4 flex-1 overflow-y-auto">
                        <h3 className="text-sm font-semibold text-gray-400 mb-2">Recent Sessions</h3>
                        <div className="space-y-2">
                            {sessions.slice(0, 5).map((session, index) => {
                                console.log(`Session ${index}:`, session); // Debug logging
                                return (
                                    <div 
                                        key={session.session_id}
                                        className={`p-2 rounded cursor-pointer text-xs border ${
                                            session.session_id === currentSessionId
                                                ? 'border-blue-500 bg-blue-900/30'
                                                : 'border-gray-600 hover:border-gray-500'
                                        }`}
                                        onClick={() => {
                                            console.log('Clicking session:', session.session_id); // Debug logging
                                            loadSessionMessages(session.session_id);
                                        }}
                                    >
                                        <div className="font-medium">{session.session_id.slice(0, 8)}...</div>
                                        <div className="text-gray-500">{session.message_count} messages</div>
                                        <div className="text-gray-500">
                                            {new Date(session.last_activity).toLocaleDateString()}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1 flex flex-col">
                    {activeTab === 'chat' && (
                        <>
                            {/* Messages Area */}
                            <div className="flex-1 overflow-y-auto p-4 chat-scroll">
                                <div className="max-w-4xl mx-auto space-y-4">
                                    {messages.length === 0 && (
                                        <div className="text-center text-gray-500 py-8">
                                            <span className="text-4xl mb-4 block">🌙</span>
                                            <p>Welcome to the Esoteric AI Agent</p>
                                            <p className="text-sm mt-2">Ask me about emotions, spirituality, lunar phases, or seek guidance</p>
                                        </div>
                                    )}
                                    
                                    {messages.map((message, index) => (
                                        <div
                                            key={index}
                                            className={`flex ${
                                                message.role === 'user' ? 'justify-end' : 'justify-start'
                                            }`}
                                        >
                                            <div
                                                className={`max-w-3xl px-4 py-3 rounded-lg ${
                                                    message.role === 'user'
                                                        ? 'bg-blue-600 text-white'
                                                        : message.isError
                                                        ? 'bg-red-900 text-red-100 border border-red-700'
                                                        : 'bg-gray-700 text-gray-100'
                                                }`}
                                            >
                                                <div className="whitespace-pre-wrap">{message.content}</div>
                                                
                                                {/* Message metadata */}
                                                {message.metadata && (
                                                    <div className="mt-2 pt-2 border-t border-gray-600 flex space-x-3 text-xs text-gray-400">
                                                        <span className={`px-1 rounded ${
                                                            message.metadata.message_type === 'emotional' 
                                                                ? 'bg-purple-600' : 'bg-blue-600'
                                                        }`}>
                                                            {message.metadata.message_type}
                                                        </span>
                                                        {message.metadata.rag_used && (
                                                            <span className="px-1 bg-green-600 rounded">RAG</span>
                                                        )}
                                                        {message.metadata.cache_hit && (
                                                            <span className="px-1 bg-yellow-600 rounded">Cache</span>
                                                        )}
                                                    </div>
                                                )}
                                                
                                                <div className="mt-1 text-xs text-gray-500">
                                                    {new Date(message.timestamp).toLocaleTimeString()}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    
                                    {isLoading && (
                                        <div className="flex justify-start">
                                            <div className="bg-gray-700 px-4 py-3 rounded-lg">
                                                <div className="flex space-x-1">
                                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                    
                                    <div ref={messagesEndRef} />
                                </div>
                            </div>

                            {/* Input Area */}
                            <div className="border-t border-gray-700 p-4">
                                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                                    <div className="flex space-x-3">
                                        <input
                                            ref={inputRef}
                                            type="text"
                                            value={inputValue}
                                            onChange={(e) => setInputValue(e.target.value)}
                                            placeholder="Share your thoughts, ask for guidance..."
                                            className="flex-1 px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white placeholder-gray-400"
                                            disabled={isLoading}
                                        />
                                        <button
                                            type="submit"
                                            disabled={isLoading || !inputValue.trim()}
                                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-medium transition-colors"
                                        >
                                            Send
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </>
                    )}

                    {activeTab === 'settings' && (
                        <div className="flex-1 p-6 overflow-y-auto">
                            <div className="max-w-2xl mx-auto space-y-6">
                                <h2 className="text-2xl font-bold mb-6">Settings</h2>
                                
                                {/* Memory Settings */}
                                <div className="bg-gray-800 rounded-lg p-6">
                                    <h3 className="text-lg font-semibold mb-4">Memory Settings</h3>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <div className="font-medium">Short-term Memory</div>
                                                <div className="text-sm text-gray-400">Recent conversation context</div>
                                            </div>
                                            <button
                                                onClick={() => executeCommand(systemStatus?.memory_enabled.short_term ? 'memory disable short' : 'memory enable short')}
                                                className={`px-4 py-2 rounded ${
                                                    systemStatus?.memory_enabled.short_term 
                                                        ? 'bg-green-600 hover:bg-green-700' 
                                                        : 'bg-gray-600 hover:bg-gray-500'
                                                }`}
                                            >
                                                {systemStatus?.memory_enabled.short_term ? 'ON' : 'OFF'}
                                            </button>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <div className="font-medium">Medium-term Memory</div>
                                                <div className="text-sm text-gray-400">Session summary and context</div>
                                            </div>
                                            <button
                                                onClick={() => executeCommand(systemStatus?.memory_enabled.medium_term ? 'memory disable medium' : 'memory enable medium')}
                                                className={`px-4 py-2 rounded ${
                                                    systemStatus?.memory_enabled.medium_term 
                                                        ? 'bg-green-600 hover:bg-green-700' 
                                                        : 'bg-gray-600 hover:bg-gray-500'
                                                }`}
                                            >
                                                {systemStatus?.memory_enabled.medium_term ? 'ON' : 'OFF'}
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {/* Domain Management */}
                                <div className="bg-gray-800 rounded-lg p-6">
                                    <h3 className="text-lg font-semibold mb-4">Knowledge Domains</h3>
                                    <div className="space-y-3">
                                        {systemStatus?.available_domains.map(domain => (
                                            <div key={domain} className="flex items-center justify-between">
                                                <div>
                                                    <div className="font-medium capitalize">{domain}</div>
                                                    <div className="text-sm text-gray-400">
                                                        {domain === 'lunar' && 'Lunar phases and cosmic timing'}
                                                        {domain === 'ifs' && 'Internal Family Systems therapy'}
                                                        {domain === 'astrology' && 'Astrological guidance'}
                                                        {domain === 'crystals' && 'Crystal healing and energy work'}
                                                        {domain === 'tarot' && 'Tarot wisdom and symbolism'}
                                                        {domain === 'numerology' && 'Numerological insights'}
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => toggleDomain(domain, !systemStatus.active_domains.includes(domain))}
                                                    className={`px-4 py-2 rounded ${
                                                        systemStatus.active_domains.includes(domain)
                                                            ? 'bg-green-600 hover:bg-green-700'
                                                            : 'bg-gray-600 hover:bg-gray-500'
                                                    }`}
                                                >
                                                    {systemStatus.active_domains.includes(domain) ? 'Active' : 'Inactive'}
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* System Commands */}
                                <div className="bg-gray-800 rounded-lg p-6">
                                    <h3 className="text-lg font-semibold mb-4">System Commands</h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        <button
                                            onClick={() => executeCommand('stats')}
                                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
                                        >
                                            Show Stats
                                        </button>
                                        <button
                                            onClick={() => executeCommand('cache clear')}
                                            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded"
                                        >
                                            Clear Cache
                                        </button>
                                        <button
                                            onClick={() => {
                                                fetchSystemStatus();
                                                fetchSessions();
                                            }}
                                            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded"
                                        >
                                            Refresh Data
                                        </button>
                                        <button
                                            onClick={() => executeCommand('session list')}
                                            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded"
                                        >
                                            List Sessions
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'lunar' && (
                        <div className="flex-1 p-6 overflow-y-auto">
                            <div className="max-w-2xl mx-auto">
                                <h2 className="text-2xl font-bold mb-6 flex items-center">
                                    🌙 Lunar Information
                                </h2>
                                
                                {lunarInfo ? (
                                    <div className="space-y-6">
                                        {/* Current Phase Summary */}
                                        <div className="bg-gray-800 rounded-lg p-6">
                                            <h3 className="text-lg font-semibold mb-4">Current Lunar Phase</h3>
                                            <div className="whitespace-pre-line text-gray-300">
                                                {lunarInfo.summary}
                                            </div>
                                        </div>

                                        {/* Detailed Information */}
                                        <div className="bg-gray-800 rounded-lg p-6">
                                            <h3 className="text-lg font-semibold mb-4">Detailed Information</h3>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <div className="text-sm text-gray-400">Current Date</div>
                                                    <div className="font-medium">
                                                        {new Date(lunarInfo.details.date).toLocaleDateString()}
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="text-sm text-gray-400">Phase</div>
                                                    <div className="font-medium">{lunarInfo.details.phase}</div>
                                                </div>
                                                <div>
                                                    <div className="text-sm text-gray-400">Illumination</div>
                                                    <div className="font-medium">{lunarInfo.details.illumination_percentage}%</div>
                                                </div>
                                                <div>
                                                    <div className="text-sm text-gray-400">Days from New Moon</div>
                                                    <div className="font-medium">{lunarInfo.details.days_from_new_moon}</div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Lunar Guidance */}
                                        <div className="bg-gray-800 rounded-lg p-6">
                                            <h3 className="text-lg font-semibold mb-4">Lunar Guidance</h3>
                                            <div className="text-gray-300">
                                                <p className="mb-3">
                                                    The {lunarInfo.details.phase} is a time of powerful energy. 
                                                    {lunarInfo.details.phase === 'Full Moon' && 
                                                        " This is a time of culmination, release, and heightened intuition. Perfect for letting go of what no longer serves you."
                                                    }
                                                    {lunarInfo.details.phase === 'New Moon' && 
                                                        " This is a time of new beginnings, setting intentions, and planting seeds for the future."
                                                    }
                                                    {lunarInfo.details.phase.includes('Waxing') && 
                                                        " This is a time of growth, manifestation, and building energy toward your goals."
                                                    }
                                                    {lunarInfo.details.phase.includes('Waning') && 
                                                        " This is a time of release, reflection, and letting go of what doesn't serve your highest good."
                                                    }
                                                </p>
                                                <p className="text-sm text-gray-400">
                                                    Ask me about lunar timing for your questions and I can provide guidance 
                                                    based on the current celestial energies.
                                                </p>
                                            </div>
                                        </div>

                                        {/* Refresh Button */}
                                        <div className="text-center">
                                            <button
                                                onClick={fetchLunarInfo}
                                                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
                                            >
                                                Refresh Lunar Data
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="bg-gray-800 rounded-lg p-6 text-center">
                                        <div className="text-gray-400">Loading lunar information...</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// Render the app
ReactDOM.render(<App />, document.getElementById('root')); 