import ConversationStarters from './ConversationStarters.js';

function ChatArea({ 
    messages, 
    isLoading, 
    inputValue, 
    setInputValue, 
    onSubmit, 
    messagesEndRef,
    systemStatus,
    showSuggestions,
    onDismissSuggestions,
    onSuggestionClick,
    selectedSuggestion,
    currentSuggestions,
    isNewSession
}) {
    return (
        <>
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
                            
                            <ConversationStarters
                                systemStatus={systemStatus}
                                showSuggestions={showSuggestions}
                                onDismiss={onDismissSuggestions}
                                onSuggestionClick={onSuggestionClick}
                                selectedSuggestion={selectedSuggestion}
                                isLoading={isLoading}
                                currentSuggestions={currentSuggestions}
                            />
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
                    <form onSubmit={onSubmit} className="flex space-x-4">
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder={isNewSession && showSuggestions ? "Ask about lunar wisdom, life guidance, or spiritual insights..." : "Message Esoteric Agent..."}
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
        </>
    );
}

export default ChatArea; 