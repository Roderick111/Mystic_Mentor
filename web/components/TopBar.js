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

            {/* Right Section - Theme Switcher + User Profile */}
            <div className="flex justify-end items-center space-x-3">
                {/* Theme Switcher */}
                <ThemeSwitcher />
                
                {/* User Profile Icon with Menu */}
                <TopBarUserProfile 
                    showProfileMenu={showProfileMenu}
                    setShowProfileMenu={setShowProfileMenu}
                    onOpenSettingsModal={onOpenSettingsModal}
                    onOpenLunarModal={onOpenLunarModal}
                    onOpenArchivedModal={onOpenArchivedModal}
                />
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