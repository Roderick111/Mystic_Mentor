/**
 * Modals.js - Modal Management System
 * Purpose: Handles Settings and Lunar modals with backdrop click-to-close functionality.
 * Centralizes all overlay UI components and their interaction logic.
 */
const Modals = ({
    showSettingsModal,
    setShowSettingsModal,
    showLunarModal,
    setShowLunarModal,
    showProfileMenu,
    setShowProfileMenu,
    systemStatus,
    onToggleDomain
}) => {
    const [lunarData, setLunarData] = React.useState(null);
    const [loadingLunar, setLoadingLunar] = React.useState(false);

    // Fetch detailed lunar data when modal opens
    React.useEffect(() => {
        if (showLunarModal && !lunarData) {
            setLoadingLunar(true);
            apiService.fetchLunarInfo()
                .then(data => {
                    setLunarData(data.details);
                    setLoadingLunar(false);
                })
                .catch(error => {
                    console.error('Failed to fetch lunar data:', error);
                    setLoadingLunar(false);
                });
        }
    }, [showLunarModal]);

    // Reset lunar data when modal closes
    React.useEffect(() => {
        if (!showLunarModal) {
            setLunarData(null);
        }
    }, [showLunarModal]);

    // Get moon phase icon based on phase name
    const getMoonPhaseIcon = (phase) => {
        if (!phase) return '🌙';
        const lowerPhase = phase.toLowerCase();
        if (lowerPhase.includes('new')) return '🌑';
        if (lowerPhase.includes('waxing crescent')) return '🌒';
        if (lowerPhase.includes('first quarter')) return '🌓';
        if (lowerPhase.includes('waxing gibbous')) return '🌔';
        if (lowerPhase.includes('full')) return '🌕';
        if (lowerPhase.includes('waning gibbous')) return '🌖';
        if (lowerPhase.includes('third quarter') || lowerPhase.includes('last quarter')) return '🌗';
        if (lowerPhase.includes('waning crescent')) return '🌘';
        return '🌙';
    };

    // Format date for display
    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    };

    // Get dynamic phase description
    const getPhaseInfo = (phaseName) => {
        if (typeof window.getPhaseDescription === 'function') {
            return window.getPhaseDescription(phaseName);
        }
        return {
            title: "Lunar Energy",
            description: "The current moon phase brings powerful energy for reflection and spiritual connection. This is an ideal time to tune into lunar wisdom and cosmic rhythms.",
            energy: "Cosmic connection, spiritual guidance"
        };
    };

    return (
        <>
            {/* Settings Modal */}
            {showSettingsModal && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    onClick={() => setShowSettingsModal(false)}
                >
                    <div 
                        className="bg-gray-800 rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto"
                        onClick={(e) => e.stopPropagation()}
                    >
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
                                                onClick={() => onToggleDomain(domain, !systemStatus.active_domains.includes(domain))}
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
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    onClick={() => setShowLunarModal(false)}
                >
                    <div 
                        className="bg-gradient-to-br from-slate-800 via-slate-700 to-slate-800 rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto shadow-2xl border border-slate-600"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="relative p-6 border-b border-slate-600/50">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                        </svg>
                                    </div>
                                    <h2 className="text-xl font-semibold text-white">Lunar Information</h2>
                                </div>
                            <button
                                onClick={() => setShowLunarModal(false)}
                                    className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                            >
                                    <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                            </div>
                        </div>
                        
                        {/* Content */}
                        <div className="p-6">
                            {loadingLunar ? (
                                <div className="text-center py-12">
                                    <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-medium text-white mb-2">Connecting to Luna</h3>
                                    <p className="text-gray-400">Gathering celestial wisdom...</p>
                                </div>
                            ) : lunarData ? (
                                <div className="space-y-6">
                                    {/* Central Moon Phase Display */}
                                    <div className="text-center">
                                        <div className="text-6xl mb-3">
                                            {getMoonPhaseIcon(lunarData.phase)}
                                        </div>
                                        <h3 className="text-2xl font-semibold text-white mb-2">
                                            {lunarData.phase}
                                        </h3>
                                        <p className="text-gray-300 text-sm">
                                            {formatDate(lunarData.date)}
                                        </p>
                                    </div>

                                    {/* Lunar Details Grid */}
                                    <div className="grid grid-cols-1 gap-4">
                                        {/* Illumination */}
                                        <div className="bg-slate-700/50 rounded-xl p-4 border border-slate-600/30">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                                                    <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                                                    </svg>
                                                </div>
                                                <div className="flex-1">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-300 text-sm">Illumination</span>
                                                        <span className="text-white font-semibold">{lunarData.illumination_percentage}%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Days from New Moon */}
                                        <div className="bg-slate-700/50 rounded-xl p-4 border border-slate-600/30">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                                                    <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                    </svg>
                                                </div>
                                                <div className="flex-1">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-300 text-sm">Days from New Moon</span>
                                                        <span className="text-white font-semibold">{lunarData.days_from_new_moon}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Days to Full Moon */}
                                        {lunarData.days_to_full_moon > 0 && (
                                            <div className="bg-slate-700/50 rounded-xl p-4 border border-slate-600/30">
                                                <div className="flex items-center space-x-3">
                                                    <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                                                        <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7" />
                                                        </svg>
                                                    </div>
                                                    <div className="flex-1">
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-gray-300 text-sm">Days to Full Moon</span>
                                                            <span className="text-white font-semibold">{lunarData.days_to_full_moon}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Dynamic Spiritual Insight */}
                                    {(() => {
                                        const phaseInfo = getPhaseInfo(lunarData.phase);
                                        return (
                                            <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-xl p-4 border border-purple-500/30">
                                                <div className="flex items-start space-x-3">
                                                    <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                                                        <svg className="w-5 h-5 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                                        </svg>
                                                    </div>
                                                    <div className="flex-1">
                                                        <h4 className="text-purple-200 font-medium mb-2">{phaseInfo.title}</h4>
                                                        <p className="text-gray-300 text-sm leading-relaxed">
                                                            {phaseInfo.description}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })()}
                                </div>
                            ) : (
                                <div className="text-center py-12">
                                    <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
                                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-medium text-white mb-2">Unable to Connect</h3>
                                    <p className="text-gray-400">Lunar information is currently unavailable.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Click outside to close profile menu */}
            {showProfileMenu && (
                <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => {
                        setShowProfileMenu(false);
                    }}
                ></div>
            )}
        </>
    );
};

// Export for use in other components
window.Modals = Modals; 