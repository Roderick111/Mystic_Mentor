/**
 * app.js - Main Application Layout & Component Orchestration
 * Purpose: Pure presentation layer that composes UI components and distributes props.
 * Contains NO business logic - delegates all functionality to useAppLogic hook.
 */

const { useState, useEffect, useRef } = React;

// Main Chat Application Component
function App() {
    // Use our custom hook for all business logic
    const {
        // State
        messages,
        inputValue,
        setInputValue,
        isLoading,
        systemStatus,
        sessions,
        currentSessionId,
        sidebarOpen,
        setSidebarOpen,
        showSettingsModal,
        setShowSettingsModal,
        showLunarModal,
        setShowLunarModal,
        showProfileMenu,
        setShowProfileMenu,
        showArchivedModal,
        setShowArchivedModal,
        suggestionsDismissed,
        selectedSuggestion,
        isNewSession,
        showSuggestions,
        
        // Refs
        messagesEndRef,
        inputRef,
        
        // Functions
        handleSuggestionClick,
        dismissSuggestions,
        openSettingsModal,
        openLunarModal,
        openArchivedModal,
        sendMessage,
        toggleDomain,
        createNewSession,
        loadSessionMessages,
        updateSessionTitle,
        archiveSession,
        deleteSession
    } = useAppLogic();

    return (
        <div className="flex h-screen bg-gray-900 text-white">
            {/* Left Sidebar */}
            <Sidebar 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                systemStatus={systemStatus}
                sessions={sessions}
                currentSessionId={currentSessionId}
                onCreateNewSession={createNewSession}
                onLoadSession={loadSessionMessages}
                onToggleDomain={toggleDomain}
                onUpdateSessionTitle={updateSessionTitle}
                onArchiveSession={archiveSession}
                onDeleteSession={deleteSession}
            />

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col">
                {/* Top Bar */}
                <TopBar 
                    sidebarOpen={sidebarOpen}
                    setSidebarOpen={setSidebarOpen}
                    currentSessionId={currentSessionId}
                    sessions={sessions}
                    showProfileMenu={showProfileMenu}
                    setShowProfileMenu={setShowProfileMenu}
                    onOpenSettingsModal={openSettingsModal}
                    onOpenLunarModal={openLunarModal}
                    onOpenArchivedModal={openArchivedModal}
                    systemStatus={systemStatus}
                    onToggleDomain={toggleDomain}
                />

                {/* Chat Area */}
                <ChatArea 
                    messages={messages}
                    isLoading={isLoading}
                    inputValue={inputValue}
                    setInputValue={setInputValue}
                    onSendMessage={sendMessage}
                    messagesEndRef={messagesEndRef}
                    inputRef={inputRef}
                    systemStatus={systemStatus}
                    isNewSession={isNewSession}
                    suggestionsDismissed={suggestionsDismissed}
                    selectedSuggestion={selectedSuggestion}
                    onSuggestionClick={handleSuggestionClick}
                    onDismissSuggestions={dismissSuggestions}
                />
            </div>

                        {/* Modals */}
            <Modals
                showSettingsModal={showSettingsModal}
                setShowSettingsModal={setShowSettingsModal}
                showLunarModal={showLunarModal}
                setShowLunarModal={setShowLunarModal}
                showProfileMenu={showProfileMenu}
                setShowProfileMenu={setShowProfileMenu}
                systemStatus={systemStatus}
                onToggleDomain={toggleDomain}
            />

            {/* Archived Sessions Modal */}
            <ArchivedSessions
                showArchivedModal={showArchivedModal}
                setShowArchivedModal={setShowArchivedModal}
                onLoadSession={loadSessionMessages}
                onDeleteSession={deleteSession}
            />
        </div>
    );
}

// Render the app
ReactDOM.render(<App />, document.getElementById('root')); 