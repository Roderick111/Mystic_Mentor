/**
 * Sidebar.js - Session & Domain Management Panel
 * Purpose: Handles session CRUD operations, domain toggles, and navigation.
 * Provides collapsible sidebar with search, pagination, and live editing features.
 */
const Sidebar = ({
    sidebarOpen,
    setSidebarOpen,
    systemStatus,
    sessions,
    currentSessionId,
    onCreateNewSession,
    onLoadSession,
    onToggleDomain,
    onUpdateSessionTitle,
    onArchiveSession,
    onDeleteSession
}) => {
    // Session management state
    const [showAllSessions, setShowAllSessions] = React.useState(false);
    const [sessionSearch, setSessionSearch] = React.useState('');
    const [hoveredSessionId, setHoveredSessionId] = React.useState(null);
    const [showSessionMenu, setShowSessionMenu] = React.useState(null);
    const [editingSessionId, setEditingSessionId] = React.useState(null);
    const [editingTitle, setEditingTitle] = React.useState('');
    
    // Reset showAllSessions when there are 5 or fewer sessions
    React.useEffect(() => {
        if (sessions.length <= 5) {
            setShowAllSessions(false);
        }
    }, [sessions.length]);

    // Handle session rename
    const handleRenameSession = (sessionId, currentTitle) => {
        setEditingSessionId(sessionId);
        setEditingTitle(currentTitle);
        setShowSessionMenu(null);
    };

    // Save session rename
    const saveSessionRename = async () => {
        if (editingSessionId && editingTitle.trim()) {
            await onUpdateSessionTitle(editingSessionId, editingTitle.trim());
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
    const hasMoreSessions = !sessionSearch && allFilteredSessions.length > 5;

    // Session component for reuse
    const SessionComponent = ({ session }) => (
        <div key={session.session_id}>
            <div
                className="relative group"
                onMouseEnter={() => setHoveredSessionId(session.session_id)}
                onMouseLeave={() => {
                    // Only clear hover if no menu is open for this session
                    if (showSessionMenu !== session.session_id) {
                        setHoveredSessionId(null);
                    }
                }}
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
                        onClick={() => onLoadSession(session.session_id)}
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
                            {(hoveredSessionId === session.session_id || showSessionMenu === session.session_id) && (
                                <div className="relative session-dropdown">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setShowSessionMenu(showSessionMenu === session.session_id ? null : session.session_id);
                                        }}
                                        onMouseEnter={() => setHoveredSessionId(session.session_id)}
                                        className={`p-1 hover:bg-gray-600 rounded transition-opacity ${
                                            showSessionMenu === session.session_id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                                        }`}
                                    >
                                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                                        </svg>
                                    </button>
                                    
                                    {/* Dropdown Menu */}
                                    {showSessionMenu === session.session_id && (
                                        <div className="absolute right-0 top-6 w-32 bg-gray-700 rounded-lg shadow-lg border border-gray-600 z-50 session-dropdown">
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
                                                        onArchiveSession(session.session_id);
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
                                                        onDeleteSession(session.session_id);
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
        </div>
    );

    return (
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
                        <rect x="3" y="3" width="6" height="18" rx="2" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}/>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8M13 12h8M13 17h8" />
                    </svg>
                </button>
            </div>

            {/* New Chat Button */}
            <div className="p-4">
                <button
                    onClick={onCreateNewSession}
                    className="w-full bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>New Session</span>
                </button>
            </div>

            {/* Recent Sessions */}
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
                    {/* No sessions message */}
                    {allFilteredSessions.length === 0 && (
                        <div className="text-center text-gray-400 text-sm py-4">
                            {sessions.length === 0 ? 'No sessions found' : 'Loading sessions...'}
                        </div>
                    )}
                    
                    {/* When searching, show all results */}
                    {sessionSearch ? (
                        <>
                            {allFilteredSessions.map((session) => (
                                <SessionComponent key={session.session_id} session={session} />
                            ))}
                            {allFilteredSessions.length === 0 && (
                                <div className="text-center text-gray-400 text-sm py-4">
                                    No sessions found matching "{sessionSearch}"
                                </div>
                            )}
                        </>
                    ) : (
                        <>
                            {/* First 5 sessions */}
                            {allFilteredSessions.slice(0, 5).map((session) => (
                                <SessionComponent key={session.session_id} session={session} />
                            ))}
                            
                            {/* Show more button after exactly 5 sessions */}
                            {hasMoreSessions && allFilteredSessions.length >= 5 && (
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
                            
                            {/* Remaining sessions when showAllSessions is true */}
                            {showAllSessions && allFilteredSessions.slice(5).map((session) => (
                                <SessionComponent key={session.session_id} session={session} />
                            ))}
                        </>
                    )}
                </div>

                {/* Click outside to close session menu */}
                {showSessionMenu && (
                    <div 
                        className="fixed inset-0 z-40" 
                        onClick={() => {
                            setShowSessionMenu(null);
                            setHoveredSessionId(null);
                        }}
                    ></div>
                )}
            </div>
        </div>
    );
};

// Export for use in other components
window.Sidebar = Sidebar; 