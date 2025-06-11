/**
 * ConversationStarters.js - Dynamic Conversation Prompts
 * Purpose: Generates domain-specific question suggestions using Fisher-Yates shuffle.
 * Provides 4 randomized conversation starters based on currently active knowledge domains.
 */
const ConversationStarters = ({ 
    systemStatus, 
    isLoading, 
    onSuggestionClick, 
    onDismiss,
    selectedSuggestion 
}) => {
    const [currentSuggestions, setCurrentSuggestions] = React.useState([]);

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
        ],
        personal: [
            "I'm feeling lost and need guidance on my life direction",
            "Help me understand why I keep attracting the same relationship patterns",
            "I'm going through a difficult transition and need spiritual support",
            "I feel stuck emotionally and don't know how to heal",
            "What is my soul trying to teach me through recent challenges?",
            "I'm struggling with self-doubt - how can I find my inner strength?",
            "Help me release old wounds that are holding me back",
            "I need clarity about a major life decision I'm facing",
            "How can I better trust my intuition in daily life?",
            "I'm feeling disconnected from my purpose - guide me back"
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

    // Get 4 suggestions: 1 from active domain + 2 from personal + 1 from active domain
    const getConversationSuggestions = () => {
        if (!systemStatus?.active_domains?.length) {
            // Fallback to lunar + personal if no active domains
            const lunarQuestions = shuffleArray(conversationStarters.lunar).slice(0, 2);
            const personalQuestions = shuffleArray(conversationStarters.personal).slice(0, 2);
            return [...lunarQuestions, ...personalQuestions];
        }
        
        // Get the first active domain (since we're in single domain mode)
        const activeDomain = systemStatus.active_domains[0];
        const domainQuestions = conversationStarters[activeDomain] || conversationStarters.lunar;
        const personalQuestions = conversationStarters.personal;
        
        // Get 1 random domain question and 2 random personal questions
        const selectedDomainQuestions = shuffleArray(domainQuestions).slice(0, 2);
        const selectedPersonalQuestions = shuffleArray(personalQuestions).slice(0, 2);
        
        // Combine and return 4 total questions
        return [...selectedDomainQuestions, ...selectedPersonalQuestions];
    };

    // Regenerate suggestions when domain changes
    React.useEffect(() => {
        if (systemStatus) {
            const newSuggestions = getConversationSuggestions();
            setCurrentSuggestions(newSuggestions);
        }
    }, [systemStatus?.active_domains]);

    // Generate initial suggestions when component mounts
    React.useEffect(() => {
        if (systemStatus && currentSuggestions.length === 0) {
            const initialSuggestions = getConversationSuggestions();
            setCurrentSuggestions(initialSuggestions);
        }
    }, [systemStatus]);

    // Fallback: if suggestions are still empty after domain loads, generate them
    React.useEffect(() => {
        if (systemStatus?.active_domains?.length > 0 && currentSuggestions.length === 0) {
            const fallbackSuggestions = getConversationSuggestions();
            setCurrentSuggestions(fallbackSuggestions);
        }
    }, [systemStatus?.active_domains, currentSuggestions.length]);

    return (
        <div className="mt-10 space-y-3">
            <div className="flex items-center justify-between max-w-lg mx-auto mb-3">
                <p className="text-sm text-gray-400">
                    Try asking about {systemStatus?.active_domains?.[0] || 'spiritual guidance'}:
                </p>
                <button
                    onClick={onDismiss}
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
                            onClick={() => onSuggestionClick(prompt)}
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
        </div>
    );
};

// Export for use in other components
window.ConversationStarters = ConversationStarters; 