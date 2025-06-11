const { useState, useEffect, useRef } = React;

// API base URL - update this to match your server
const API_BASE = 'http://localhost:8000';

// Main Chat Application Component
function App() {
    // State management
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [systemStatus, setSystemStatus] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [showSettingsModal, setShowSettingsModal] = useState(false);
    const [showLunarModal, setShowLunarModal] = useState(false);
    const [showProfileMenu, setShowProfileMenu] = useState(false);
    
    // Session-based conversation starter state
    const [suggestionsDismissed, setSuggestionsDismissed] = useState(false);
    const [selectedSuggestion, setSelectedSuggestion] = useState(null);
    const [currentSuggestions, setCurrentSuggestions] = useState([]);
    
    // Session management state
    const [showAllSessions, setShowAllSessions] = useState(false);
    const [sessionSearch, setSessionSearch] = useState('');
    const [hoveredSessionId, setHoveredSessionId] = useState(null);
    const [showSessionMenu, setShowSessionMenu] = useState(null);
    const [editingSessionId, setEditingSessionId] = useState(null);
    const [editingTitle, setEditingTitle] = useState('');

    // Refs
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Check if this is a new session (no messages)
    const isNewSession = messages.length === 0;
    
    // Show suggestions for new sessions unless manually dismissed for this session
    const showSuggestions = isNewSession && !suggestionsDismissed;

    // Handle dismissing suggestions for current session
    const dismissSuggestions = () => {
        setSuggestionsDismissed(true);
    };

    // Domain-specific conversation starters
    const conversationStarters = {
        lunar: [
            "What does today's lunar energy mean for me?",
            "How does the current moon phase affect my emotions?",
            "What lunar rituals can enhance my spiritual practice?",
            "How can I align with the moon's cycles for manifestation?",
            "What does the new moon mean for new beginnings?",
            "How does the full moon impact my relationships?",
            "What lunar guidance do I need for this week?",
            "How can I harness lunar energy for healing?",
            "What does the waning moon teach about letting go?",
            "How do lunar eclipses affect my spiritual journey?"
        ],
        numerology: [
            "What do the numbers in my life reveal?",
            "What is my life path number and its meaning?",
            "How does my birth date influence my destiny?",
            "What numerological patterns should I pay attention to?",
            "What does the number 11:11 mean when I see it?",
            "How can numerology guide my career decisions?",
            "What do repeating numbers in my life signify?",
            "How does my name's numerical value affect me?",
            "What numerological insights can help my relationships?",
            "What does my personal year number reveal about this period?"
        ],
        crystals: [
            "Which crystals should I work with right now?",
            "How can I cleanse and charge my crystal collection?",
            "What crystal energy do I need for protection?",
            "How do I choose the right crystal for meditation?",
            "What crystals can help with emotional healing?",
            "How should I program my crystals for manifestation?",
            "What crystal combinations work best together?",
            "How do I know if a crystal is right for me?",
            "What crystals support chakra balancing?",
            "How can I create a crystal grid for my intentions?"
        ]
    };

    // Fisher-Yates shuffle algorithm for unbiased random selection
    const shuffleArray = (array) => {
        const shuffled = [...array]; // Create a copy to avoid modifying original
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    };

    // Get 4 random suggestions from the active domain
    const getConversationSuggestions = () => {
        if (!systemStatus?.active_domains?.length) {
            // Fallback to lunar if no active domains
            return shuffleArray(conversationStarters.lunar).slice(0, 4);
        }
        
        // Get the first active domain (since we're in single domain mode)
        const activeDomain = systemStatus.active_domains[0];
        const domainQuestions = conversationStarters[activeDomain] || conversationStarters.lunar;
        
        // Return 4 randomly selected questions
        return shuffleArray(domainQuestions).slice(0, 4);
    };

    // Handle suggestion click with visual feedback
    const handleSuggestionClick = (suggestion) => {
        setSelectedSuggestion(suggestion);
        setInputValue(suggestion);
        
        // Clear selection after a brief moment
        setTimeout(() => {
            setSelectedSuggestion(null);
        }, 200);
    };

    // Reset suggestions when starting a new session
    useEffect(() => {
        if (messages.length === 0) {
            setSuggestionsDismissed(false);
        }
    }, [currentSessionId]); // Reset when session changes

    // Regenerate suggestions when domain changes or system status loads
    useEffect(() => {
        if (systemStatus) {
            const newSuggestions = getConversationSuggestions();
            setCurrentSuggestions(newSuggestions);
        }
    }, [systemStatus?.active_domains]); // Regenerate when active domains change

    // Generate initial suggestions when component mounts
    useEffect(() => {
        if (systemStatus && currentSuggestions.length === 0) {
            const initialSuggestions = getConversationSuggestions();
            setCurrentSuggestions(initialSuggestions);
        }
    }, [systemStatus]); // Only when systemStatus first loads

    // Fallback: if suggestions are still empty after domain loads, generate them
    useEffect(() => {
        if (systemStatus?.active_domains?.length > 0 && currentSuggestions.length === 0) {
            const fallbackSuggestions = getConversationSuggestions();
            setCurrentSuggestions(fallbackSuggestions);
        }
    }, [systemStatus?.active_domains, currentSuggestions.length]);

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

            // Fetch sessions
        const fetchSessions = async () => {
            try {
                const response = await fetch(`${API_BASE}/sessions?_t=${Date.now()}`);
                const data = await response.json();
                console.log('Fetched sessions:', data);
                setSessions(data);
            } catch (error) {
                console.error('Error fetching sessions:', error);
            }
        };

    // Initial data load
    useEffect(() => {
        fetchSystemStatus();
        fetchSessions();
    }, []);

    // Auto-load messages when switching to a session that has messages
    useEffect(() => {
        const selectedSession = sessions.find(s => s.session_id === currentSessionId);
        if (selectedSession && selectedSession.message_count > 0 && messages.length === 0) {
            console.log(`Auto-loading messages for session ${currentSessionId} (${selectedSession.message_count} messages)`);
            loadSessionMessages(currentSessionId);
        }
    }, [currentSessionId, sessions, messages.length]);

    // Generate meaningful session title from first message
    const generateSessionTitle = (firstMessage) => {
        if (!firstMessage) return 'New Session';
        
        // Clean and truncate the message
        const cleanMessage = firstMessage.trim().replace(/\n+/g, ' ');
        if (cleanMessage.length <= 40) return cleanMessage;
        
        // Find a good breaking point
        const truncated = cleanMessage.substring(0, 40);
        const lastSpace = truncated.lastIndexOf(' ');
        return lastSpace > 20 ? truncated.substring(0, lastSpace) + '...' : truncated + '...';
    };

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
                
                // If this was the first message, update session title
                if (messages.length === 0) {
                    await updateSessionTitle(data.session_id, generateSessionTitle(message));
                }
                
                // Refresh sessions to update message count
                await fetchSessions();
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
                fetchSystemStatus();
            }
        } catch (error) {
            console.error('Error toggling domain:', error);
        }
    };

    // Create new session
    const createNewSession = async () => {
        try {
            setMessages([]);
            setCurrentSessionId(null);
            setSuggestionsDismissed(false); // Reset suggestions for new session
            await fetchSessions();
        } catch (error) {
            console.error('Error creating new session:', error);
        }
    };

    // Load session messages
    const loadSessionMessages = async (sessionId) => {
        try {
            console.log(`Loading messages for session: ${sessionId}`);
            
            const response = await fetch(`${API_BASE}/sessions/${sessionId}/history?_t=${Date.now()}`, {
                method: 'GET',
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
            
            if (!response.ok) {
                console.error(`Failed to load session history: ${response.status} ${response.statusText}`);
                return;
            }
            
            const data = await response.json();
            console.log(`Loaded ${data.messages?.length || 0} messages for session ${sessionId}`);
            
            if (data.messages && Array.isArray(data.messages)) {
                setMessages(data.messages);
                setCurrentSessionId(sessionId);
            } else {
                console.warn('No messages found in session data:', data);
                setMessages([]);
                setCurrentSessionId(sessionId);
            }
        } catch (error) {
            console.error('Error loading session messages:', error);
            setMessages([]);
        }
    };

    // Update session title
    const updateSessionTitle = async (sessionId, title) => {
        try {
            const response = await fetch(`${API_BASE}/sessions/${sessionId}/title`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title }),
            });
            
            if (response.ok) {
                await fetchSessions();
            }
        } catch (error) {
            console.error('Error updating session title:', error);
        }
    };

    // Archive session
    const archiveSession = async (sessionId) => {
        try {
            const response = await fetch(`${API_BASE}/sessions/${sessionId}/archive`, {
                method: 'POST',
            });
            
            if (response.ok) {
                await fetchSessions();
                if (currentSessionId === sessionId) {
                    setMessages([]);
                    setCurrentSessionId(null);
                }
            }
        } catch (error) {
            console.error('Error archiving session:', error);
        }
    };

    // Delete session
    const deleteSession = async (sessionId) => {
        if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
                method: 'DELETE',
            });
            
            if (response.ok) {
                await fetchSessions();
                if (currentSessionId === sessionId) {
                    setMessages([]);
                    setCurrentSessionId(null);
                }
            }
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    };

    // Handle session rename
    const handleRenameSession = (sessionId, currentTitle) => {
        setEditingSessionId(sessionId);
        setEditingTitle(currentTitle);
        setShowSessionMenu(null);
    };

    // Save session rename
    const saveSessionRename = async () => {
        if (editingTitle.trim()) {
            await updateSessionTitle(editingSessionId, editingTitle.trim());
        }
        setEditingSessionId(null);
        setEditingTitle('');
    };

    // Cancel session rename
    const cancelSessionRename = () => {
        setEditingSessionId(null);
        setEditingTitle('');
    };

    // Filter and limit sessions
    const getFilteredSessions = () => {
        let filtered = sessions.filter(session => {
            if (sessionSearch) {
                const title = session.title || `Session ${session.session_id.slice(0, 8)}`;
                return title.toLowerCase().includes(sessionSearch.toLowerCase());
            }
            return true;
        });

        // Sort by last activity (most recent first)
        filtered.sort((a, b) => new Date(b.last_activity) - new Date(a.last_activity));

        return filtered;
    };

    const allFilteredSessions = getFilteredSessions();
    const visibleSessions = (!showAllSessions && !sessionSearch) ? allFilteredSessions.slice(0, 5) : allFilteredSessions;
    const hasMoreSessions = allFilteredSessions.length > 5 && !sessionSearch;

    return (
        <div className="flex h-screen bg-gray-900 text-white">
            {/* Left Sidebar */}
            <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-gray-800 flex flex-col overflow-hidden border-r border-gray-700`}>
                {/* Sidebar Header */}
                <div className="p-4 border-b border-gray-700 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">EA</span>
                        </div>
                        <span className="font-semibold">Esoteric Agent</span>
                    </div>
                    <button
                        onClick={() => setSidebarOpen(false)}
                        className="p-1 hover:bg-gray-700 rounded"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* New Chat Button */}
                <div className="p-4">
                    <button
                        onClick={createNewSession}
                        className="w-full bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span>New Session</span>
                    </button>
                </div>

                {/* Active Domains - Always show */}
                {systemStatus && (
                    <div className="px-4 pb-4">
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

                {/* Recent Sessions - Always show */}
                <div className="flex-1 overflow-y-auto px-4">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-semibold text-gray-400">Recent Sessions</h3>
                    </div>
                        
                        {/* Search Input */}
                        <div className="mb-3">
                            <input
                                type="text"
                                placeholder="Search sessions..."
                                value={sessionSearch}
                                onChange={(e) => setSessionSearch(e.target.value)}
                                className="w-full bg-gray-700 text-white text-sm px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
                            />
                        </div>

                        {/* Sessions List */}
                        <div className="space-y-1">
                            {/* Debug sessions */}
                            {allFilteredSessions.length === 0 && (
                                <div className="text-center text-gray-400 text-sm py-4">
                                    {sessions.length === 0 ? 'No sessions found' : 'Loading sessions...'}
                                </div>
                            )}
                            {allFilteredSessions.map((session, index) => {
                                // Show first 5 sessions, then the button, then remaining sessions if showAllSessions is true
                                const shouldShow = index < 5 || (showAllSessions && !sessionSearch);
                                
                                if (!shouldShow) return null;
                                
                                return (
                                    <div key={session.session_id}>
                                        <div
                                            className="relative group"
                                            onMouseEnter={() => setHoveredSessionId(session.session_id)}
                                            onMouseLeave={() => setHoveredSessionId(null)}
                                        >
                                            {editingSessionId === session.session_id ? (
                                                <div className="p-2 bg-gray-700 rounded">
                                                    <input
                                                        type="text"
                                                        value={editingTitle}
                                                        onChange={(e) => setEditingTitle(e.target.value)}
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter') saveSessionRename();
                                                            if (e.key === 'Escape') cancelSessionRename();
                                                        }}
                                                        onBlur={saveSessionRename}
                                                        className="w-full bg-gray-600 text-white text-sm px-2 py-1 rounded border-none focus:outline-none"
                                                        autoFocus
                                                    />
                                                </div>
                                            ) : (
                                                <button
                                                    onClick={() => loadSessionMessages(session.session_id)}
                                                    className={`w-full text-left p-2 rounded text-sm hover:bg-gray-700 transition-colors ${
                                                        currentSessionId === session.session_id ? 'bg-gray-700' : ''
                                                    }`}
                                                >
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex-1 min-w-0">
                                                            <div className="truncate">
                                                                {session.title || `Session ${session.session_id.slice(0, 8)}`}
                                                            </div>
                                                            <div className="text-xs text-gray-400">
                                                                {session.message_count} messages
                                                            </div>
                                                        </div>
                                                        
                                                        {/* Three dots menu */}
                                                        {hoveredSessionId === session.session_id && (
                                                            <div className="relative">
                                                                <button
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        setShowSessionMenu(showSessionMenu === session.session_id ? null : session.session_id);
                                                                    }}
                                                                    className="p-1 hover:bg-gray-600 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                                                                >
                                                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                                                                    </svg>
                                                                </button>
                                                                
                                                                {/* Dropdown Menu */}
                                                                {showSessionMenu === session.session_id && (
                                                                    <div className="absolute right-0 top-6 w-32 bg-gray-700 rounded-lg shadow-lg border border-gray-600 z-50">
                                                                        <div className="py-1">
                                                                            <button
                                                                                onClick={(e) => {
                                                                                    e.stopPropagation();
                                                                                    handleRenameSession(session.session_id, session.title || `Session ${session.session_id.slice(0, 8)}`);
                                                                                }}
                                                                                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-600 flex items-center space-x-2"
                                                                            >
                                                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                                                </svg>
                                                                                <span>Rename</span>
                                                                            </button>
                                                                            <button
                                                                                onClick={(e) => {
                                                                                    e.stopPropagation();
                                                                                    archiveSession(session.session_id);
                                                                                    setShowSessionMenu(null);
                                                                                }}
                                                                                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-600 flex items-center space-x-2"
                                                                            >
                                                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8l4 4 4-4m6 5l-3 3-3-3" />
                                                                                </svg>
                                                                                <span>Archive</span>
                                                                            </button>
                                                                            <button
                                                                                onClick={(e) => {
                                                                                    e.stopPropagation();
                                                                                    deleteSession(session.session_id);
                                                                                    setShowSessionMenu(null);
                                                                                }}
                                                                                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-600 text-red-400 flex items-center space-x-2"
                                                                            >
                                                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                                                </svg>
                                                                                <span>Delete</span>
                                                                            </button>
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                </button>
                                            )}
                                        </div>
                                        
                                        {/* Show More / Hide Button - Always after 5th session */}
                                        {index === 4 && hasMoreSessions && (
                                            <button
                                                onClick={() => setShowAllSessions(!showAllSessions)}
                                                className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors mt-1"
                                            >
                                                {showAllSessions 
                                                    ? "Hide previous sessions" 
                                                    : `Show ${allFilteredSessions.length - 5} more sessions...`
                                                }
                                            </button>
                                        )}
                                    </div>
                                );
                            })}
                            
                            {/* No sessions message */}
                            {allFilteredSessions.length === 0 && sessionSearch && (
                                <div className="text-center text-gray-400 text-sm py-4">
                                    No sessions found matching "{sessionSearch}"
                                </div>
                            )}
                        </div>
                    </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col">
                {/* Top Bar */}
                <div className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
                    {/* Sidebar Toggle */}
                    {!sidebarOpen && (
                        <button
                            onClick={() => setSidebarOpen(true)}
                            className="p-2 hover:bg-gray-700 rounded"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                    )}

                    {/* Current Session Info */}
                    <div className="flex-1 text-center">
                        <span className="text-sm text-gray-400">
                            {currentSessionId ? 
                                (sessions.find(s => s.session_id === currentSessionId)?.title || `Session ${currentSessionId.slice(0, 8)}`) 
                                : 'New Session'
                            }
                        </span>
                    </div>

                    {/* Profile Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setShowProfileMenu(!showProfileMenu)}
                            className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity"
                        >
                            <span className="text-white font-bold text-sm">U</span>
                        </button>

                        {/* Profile Dropdown */}
                        {showProfileMenu && (
                            <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-lg border border-gray-700 z-50">
                                <div className="py-1">
                                    <button
                                        onClick={() => {
                                            setShowSettingsModal(true);
                                            setShowProfileMenu(false);
                                        }}
                                        className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 flex items-center space-x-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                        <span>Settings</span>
                                    </button>
                                    <button
                                        onClick={() => {
                                            setShowLunarModal(true);
                                            setShowProfileMenu(false);
                                        }}
                                        className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 flex items-center space-x-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                        </svg>
                                        <span>Lunar Info</span>
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-6">
                    <div className="max-w-4xl mx-auto space-y-6">
                        {messages.length === 0 ? (
                            <div className="text-center text-gray-400 mt-20">
                                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <span className="text-white font-bold text-xl">EA</span>
                                </div>
                                <h2 className="text-2xl font-semibold mb-2">
                                    {isNewSession ? "Welcome, seeker. I am your guide through the mysteries of the cosmos." : "How can I help you today?"}
                                </h2>
                                <p className="text-gray-500">
                                    {isNewSession ? "What wisdom do you seek from the universe?" : "Continue your spiritual journey with your Esoteric Agent"}
                                </p>
                                
                                {/* Suggested prompts for new sessions */}
                                {showSuggestions && (
                                    <div className="mt-6 space-y-3">
                                        <div className="flex items-center justify-between max-w-lg mx-auto mb-3">
                                            <p className="text-sm text-gray-400">
                                                Try asking about {systemStatus?.active_domains?.[0] || 'spiritual guidance'}:
                                            </p>
                                            <button
                                                onClick={dismissSuggestions}
                                                className="text-xs text-gray-500 hover:text-gray-300 transition-colors px-2 py-1 hover:bg-gray-800 rounded"
                                                title="Hide suggestions for this session"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                        <div className="space-y-2">
                                            {currentSuggestions.length === 0 ? (
                                                <div className="text-center text-gray-400 text-sm py-4">
                                                    Loading suggestions...
                                                </div>
                                            ) : (
                                                currentSuggestions.map((prompt, index) => (
                                                <button
                                                    key={index}
                                                    onClick={() => handleSuggestionClick(prompt)}
                                                    disabled={isLoading}
                                                    className={`block w-full max-w-lg mx-auto p-3 rounded-lg text-sm text-left transition-all duration-200 ${
                                                        selectedSuggestion === prompt
                                                            ? 'bg-blue-600 text-white transform scale-[0.98]'
                                                            : 'bg-gray-800 hover:bg-gray-700 hover:scale-[1.01]'
                                                    } ${
                                                        isLoading ? 'opacity-50 cursor-not-allowed' : ''
                                                    }`}
                                                >
                                                    <span className="flex items-center">
                                                        {selectedSuggestion === prompt && (
                                                            <span className="mr-2 animate-spin">⟳</span>
                                                        )}
                                                        "{prompt}"
                                                    </span>
                                                </button>
                                                ))
                                            )}
                                        </div>
                                        <p className="text-xs text-gray-500 text-center mt-2 opacity-75">
                                            Questions change with each domain switch and new session
                                        </p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            messages.map((message, index) => (
                                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`flex space-x-3 max-w-3xl ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                                            message.role === 'user' 
                                                ? 'bg-blue-600' 
                                                : 'bg-gradient-to-r from-purple-500 to-blue-500'
                                        }`}>
                                            <span className="text-white font-bold text-sm">
                                                {message.role === 'user' ? 'U' : 'EA'}
                                            </span>
                                        </div>
                                        <div className={`p-4 rounded-lg ${
                                            message.role === 'user' 
                                                ? 'bg-blue-600 text-white' 
                                                : 'bg-gray-800 text-gray-100'
                                        }`}>
                                            <div className="whitespace-pre-wrap">{message.content}</div>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                        
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="flex space-x-3 max-w-3xl">
                                    <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                                        <span className="text-white font-bold text-sm">EA</span>
                                    </div>
                                    <div className="bg-gray-800 p-4 rounded-lg">
                                        <div className="flex space-x-1">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Input Area */}
                <div className="border-t border-gray-700 p-4">
                    <div className="max-w-4xl mx-auto">
                        <form onSubmit={handleSubmit} className="flex space-x-4">
                            <input
                                ref={inputRef}
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                placeholder={isNewSession && !suggestionsDismissed ? "Ask about lunar wisdom, life guidance, or spiritual insights..." : "Message Esoteric Agent..."}
                                className="flex-1 bg-gray-800 text-white border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                                disabled={isLoading}
                            />
                            <button
                                type="submit"
                                disabled={isLoading || !inputValue.trim()}
                                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            {/* Settings Modal */}
            {showSettingsModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-gray-800 rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto">
                        <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">Settings</h2>
                            <button
                                onClick={() => setShowSettingsModal(false)}
                                className="p-2 hover:bg-gray-700 rounded"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        
                        <div className="p-6">
                            {/* Domain Management */}
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold mb-4">Knowledge Domains</h3>
                                <div className="space-y-3">
                                    {systemStatus?.available_domains.map(domain => (
                                        <div key={domain} className="flex items-center justify-between">
                                            <div>
                                                <div className="font-medium capitalize">{domain}</div>
                                                <div className="text-sm text-gray-400">
                                                    {domain === 'lunar' && 'Lunar phases and cosmic timing'}
                                                    {domain === 'numerology' && 'Numerological insights'}
                                                    {domain === 'crystals' && 'Crystal healing and energy work'}
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
                        </div>
                    </div>
                </div>
            )}

            {/* Lunar Modal */}
            {showLunarModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-gray-800 rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto">
                        <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">Lunar Information</h2>
                            <button
                                onClick={() => setShowLunarModal(false)}
                                className="p-2 hover:bg-gray-700 rounded"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        
                        <div className="p-6">
                            {systemStatus?.lunar_info ? (
                                <div className="whitespace-pre-wrap text-gray-300">
                                    {systemStatus.lunar_info}
                                </div>
                            ) : (
                                <div className="text-center text-gray-400">
                                    <div className="w-16 h-16 bg-gradient-to-r from-purple-400 to-blue-400 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                        </svg>
                                    </div>
                                    <p>Lunar information will appear here when available.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Click outside to close menus */}
            {(showProfileMenu || showSessionMenu) && (
                <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => {
                        setShowProfileMenu(false);
                        setShowSessionMenu(null);
                    }}
                ></div>
            )}
        </div>
    );
}

// Render the app
ReactDOM.render(<App />, document.getElementById('root')); 