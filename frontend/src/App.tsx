import React, { useState, useEffect } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { PersonaSelector } from './components/PersonaSelector';
import { SummaryPanel } from './components/SummaryPanel';
import DebatePanel from './components/DebatePanel';
import { config } from './config';
import { logger } from './utils/logger';
// Import product and persona configurations
import { productContext as configuredProductContext } from './config/product.config';
import { personasData as configuredPersonasData } from './config/personas.config';

// Product context data - now imported from config
// This structure is kept for backward compatibility with the backend API
const productContext = {
  product_id: configuredProductContext.name.replace(/\s+/g, '_').toUpperCase(),
  product_name: configuredProductContext.name,
  description: configuredProductContext.description,
  purpose: [
    `Provide ${configuredProductContext.target_users[0]} with ${configuredProductContext.key_features[0]}`,
    configuredProductContext.value_proposition
  ],
  current_capabilities: configuredProductContext.key_features,
  target_users: configuredProductContext.target_users,
  industry: configuredProductContext.industry,
  technical_context: configuredProductContext.technical_context
};

// Personas data - now imported from config and transformed
// This transformation maps the config structure to the App's expected format
const personasData = configuredPersonasData.map(persona => ({
  ...persona,
  isActive: false
}));

function App() {
  const [personas, setPersonas] = useState(personasData);
  const [selectedPersonas, setSelectedPersonas] = useState<string[]>([]);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [mode, setMode] = useState<'chat' | 'debate'>('chat');
  const [isLoading, setIsLoading] = useState(false);
  
  // Load chat state from localStorage on mount
  useEffect(() => {
    const savedChatState = localStorage.getItem('personasay_chat_state');
    if (savedChatState) {
      try {
        const parsed = JSON.parse(savedChatState);
        
        // Restore chat history with date conversion
        const restoredHistory = (parsed.chatHistory || []).map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp) // Convert ISO string back to Date
        }));
        
        setChatHistory(restoredHistory);
        setSummary(parsed.summary || null);
        logger.debug('Restored chat state from localStorage', {
          messageCount: restoredHistory.length,
          hasSummary: !!parsed.summary
        });
      } catch (error) {
        logger.error('Failed to restore chat state:', error);
        localStorage.removeItem('personasay_chat_state');
      }
    }
  }, []);
  
  // Save chat state to localStorage whenever it changes
  useEffect(() => {
    if (chatHistory.length > 0 || summary) {
      const chatState = {
        chatHistory: chatHistory.map(msg => ({
          ...msg,
          timestamp: msg.timestamp.toISOString() // Convert Date to ISO string for storage
        })),
        summary,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem('personasay_chat_state', JSON.stringify(chatState));
      logger.debug('Saved chat state to localStorage', {
        messageCount: chatHistory.length,
        hasSummary: !!summary
      });
    }
  }, [chatHistory, summary]);
  
  // Set default selected personas (first 4)
  useEffect(() => {
    setSelectedPersonas(['alex', 'ben', 'nina', 'rachel']);
  }, []);

  // Debug: Log when selected personas change
  useEffect(() => {
    logger.debug('App.tsx - selectedPersonas changed:', selectedPersonas);
  }, [selectedPersonas]);
  
  // Get selected persona objects for DebatePanel
  const selectedPersonaObjects = personas.filter(p => selectedPersonas.includes(p.id));

  return (
    <div className="min-h-screen text-white p-6" style={{background: '#000000'}}>
      <div className="flex h-full max-w-7xl mx-auto gap-6">
        {/* Left Panel - Expert Personas */}
        <div className="w-1/3 rounded-2xl p-6 flex flex-col stable-layout backdrop-blur-sm" style={{backgroundColor: 'rgba(30, 30, 45, 0.7)', border: '1px solid rgba(255, 255, 255, 0.1)'}}>
          <div className="mb-8 flex-shrink-0">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-2 h-2 rounded-full" style={{background: 'linear-gradient(45deg, #22d3ee, #2dd4bf)'}}></div>
              <h1 className="text-lg font-semibold text-white tracking-tight">
                Active Personas
              </h1>
            </div>
            <p className="text-sm text-gray-300 ml-5 tabular-nums">
              {selectedPersonas.length} of {personas.length} selected
            </p>
          </div>
        
          <div className="flex-1 overflow-hidden">
            <PersonaSelector 
              personas={personas} 
              selected={selectedPersonas} 
              setSelected={setSelectedPersonas}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Right Panel - PersonaSay Chat/Debate */}
        <div className="w-2/3 rounded-2xl p-6 backdrop-blur-sm" style={{backgroundColor: 'rgba(30, 30, 45, 0.7)', border: '1px solid rgba(255, 255, 255, 0.1)'}}>
          <div className="flex justify-between items-start mb-6">
            <div>
              <div className="mb-4">
                <h2 className="text-3xl text-white font-normal tracking-tight" style={{fontFamily: 'Aboreto, serif'}}>
                  PersonaSay
                </h2>
              </div>
            </div>
            
            {/* Mode Toggle */}
            <div className="flex rounded-lg p-1" style={{backgroundColor: 'rgba(30, 30, 45, 0.9)', border: '1px solid rgba(255, 255, 255, 0.1)'}}>
              <button
                onClick={() => setMode('chat')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  mode === 'chat' 
                    ? 'text-white' 
                    : 'text-gray-400 hover:text-gray-200'
                }`}
                style={{
                  backgroundColor: mode === 'chat' ? 'rgba(6, 182, 212, 0.3)' : 'transparent',
                  border: mode === 'chat' ? '1px solid rgba(34, 211, 238, 0.3)' : '1px solid transparent'
                }}
              >
                💬 Chat
              </button>
              <button
                onClick={() => setMode('debate')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  mode === 'debate' 
                    ? 'text-white' 
                    : 'text-gray-400 hover:text-gray-200'
                }`}
                style={{
                  backgroundColor: mode === 'debate' ? 'rgba(6, 182, 212, 0.3)' : 'transparent',
                  border: mode === 'debate' ? '1px solid rgba(34, 211, 238, 0.3)' : '1px solid transparent'
                }}
              >
                👥 Debate
              </button>
            </div>
          </div>
        
          {mode === 'chat' ? (
            <>
              <ChatWindow 
                allPersonas={personas}
                selectedPersonaIds={selectedPersonas}
                context={productContext}
                chatHistory={chatHistory}
                setChatHistory={setChatHistory}
                summary={summary}
                setSummary={setSummary}
                onLoadingChange={setIsLoading}
              />
              
              <SummaryPanel
                context={productContext}
                chatHistory={chatHistory}
                setSummary={setSummary}
                summary={summary}
                allPersonas={personas}
                selectedPersonaIds={selectedPersonas}
              />
            </>
          ) : (
            <DebatePanel
              selectedPersonas={selectedPersonaObjects}
              onLoadingChange={setIsLoading}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;