import React, { useState, useRef, useEffect } from 'react';
import { marked } from 'marked';
import { config } from '../config';
import { logger } from '../utils/logger';
import { Persona } from '../config/personas.config';

interface DebateMessage {
  persona_id?: string;
  persona_name?: string;
  persona_title?: string;
  response: string;
  round: number;
  timestamp: string;
  error?: boolean;
  type?: 'user' | 'persona';
}

interface DebatePanelProps {
  selectedPersonas: Persona[];
  onDebateStatusChange?: (isActive: boolean) => void;
  onLoadingChange?: (isLoading: boolean) => void;
}

const DebatePanel: React.FC<DebatePanelProps> = ({ selectedPersonas, onDebateStatusChange, onLoadingChange }) => {
  const [topic, setTopic] = useState('');
  const [debateId, setDebateId] = useState('');
  const [currentRound, setCurrentRound] = useState(0);
  const [maxRounds, setMaxRounds] = useState(3);
  const [conversation, setConversation] = useState<DebateMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDebateActive, setIsDebateActive] = useState(false);
  const [error, setError] = useState('');
  const [waitingForUser, setWaitingForUser] = useState(false);
  const [debateSummary, setDebateSummary] = useState<string>('');
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [attachError, setAttachError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Close export menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showExportMenu && !target.closest('.export-menu-container')) {
        setShowExportMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showExportMenu]);

  // Load debate state from localStorage on mount
  useEffect(() => {
    const savedDebateState = localStorage.getItem('personasay_debate_state');
    if (savedDebateState) {
      try {
        const parsed = JSON.parse(savedDebateState);
        
        // Migrate old conversation format to new format
        const migratedConversation = (parsed.conversation || []).map((msg: any, idx: number) => {
          // Ensure each message has a timestamp
          const timestamp = msg.timestamp || (Date.now() - (parsed.conversation.length - idx) * 1000);
          
          // If the message already has persona_name, it's already in the new format
          if (msg.persona_name) {
            return { ...msg, timestamp };
          }
          
          // Otherwise, migrate from old format (name -> persona_name, role -> persona_title)
          return {
            ...msg,
            persona_name: msg.name || msg.persona_name || 'Unknown',
            persona_title: msg.role || msg.persona_title || '',
            timestamp,
          };
        });
        
        setTopic(parsed.topic || '');
        setDebateId(parsed.debateId || '');
        setCurrentRound(parsed.currentRound || 0);
        setMaxRounds(parsed.maxRounds || 3);
        setConversation(migratedConversation);
        setIsDebateActive(parsed.isDebateActive || false);
        setWaitingForUser(parsed.waitingForUser || false);
        setDebateSummary(parsed.debateSummary || '');
        logger.debug('Restored and migrated debate state from localStorage');
        
        // Notify parent if debate was active
        if (parsed.isDebateActive && onDebateStatusChange) {
          onDebateStatusChange(true);
        }
      } catch (error) {
        logger.error('Failed to restore debate state:', error);
      }
    }
  }, []);

  // Save debate state to localStorage whenever it changes
  useEffect(() => {
    if (isDebateActive || conversation.length > 0) {
      const debateState = {
        topic,
        debateId,
        currentRound,
        maxRounds,
        conversation,
        isDebateActive,
        waitingForUser,
        debateSummary
      };
      localStorage.setItem('personasay_debate_state', JSON.stringify(debateState));
      logger.debug('Saved debate state to localStorage');
    }
  }, [topic, debateId, currentRound, maxRounds, conversation, isDebateActive, waitingForUser, debateSummary]);

  const startDebate = async () => {
    if (selectedPersonas.length < 2) {
      setError('Please select at least 2 personas to start a debate.');
      return;
    }
    if (!topic.trim()) {
      setError('Please enter a topic for the debate.');
      return;
    }

    const newDebateId = `debate_${Date.now()}`;
    setDebateId(newDebateId);
    setConversation([]);
    setCurrentRound(0);
    setIsDebateActive(true);
    setError('');
    
    // Notify parent that debate started
    if (onDebateStatusChange) {
      onDebateStatusChange(true);
    }
    
    // Start Round 1
    await executeRound(newDebateId, 1, []);
  };

  const executeRound = async (sessionId: string, roundNum: number, history: DebateMessage[], userMsg?: string, targetPersonas?: any[]) => {
    setIsLoading(true);
    if (onLoadingChange) onLoadingChange(true);
    setError('');
    setWaitingForUser(false);

    // Use provided targetPersonas or default to selectedPersonas
    const personasToUse = targetPersonas || selectedPersonas;

    try {
      logger.debug(`Executing Round ${roundNum}...`, {
        debateId: sessionId,
        userMessage: userMsg || 'none',
        historyLength: history.length,
        targetPersonas: personasToUse.map(p => p.name),
        attachedFiles: attachedFiles.length
      });

      let response: Response;
      
      // Use attachments endpoint if files are attached
      if (attachedFiles.length > 0) {
        logger.debug(`Using /debate/round-with-attachments endpoint with ${attachedFiles.length} files`);
        const form = new FormData();
        form.append('debate_id', sessionId);
        form.append('topic', topic);
        form.append('personas', JSON.stringify(personasToUse));
        form.append('round_number', String(roundNum));
        form.append('conversation_history', JSON.stringify(history));
        if (userMsg) {
          form.append('user_message', userMsg);
        }
        attachedFiles.forEach((f) => form.append('files', f));
        
        response = await fetch(`${config.api.baseUrl}/debate/round-with-attachments`, {
          method: 'POST',
          body: form
        });
      } else {
        response = await fetch(`${config.api.baseUrl}/debate/round`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            debate_id: sessionId,
            topic: topic,
            personas: personasToUse,
            round_number: roundNum,
            conversation_history: history,
            user_message: userMsg || null,
          }),
        });
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Round failed');
      }

      const data = await response.json();
      logger.debug(`Round ${roundNum} complete`, data);

      // Add responses to conversation and map field names
      const newMessages = data.responses.map((resp: any, idx: number) => {
        const mapped = {
          persona_id: resp.persona_id,
          persona_name: resp.name,  // Map 'name' to 'persona_name'
          persona_title: resp.role,  // Map 'role' to 'persona_title'
          response: resp.response,
          round: roundNum,
          timestamp: Date.now() + idx,  // Add idx to ensure unique timestamps
          type: 'persona' as const,
          error: resp.error || false,
        };
        logger.debug(`Mapped response for ${resp.name}:`, mapped);
        return mapped;
      });
      
      const updatedHistory = [...history, ...newMessages];
      setConversation(updatedHistory);
      setCurrentRound(roundNum);

      // Always wait for user input after a round completes
      // This allows continuous interaction even after max rounds
      setWaitingForUser(true);
      setUserInput('');
      
      // Log if we've reached max rounds, but don't end the debate
      if (roundNum >= maxRounds) {
        logger.info('Reached max rounds, but debate continues (user can still participate)');
      }

    } catch (err: any) {
      logger.error(`Round ${roundNum} error:`, err);
      setError(err.message || `Failed to execute round ${roundNum}`);
      setIsDebateActive(false);
      // Notify parent that debate ended due to error
      if (onDebateStatusChange) {
        onDebateStatusChange(false);
      }
    } finally {
      setIsLoading(false);
      if (onLoadingChange) onLoadingChange(false);
    }
  };

  const generateDebateSummary = async () => {
    if (!conversation.length) return;
    
    setIsGeneratingSummary(true);
    setError('');
    
    try {
      logger.info('Generating debate summary...');
      
      // Convert conversation to history format for the /summary endpoint
      const history = conversation
        .filter(msg => !msg.error)
        .map(msg => {
          if (msg.type === 'user') {
            return {
              role: 'user',
              content: msg.response,
            };
          } else {
            return {
              role: 'assistant',
              content: msg.response,
              name: msg.persona_name,
            };
          }
        });
      
      // Format ALL selected personas for the summary
      const personasData = selectedPersonas.map(p => ({
        id: p.id,
        name: p.name,
        title: p.title,
        company: p.company || 'Company',
      }));
      
      // Use the improved /summary endpoint with round detection and better AI instructions
      const response = await fetch(`${config.api.baseUrl}/summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          history: history,
          context: {
            debate_topic: topic,
            max_rounds: maxRounds,
            current_round: currentRound,
          },
          personas: personasData,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Summary generation failed');
      }
      
      const data = await response.json();
      const summary = data.summary || 'Summary unavailable';
      
      setDebateSummary(summary);
      logger.info('Summary generated');
      
    } catch (err: any) {
      logger.error('Summary generation error:', err);
      setError(err.message || 'Failed to generate summary');
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  const continueDebate = async (withUserInput: boolean) => {
    if (!isDebateActive || isLoading) return;

    // Detect @mentions and filter target personas
    let targetPersonas = selectedPersonas;
    let mentionedPersonas: any[] = [];
    
    if (withUserInput && userInput.trim()) {
      const mentionPattern = /@(\w+)/g;
      const mentions = [...userInput.matchAll(mentionPattern)];
      
      if (mentions.length > 0) {
        // Find mentioned personas
        for (const match of mentions) {
          const mentionedName = match[1].toLowerCase();
          const persona = selectedPersonas.find(p => 
            p.name.toLowerCase() === mentionedName || 
            p.name.toLowerCase().startsWith(mentionedName) ||
            p.id.toLowerCase() === mentionedName
          );
          
          if (persona && !mentionedPersonas.find(p => p.id === persona.id)) {
            mentionedPersonas.push(persona);
          } else if (!persona) {
            setError(`WARNING: Persona @${match[1]} is not in this debate. Only these personas can be tagged: ${selectedPersonas.map(p => p.name).join(', ')}`);
            return;
          }
        }
        
        // If mentions found, only those personas should respond
        if (mentionedPersonas.length > 0) {
          targetPersonas = mentionedPersonas;
          logger.debug('Only mentioned personas will respond:', targetPersonas.map(p => p.name));
        }
      }
    }

    const nextRound = currentRound + 1;
    let userMessage = undefined;

    if (withUserInput && userInput.trim()) {
      // Add user message to conversation
      const userMsg: DebateMessage = {
        response: userInput.trim(),
        round: currentRound,
        timestamp: new Date().toISOString(),
        type: 'user',
        persona_name: 'You',
      };
      const updatedHistory = [...conversation, userMsg];
      setConversation(updatedHistory);
      userMessage = userInput.trim();
      setUserInput('');
    }

    await executeRound(debateId, nextRound, withUserInput && userMessage ? [...conversation, {
      response: userMessage!,
      round: currentRound,
      timestamp: new Date().toISOString(),
      type: 'user',
      persona_name: 'You',
    }] : conversation, userMessage, targetPersonas);
    
    // Clear attachments after round
    setAttachedFiles([]);
  };

  const getPersonaAvatar = (personaId?: string) => {
    if (!personaId) return '/avatars/default.png';
    const persona = selectedPersonas.find(p => p.id === personaId);
    return persona ? persona.avatar : '/avatars/default.png';
  };

  const getPersonaColor = (personaId?: string) => {
    const colors = ['#22d3ee', '#14b8a6', '#06b6d4', '#f59e0b', '#8b5cf6', '#ec4899', '#3b82f6'];
    if (!personaId) return '#10b981'; // User color
    const index = selectedPersonas.findIndex(p => p.id === personaId);
    return colors[index % colors.length];
  };

  const exportDebate = (format: 'txt' | 'json' | 'md') => {
    // Only export summary, not the full conversation
    if (!debateSummary) {
      setError('No summary available to export. Please generate a summary first.');
      return;
    }

    let content = '';
    let filename = '';
    let mimeType = '';

    const timestamp = new Date().toISOString().split('T')[0];
    const cleanSummary = debateSummary.replace(/<[^>]*>/g, ''); // Strip HTML

    if (format === 'txt') {
      // Plain text format - Summary only
      content = `DEBATE SUMMARY\n`;
      content += `${'='.repeat(60)}\n\n`;
      content += `Topic: ${topic}\n`;
      content += `Date: ${new Date().toLocaleDateString()}\n`;
      content += `Participants: ${selectedPersonas.map(p => p.name).join(', ')}\n`;
      content += `Total Rounds: ${currentRound}\n`;
      content += `\n${'='.repeat(60)}\n\n`;
      content += cleanSummary;

      filename = `debate-summary_${timestamp}.txt`;
      mimeType = 'text/plain';

    } else if (format === 'json') {
      // JSON format - Summary with metadata only
      const exportData = {
        metadata: {
          topic,
          date: new Date().toISOString(),
          participants: selectedPersonas.map(p => ({ id: p.id, name: p.name, title: p.title })),
          totalRounds: currentRound,
          debateId,
        },
        summary: cleanSummary,
      };

      content = JSON.stringify(exportData, null, 2);
      filename = `debate-summary_${timestamp}.json`;
      mimeType = 'application/json';

    } else if (format === 'md') {
      // Markdown format - Summary only
      content = `# Debate Summary\n\n`;
      content += `**Topic:** ${topic}\n\n`;
      content += `**Date:** ${new Date().toLocaleDateString()}\n\n`;
      content += `**Participants:** ${selectedPersonas.map(p => p.name).join(', ')}\n\n`;
      content += `**Total Rounds:** ${currentRound}\n\n`;
      content += `---\n\n`;
      content += cleanSummary;

      filename = `debate-summary_${timestamp}.md`;
      mimeType = 'text/markdown';
    }

    // Create and trigger download
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    logger.info(`Exported debate summary as ${filename}`);
  };

  const renderMessage = (message: DebateMessage, uniqueKey: string) => {
    const isUser = message.type === 'user';
    
    return (
      <div 
        key={uniqueKey}
        className={`flex items-start space-x-4 mb-6 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}
      >
        {!isUser && (
          <img
            src={getPersonaAvatar(message.persona_id)}
            alt={message.persona_name || 'Avatar'}
            className="w-10 h-10 rounded-full flex-shrink-0 border-2"
            style={{ borderColor: getPersonaColor(message.persona_id) }}
          />
        )}
        {isUser && (
          <div className="w-10 h-10 rounded-full flex-shrink-0 bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center text-white font-semibold border-2 border-green-400">
            U
          </div>
        )}
        <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
          <div className={`flex items-baseline space-x-2 mb-2 ${isUser ? 'justify-end' : ''}`}>
            <span className="font-semibold text-base" style={{ color: getPersonaColor(message.persona_id) }}>
              {message.persona_name || 'Unknown'}
            </span>
            {message.persona_title && (
              <span className="text-sm text-gray-400">({message.persona_title})</span>
            )}
            <span className="text-xs text-gray-500 px-2 py-0.5 rounded-full bg-slate-700/50">Round {message.round}</span>
          </div>
          <div
            className={`prose prose-invert max-w-none text-gray-200 leading-relaxed debate-text ${isUser ? 'text-right' : ''}`}
            style={{ 
              fontSize: '15px', 
              lineHeight: '1.75',
              letterSpacing: '0.01em'
            }}
            dangerouslySetInnerHTML={{ __html: marked(message.response) }}
          />
          {message.error && (
            <p className="text-red-500 text-xs mt-2 flex items-center">
              <span className="mr-1">⚠️</span> Error occurred
            </p>
          )}
        </div>
      </div>
    );
  };

  const resetDebate = () => {
    setTopic('');
    setDebateId('');
    setCurrentRound(0);
    setMaxRounds(3);
    setConversation([]);
    setIsDebateActive(false);
    setWaitingForUser(false);
    setDebateSummary('');
    setError('');
    localStorage.removeItem('personasay_debate_state');
    logger.info('Debate reset');
    
    if (onDebateStatusChange) {
      onDebateStatusChange(false);
    }
  };

  return (
    <div className="flex flex-col h-[650px] max-w-full">
      {!isDebateActive ? (
        <div className="mb-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <h3 className="text-lg font-semibold text-white mb-3">Start an Interactive Debate</h3>
          <div className="mb-4">
            <label htmlFor="topic" className="block text-sm font-medium text-gray-300 mb-1">
              Debate Topic
            </label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Should we integrate a new odds provider?"
              className="w-full p-2 rounded-md bg-slate-700/50 border border-slate-600/50 text-white placeholder-gray-500 focus:ring-cyan-500 focus:border-cyan-500"
              disabled={isLoading}
            />
          </div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <label htmlFor="rounds" className="block text-sm font-medium text-gray-300 mb-1">
                Max Rounds
              </label>
              <select
                id="rounds"
                value={maxRounds}
                onChange={(e) => setMaxRounds(Number(e.target.value))}
                className="p-2 rounded-md bg-slate-700/50 border border-slate-600/50 text-white focus:ring-cyan-500 focus:border-cyan-500"
                disabled={isLoading}
              >
                {[2, 3, 4, 5].map((r) => (
                  <option key={r} value={r}>
                    {r} Rounds
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-300">Participants:</span>
              {selectedPersonas.length > 0 ? (
                selectedPersonas.map((p) => (
                  <img
                    key={p.id}
                    src={p.avatar}
                    alt={p.name}
                    title={p.name}
                    className="w-8 h-8 rounded-full border-2"
                    style={{ borderColor: getPersonaColor(p.id) }}
                  />
                ))
              ) : (
                <span className="text-sm text-gray-500">Select personas on the left</span>
              )}
            </div>
          </div>
          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
          <button
            onClick={startDebate}
            className="w-full py-2 px-4 rounded-md text-white font-semibold transition-colors duration-200 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700"
            disabled={isLoading}
          >
            Start Interactive Debate
          </button>
          <p className="text-xs text-gray-400 mt-2">You'll be able to join the conversation between rounds!</p>
        </div>
      ) : (
        <div className="flex flex-col h-full overflow-y-auto pb-4">
          <div className="flex-shrink pr-4 pb-2">
            <div className="mb-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-cyan-400">📋 Topic: {topic}</h3>
                  <p className="text-xs text-gray-400 mt-1">Round {currentRound} of {maxRounds}</p>
                </div>
                <button
                  onClick={resetDebate}
                  className="px-3 py-2 text-sm rounded-xl transition-all duration-200 border backdrop-blur-sm"
                  style={{
                    backgroundColor: 'rgba(220, 38, 38, 0.2)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    color: '#fca5a5'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.3)';
                    e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.5)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.2)';
                    e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)';
                  }}
                  title="Clear debate and start over"
                >
                  <span>🗑️</span>
                </button>
              </div>
            </div>

            {Array.from(new Set(conversation.map(msg => msg.round))).sort().map(roundNum => (
              <div key={roundNum} className="mb-8">
                <div className="flex items-center mb-6">
                  <span className="px-4 py-2 bg-gradient-to-r from-cyan-600/30 to-teal-600/30 text-cyan-300 text-base font-semibold rounded-lg border border-cyan-500/30">
                    Round {roundNum}
                  </span>
                  <div className="flex-grow border-t border-slate-600/50 ml-4"></div>
                </div>
                <div className="space-y-6">
                  {conversation
                    .filter(msg => msg.round === roundNum)
                    .map((msg, idx) => {
                      // Generate a unique key combining round, persona_id, timestamp, and index
                      const uniqueKey = `${msg.round}-${msg.persona_id || 'user'}-${msg.timestamp || Date.now()}-${idx}`;
                      return renderMessage(msg, uniqueKey);
                    })}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center justify-center py-4">
                <svg className="animate-spin h-8 w-8 text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="ml-3 text-cyan-400">Personas are thinking...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {waitingForUser && !isLoading && (
            <div className="flex-shrink-0 flex flex-col p-4 bg-slate-800/50 rounded-lg border border-cyan-600/50 mt-2 mr-4 min-h-0">
              {currentRound >= maxRounds && (
                <div className="mb-3 p-2 bg-green-900/20 border border-green-600/30 rounded-lg">
                  <p className="text-xs text-green-400 flex items-center">
                    <span className="mr-2">[DONE]</span>
                    Completed {maxRounds} rounds - Continue conversation or end debate
                  </p>
                </div>
              )}
              <p className="text-sm text-cyan-400 mb-2">Your turn! Want to add to the discussion?</p>
              <p className="text-xs text-gray-400 mb-3">
                Tip: Only personas in this debate ({selectedPersonas.map(p => p.name.split(' ')[0]).join(', ')}) can be tagged with @
              </p>
              {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
              <textarea
                value={userInput}
                onChange={(e) => {
                  setUserInput(e.target.value);
                  if (error) setError(''); // Clear error when user types
                }}
                placeholder="Type your thoughts (optional)... Add @persona name to tag specific persona (e.g., @alex)"
                className="w-full p-4 rounded-xl border text-white placeholder-gray-500 resize-none mb-3 transition-all backdrop-blur-sm"
                style={{
                  backgroundColor: 'rgba(3, 94, 117, 0.18)',
                  borderColor: 'rgba(34, 211, 238, 0.18)',
                  minHeight: '80px'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(34, 211, 238, 0.35)';
                  e.currentTarget.style.backgroundColor = 'rgba(3, 94, 117, 0.25)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(34, 211, 238, 0.18)';
                  e.currentTarget.style.backgroundColor = 'rgba(3, 94, 117, 0.18)';
                }}
                rows={3}
              />
              
              {/* File attachment display and input */}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".png,.jpg,.jpeg,.webp,.pdf,.doc,.docx,.ppt,.pptx,.txt"
                style={{ display: 'none' }}
                onChange={(e) => {
                  const files = Array.from(e.target.files || []);
                  const allowed = ['png','jpg','jpeg','webp','pdf','doc','docx','ppt','pptx','txt'];
                  const valid: File[] = [];
                  const invalid: string[] = [];
                  files.forEach((f) => {
                    const ext = f.name.split('.').pop()?.toLowerCase() || '';
                    if (allowed.includes(ext)) {
                      valid.push(f);
                    } else {
                      invalid.push(f.name);
                    }
                  });
                  if (invalid.length > 0) {
                    setAttachError(`Unsupported file type: ${invalid.join(', ')}. Allowed: ${allowed.join(', ')}`);
                    window.setTimeout(() => setAttachError(null), 5000);
                  }
                  if (valid.length > 0) {
                    logger.debug(`Files attached to debate: ${valid.length}`);
                    valid.forEach(f => logger.debug(`   - ${f.name} (${f.type}, ${f.size} bytes)`));
                    setAttachedFiles(valid);
                  }
                }}
              />
              {attachedFiles.length > 0 && (
                <div className="mb-3 p-2 bg-cyan-900/20 border border-cyan-600/30 rounded-md">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-cyan-300">
                      📎 {attachedFiles.length} attachment{attachedFiles.length > 1 ? 's' : ''}: {attachedFiles.map(f => f.name).join(', ')}
                    </span>
                    <button
                      onClick={() => setAttachedFiles([])}
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              )}
              {attachError && (
                <div className="mb-3 text-xs px-2 py-1 rounded border" style={{ color: '#fca5a5', borderColor: 'rgba(239, 68, 68, 0.35)', backgroundColor: 'rgba(127, 29, 29, 0.25)' }}>
                  {attachError}
                </div>
              )}
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="text-white p-2.5 rounded-lg transition-colors border"
                  style={{ backgroundColor: 'rgba(6, 78, 94, 0.6)', borderColor: 'rgba(34, 211, 238, 0.18)' }}
                  title="Attach files"
                  aria-label="Attach files"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M21 12.5l-8.5 8.5a6 6 0 01-8.49-8.49L12.5 4a4 4 0 115.66 5.66L9.75 18.06a2 2 0 11-2.83-2.83L15 7.16"/>
                  </svg>
                </button>
                <button
                  onClick={() => continueDebate(true)}
                  disabled={!userInput.trim() && attachedFiles.length === 0}
                  className="text-white p-2.5 rounded-lg transition-colors border disabled:cursor-not-allowed"
                  style={{
                    background: (!userInput.trim() && attachedFiles.length === 0) 
                      ? 'rgba(1, 35, 43, 0.5)'
                      : 'linear-gradient(45deg, #22d3ee, #2dd4bf)',
                    borderColor: (!userInput.trim() && attachedFiles.length === 0) 
                      ? 'rgba(34, 211, 238, 0.1)'
                      : 'rgba(34, 211, 238, 0.25)',
                    boxShadow: (!userInput.trim() && attachedFiles.length === 0) 
                      ? 'none' 
                      : '0 0 12px rgba(34, 211, 238, 0.25)'
                  }}
                  title="Send and continue debate"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </button>
                <button
                  onClick={() => continueDebate(false)}
                  className="flex-1 min-w-[140px] py-2 px-4 rounded-md text-white font-semibold transition-colors duration-200 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700"
                >
                  Skip to Next Round
                </button>
                <button
                  onClick={generateDebateSummary}
                  disabled={isGeneratingSummary || conversation.length === 0}
                  className={`py-2 px-4 rounded-md text-white font-semibold transition-colors duration-200 ${
                    isGeneratingSummary
                      ? 'bg-gray-600 cursor-wait'
                      : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                  }`}
                  title="Generate a summary of the debate so far"
                >
                  {isGeneratingSummary ? 'Loading...' : 'Generate'} Summary
                </button>
                
                {/* Export Button with Dropdown */}
                <div className="relative export-menu-container flex-1 min-w-[140px]">
                  <button
                    onClick={() => setShowExportMenu(!showExportMenu)}
                    disabled={conversation.length === 0}
                    className={`w-full py-2 px-4 rounded-md text-white font-semibold transition-colors duration-200 ${
                      conversation.length === 0
                        ? 'bg-gray-600 cursor-not-allowed'
                        : 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700'
                    }`}
                    title="Export debate transcript"
                  >
                    Export
                  </button>
                  
                  {showExportMenu && conversation.length > 0 && (
                    <div className="absolute bottom-full mb-2 right-0 bg-slate-800 border border-slate-600 rounded-lg shadow-xl py-2 z-50 min-w-[140px]">
                      <button
                        onClick={() => {
                          exportDebate('txt');
                          setShowExportMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-white hover:bg-slate-700 transition-colors text-sm"
                      >
                        📄 Text (.txt)
                      </button>
                      <button
                        onClick={() => {
                          exportDebate('md');
                          setShowExportMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-white hover:bg-slate-700 transition-colors text-sm"
                      >
                        Markdown (.md)
                      </button>
                      <button
                        onClick={() => {
                          exportDebate('json');
                          setShowExportMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-white hover:bg-slate-700 transition-colors text-sm"
                      >
                        JSON (.json)
                      </button>
                    </div>
                  )}
                </div>
                
                <button
                  onClick={() => {
                    setIsDebateActive(false);
                    setConversation([]);
                    setCurrentRound(0);
                    setTopic('');
                    setDebateSummary('');
                    if (onDebateStatusChange) {
                      onDebateStatusChange(false);
                    }
                  }}
                  className="py-2 px-4 rounded-md text-white font-semibold transition-colors duration-200 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700"
                  title="End debate and start fresh"
                >
                  🛑 End Debate
                </button>
              </div>
            </div>
          )}
          
          {/* Debate Summary Display */}
          {debateSummary && (
            <div className="flex-shrink-0 mt-2 p-4 bg-purple-900/20 border border-purple-600/30 rounded-lg mr-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-purple-400 flex items-center">
                  <span className="mr-2">📋</span>
                  Conversation Summary
                </h4>
                <button
                  onClick={() => setDebateSummary('')}
                  className="text-gray-400 hover:text-white transition-colors"
                  title="Close summary"
                >
                  ✕
                </button>
              </div>
              <div
                className="prose prose-invert max-w-none text-gray-200 debate-summary-text"
                style={{ 
                  fontSize: '14px',
                  lineHeight: '1.8'
                }}
                dangerouslySetInnerHTML={{ __html: marked(debateSummary) }}
              />
            </div>
          )}

          {!waitingForUser && !isLoading && currentRound >= maxRounds && (
            <div className="flex-shrink-0 mt-2 p-4 bg-slate-800/50 rounded-lg border border-green-600/50 mr-4">
              <p className="text-sm text-green-400 mb-3">Debate Complete!</p>
              <button
                onClick={() => {
                  setIsDebateActive(false);
                  setConversation([]);
                  setCurrentRound(0);
                  setTopic('');
                  // Notify parent that debate reset
                  if (onDebateStatusChange) {
                    onDebateStatusChange(false);
                  }
                }}
                className="w-full py-2 px-4 rounded-md text-white font-semibold transition-colors duration-200 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700"
              >
                Start New Debate
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DebatePanel;
