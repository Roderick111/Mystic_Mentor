/**
 * TopBar.js - Application Header
 * Purpose: Displays current session info, sidebar toggle, and user profile menu.
 * Handles navigation controls and modal triggers for settings/lunar information.
 */
const TopBar = ({
    sidebarOpen,
    setSidebarOpen,
    currentSessionId,
    sessions,
    showProfileMenu,
    setShowProfileMenu,
    onOpenSettingsModal,
    onOpenLunarModal,
    onOpenArchivedModal,
    systemStatus,
    onToggleDomain
}) => {
    // TODO: Re-enable archive feature when multi-user authentication is implemented
    const ARCHIVE_FEATURE_ENABLED = false;
    // State for domain dropdown
    const [showDomainDropdown, setShowDomainDropdown] = React.useState(false);
    // Get current session title for display
    const getCurrentSessionTitle = () => {
        if (!currentSessionId) return 'New Session';
        
        const currentSession = sessions.find(s => s.session_id === currentSessionId);
        return currentSession?.title || `Session ${currentSessionId.slice(0, 8)}`;
    };

    return (
        <div className="bg-transparent h-16 px-4 grid grid-cols-3 items-center">
            {/* Left Section */}
            <div className="flex items-center space-x-4">
                {/* Sidebar Toggle */}
                {!sidebarOpen && (
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="p-2 hover:bg-gray-700 rounded"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <rect x="3" y="3" width="6" height="18" rx="2" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}/>
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8M13 12h8M13 17h8" />
                        </svg>
                    </button>
                )}

                {/* Knowledge Domains Dropdown */}
                <div className="relative">
                    <button
                        onClick={() => setShowDomainDropdown(!showDomainDropdown)}
                        className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                    >
                        <span>Knowledge Domains</span>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                    </button>

                    {/* Domain Dropdown Menu */}
                    {showDomainDropdown && systemStatus && (
                        <div className="absolute left-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-lg border border-gray-700 z-50">
                            <div className="p-3">
                                <div className="text-xs text-gray-400 mb-3 font-medium">Select active knowledge domains:</div>
                                <div className="space-y-2">
                                    {systemStatus.available_domains.map(domain => {
                                        const isActive = systemStatus.active_domains.includes(domain);
                                        const domainNames = {
                                            "lunar": "Lunar Wisdom",
                                            "numerology": "Numerology", 
                                            "crystals": "Crystal Healing",
                                            "astrology": "Astrology",
                                            "tarot": "Tarot & Divination",
                                            "archetypes": "Jungian Archetypes"
                                        };
                                        const displayName = domainNames[domain] || domain.charAt(0).toUpperCase() + domain.slice(1);
                                        
                                        return (
                                            <button
                                                key={domain}
                                                onClick={() => {
                                                    onToggleDomain(domain, !isActive);
                                                }}
                                                className={`w-full flex items-center justify-between p-2 rounded text-sm transition-colors ${
                                                    isActive 
                                                        ? 'bg-green-600 hover:bg-green-700 text-white' 
                                                        : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                                                }`}
                                            >
                                                <span>{displayName}</span>
                                                <div className="flex items-center">
                                                    {isActive && (
                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                        </svg>
                                                    )}
                                                </div>
                                            </button>
                                        );
                                    })}
                                </div>
                                <div className="mt-3 pt-2 border-t border-gray-700">
                                    <div className="text-xs text-gray-500">
                                        Currently active: {systemStatus.active_domains.length} of {systemStatus.available_domains.length}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Center Section - Empty */}
            <div className="text-center">
            </div>

            {/* Right Section - Theme Switcher + Profile Menu */}
            <div className="flex justify-end items-center space-x-3">
                {/* Theme Switcher */}
                <ThemeSwitcher />
                
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
                                        onOpenSettingsModal();
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
                            {ARCHIVE_FEATURE_ENABLED && (
                                <button
                                    onClick={() => {
                                        onOpenArchivedModal();
                                        setShowProfileMenu(false);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 flex items-center space-x-2"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8l4 4 4-4m6 5l-3 3-3-3" />
                                    </svg>
                                    <span>Archived Sessions</span>
                                </button>
                            )}
                            <button
                                onClick={() => {
                                    onOpenLunarModal();
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

            {/* Click outside to close domain dropdown */}
            {showDomainDropdown && (
                <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => setShowDomainDropdown(false)}
                ></div>
            )}
        </div>
    );
};

// Export for use in other components
window.TopBar = TopBar; 