/**
 * PremiumModal.js - Premium Plan Comparison Modal
 * Purpose: Shows pricing comparison and premium benefits when user clicks Go Premium
 */
const PremiumModal = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    const premiumFeatures = [
        {
            icon: "💬",
            title: "Unlimited Conversations",
            description: "No daily limits - explore as much as your spirit desires",
            highlight: true
        },
        {
            icon: "🤖",
            title: "Advanced AI Models",
            description: "Latest GPT-4 & Claude for deeper spiritual insights",
            highlight: true
        },
        {
            icon: "🔮",
            title: "Exclusive Domains",
            description: "Access all mystical domains + premium-only content",
            highlight: true
        },
        {
            icon: "⚙️",
            title: "Custom AI Personality",
            description: "Tailor your spiritual guide to your unique path",
            highlight: false
        },
        {
            icon: "⚡",
            title: "Priority Responses",
            description: "Skip the queue with instant spiritual guidance",
            highlight: false
        },
        {
            icon: "📚",
            title: "Unlimited History",
            description: "Never lose your spiritual journey with advanced search",
            highlight: false
        }
    ];

    const limitations = [
        "Limited to 20 conversations per day",
        "Standard AI models only",
        "Access to 3 basic domains"
    ];

    const handleUpgrade = (planType = 'monthly') => {
        // TODO: Integrate with actual payment system
        console.log(`Starting ${planType} premium upgrade process...`);
        // This would typically redirect to Stripe, PayPal, etc.
        if (planType === 'lifetime') {
            alert('Lifetime Premium upgrade coming soon! Thank you for being an early believer.');
        } else {
            alert('Monthly Premium upgrade coming soon! Thank you for your interest.');
        }
        onClose();
    };

    return (
        <div 
            className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[9999] p-3"
            onClick={onClose}
        >
            <div 
                className="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200 dark:border-gray-700"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="relative p-6 text-center">
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-xl transition-colors"
                    >
                        ×
                    </button>
                    <div className="mb-4">
                        <div className="text-3xl mb-2">🔮</div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                            Unlock Your Full Mystic Potential
                        </h2>
                        <p className="text-sm text-gray-600 dark:text-gray-300 max-w-sm mx-auto">
                            Transform your spiritual journey with unlimited access to advanced mystical guidance
                        </p>
                    </div>
                </div>

                {/* Primary Monthly Offer */}
                <div className="px-6 pb-4">
                    <div className="bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl p-6 text-white text-center relative overflow-hidden">
                        <div className="relative">
                            <div className="text-4xl font-bold mb-4">
                                $9<span className="text-2xl">.99</span>
                                <span className="text-sm opacity-90 ml-2">per month</span>
                            </div>
                            <button
                                onClick={() => handleUpgrade('monthly')}
                                className="bg-white text-purple-600 font-bold py-3 px-6 rounded-lg hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg text-sm mb-3 w-full"
                            >
                                Start Your Premium Journey
                            </button>
                            <p className="text-xs opacity-80">
                                Cancel anytime • 30-day money-back guarantee
                            </p>
                        </div>
                    </div>
                </div>

                {/* Secondary Lifetime Option */}
                <div className="px-6 pb-4">
                    <div className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4 text-center border border-amber-200 dark:border-amber-800">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-gray-700 dark:text-gray-300">
                                <span className="font-semibold">Save 85%</span> with lifetime access
                            </div>
                            <div className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 text-xs px-2 py-1 rounded-full font-medium">
                                Limited Time
                            </div>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="text-left">
                                <div className="text-lg font-bold text-gray-900 dark:text-white">
                                    $150 <span className="text-sm font-normal text-gray-600 dark:text-gray-400">one-time</span>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">vs $119+ annually</div>
                            </div>
                            <button
                                onClick={() => handleUpgrade('lifetime')}
                                className="bg-amber-500 text-white font-semibold py-2 px-4 rounded-lg hover:bg-amber-600 transition-all duration-200 text-sm"
                            >
                                Get Lifetime
                            </button>
                        </div>
                    </div>
                </div>

                {/* Current Limitations */}
                <div className="px-6 pb-4">
                    <div className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 text-center">
                            You're currently limited by:
                        </h3>
                        <div className="space-y-2">
                            {limitations.map((limitation, index) => (
                                <div key={index} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                    <div className="w-1.5 h-1.5 bg-red-400 rounded-full flex-shrink-0"></div>
                                    <span>{limitation}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Premium Features */}
                <div className="px-6 pb-6">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-center">
                        Unlock Everything With Premium
                    </h3>
                    <div className="space-y-3">
                        {premiumFeatures.map((feature, index) => (
                            <div key={index} className={`flex items-start gap-3 p-3 rounded-lg transition-all duration-200 hover:bg-gray-50 dark:hover:bg-gray-700/30 ${feature.highlight ? 'bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700' : ''}`}>
                                <div className="text-lg flex-shrink-0 mt-0.5">{feature.icon}</div>
                                <div className="flex-1">
                                    <h4 className="font-semibold text-gray-900 dark:text-white mb-1 text-sm">
                                        {feature.title}
                                    </h4>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                                        {feature.description}
                                    </p>
                                </div>
                                {feature.highlight && (
                                    <div className="text-purple-500 flex-shrink-0">
                                        <svg className="w-4 h-4 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

// Export for global use
window.PremiumModal = PremiumModal; 