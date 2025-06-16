/**
 * PremiumStatusDisplay.js - Premium User Status and Management Component
 * Purpose: Shows premium status and subscription management for premium users
 * Replaces the "Go Premium" button for authenticated premium users
 */
const PremiumStatusDisplay = () => {
    const { premiumStatus, isLoading, isPremium, planType } = window.usePremiumStatus();
    const [showDetails, setShowDetails] = React.useState(false);

    // Format activation date
    const formatActivationDate = (dateString) => {
        if (!dateString) return 'Unknown';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return 'Unknown';
        }
    };

    // Get status display info
    const getStatusInfo = () => {
        const statusConfig = {
            'monthly': {
                title: 'Premium Active',
                subtitle: 'Monthly Subscription',
                emoji: '⭐',
                color: 'from-purple-500 to-blue-500',
                actionText: 'Manage Subscription'
            },
            'lifetime': {
                title: 'Lifetime Access',
                subtitle: 'Premium Forever',
                emoji: '💎',
                color: 'from-amber-400 to-orange-500',
                actionText: 'View Benefits'
            },
            'admin': {
                title: 'Administrator',
                subtitle: 'Full Access',
                emoji: '👑',
                color: 'from-red-500 to-pink-500',
                actionText: 'Admin Panel'
            }
        };

        return statusConfig[planType] || statusConfig['monthly'];
    };

    if (isLoading) {
        return (
            <div className="w-full p-3 bg-gray-700 rounded-lg animate-pulse">
                <div className="h-4 bg-gray-600 rounded mb-2"></div>
                <div className="h-3 bg-gray-600 rounded w-2/3"></div>
            </div>
        );
    }

    if (!isPremium) {
        return null; // This component is only for premium users
    }

    const statusInfo = getStatusInfo();

    return (
        <div className="w-full">
            {/* Single Premium Status Container */}
            <div 
                className={`w-full p-4 bg-gradient-to-r ${statusInfo.color} rounded-lg cursor-pointer transition-all duration-200 border border-transparent hover:border-white/40`}
                onClick={() => setShowDetails(!showDetails)}
            >
                <div className="text-white space-y-3">
                    {/* Header with title and expand button - Always visible */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <span className="text-lg">{statusInfo.emoji}</span>
                            <div>
                                <div className="text-sm font-medium">{statusInfo.title}</div>
                                <div className="text-xs opacity-90">{statusInfo.subtitle}</div>
                            </div>
                        </div>
                        <svg 
                            className={`w-4 h-4 transition-transform duration-200 ${showDetails ? 'rotate-180' : ''}`} 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>

                    {/* Expanded Details Section - Only visible when showDetails is true */}
                    {showDetails && (
                        <>
                            {/* Plan Details */}
                            <div className="text-xs space-y-2 pt-3">
                                <div className="flex justify-between items-center">
                                    <span className="opacity-80">Plan:</span>
                                    <span className="font-medium capitalize">{planType}</span>
                                </div>
                                
                                {premiumStatus?.premium_activated_at && (
                                    <div className="flex justify-between items-center">
                                        <span className="opacity-80">Activated:</span>
                                        <span className="font-medium">{formatActivationDate(premiumStatus.premium_activated_at)}</span>
                                    </div>
                                )}

                                <div className="flex justify-between items-center">
                                    <span className="opacity-80">Status:</span>
                                    <div className="flex items-center space-x-1">
                                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                        <span className="font-medium">Active</span>
                                    </div>
                                </div>
                            </div>

                            {/* Benefits Section */}
                            <div className="pt-3">
                                <div className="text-xs opacity-80 mb-2">Premium Benefits:</div>
                                <div className="space-y-1 text-xs">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-white">✓</span>
                                        <span>Unlimited conversations</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className="text-white">✓</span>
                                        <span>Advanced AI models</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className="text-white">✓</span>
                                        <span>All mystical domains</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className="text-white">✓</span>
                                        <span>Priority support</span>
                                    </div>
                                </div>
                            </div>

                            {/* Management Button - only for monthly subscriptions */}
                            {planType === 'monthly' && (
                                <div className="pt-3">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            // TODO: Implement subscription management
                                            console.log('Open subscription management');
                                        }}
                                        className="w-full px-4 py-3 text-sm bg-white hover:bg-gray-100 active:bg-gray-200 rounded transition-all duration-150 text-gray-800 font-medium transform hover:scale-[1.02] active:scale-[0.98]"
                                    >
                                        <div className="flex items-center justify-center space-x-2">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            </svg>
                                            <span>Manage Subscription</span>
                                        </div>
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

// Export component globally
window.PremiumStatusDisplay = PremiumStatusDisplay; 