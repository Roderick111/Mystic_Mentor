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
    return (
        <>
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