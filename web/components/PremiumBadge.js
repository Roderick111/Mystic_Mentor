/**
 * PremiumBadge.js - Premium Status Badge Component
 * Purpose: Shows premium status badge next to user profile information
 */
const PremiumBadge = ({ size = "sm", className = "" }) => {
    const { premiumStatus, isLoading, isPremium, planType } = window.usePremiumStatus();

    // Don't show anything while loading or for non-premium users
    if (isLoading || !isPremium) {
        return null;
    }

    // Get badge configuration based on plan type
    const getBadgeConfig = () => {
        const configs = {
            'monthly': {
                text: 'Premium',
                emoji: '⭐',
                gradient: 'from-purple-500 to-blue-500',
                textColor: 'text-white'
            },
            'lifetime': {
                text: 'Lifetime',
                emoji: '💎',
                gradient: 'from-amber-400 to-orange-500',
                textColor: 'text-white'
            },
            'admin': {
                text: 'Admin',
                emoji: '👑',
                gradient: 'from-red-500 to-pink-500',
                textColor: 'text-white'
            }
        };

        return configs[planType] || configs['monthly'];
    };

    const config = getBadgeConfig();

    // Size configurations
    const sizeClasses = {
        xs: {
            badge: "px-1.5 py-0.5 text-xs",
            emoji: "text-xs",
            text: "text-xs"
        },
        sm: {
            badge: "px-2 py-1 text-xs",
            emoji: "text-sm",
            text: "text-xs"
        },
        md: {
            badge: "px-2.5 py-1.5 text-sm",
            emoji: "text-base",
            text: "text-sm"
        },
        lg: {
            badge: "px-3 py-2 text-base",
            emoji: "text-lg",
            text: "text-base"
        }
    };

    const sizeConfig = sizeClasses[size] || sizeClasses.sm;

    return (
        <div 
            className={`inline-flex items-center space-x-1 bg-gradient-to-r ${config.gradient} ${config.textColor} ${sizeConfig.badge} rounded-full font-medium shadow-sm ${className}`}
            title={`${config.text} User - Plan: ${planType}`}
        >
            <span className={sizeConfig.emoji}>{config.emoji}</span>
            <span className={sizeConfig.text}>{config.text}</span>
        </div>
    );
};

/**
 * PremiumStatusIndicator - Inline status indicator for user profile
 */
const PremiumStatusIndicator = ({ user }) => {
    const { premiumStatus, isLoading, isPremium, planType } = window.usePremiumStatus();

    if (isLoading) {
        return (
            <div className="flex items-center space-x-2">
                <div className="w-12 h-4 bg-gray-600 rounded animate-pulse"></div>
            </div>
        );
    }

    if (!isPremium) {
        return (
            <div className="flex items-center space-x-1 text-xs text-gray-400">
                <span>Free Plan</span>
            </div>
        );
    }

    return (
        <div className="flex items-center space-x-2">
            <PremiumBadge size="xs" />
            {planType === 'monthly' && (
                <span className="text-xs text-gray-400">Subscription Active</span>
            )}
            {planType === 'lifetime' && (
                <span className="text-xs text-gray-400">Lifetime Access</span>
            )}
            {planType === 'admin' && (
                <span className="text-xs text-gray-400">Administrator</span>
            )}
        </div>
    );
};

// Export components globally
window.PremiumBadge = PremiumBadge;
window.PremiumStatusIndicator = PremiumStatusIndicator; 