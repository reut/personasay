import React, { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { marked } from 'marked';
import { config } from '../config';
import { logger } from '../utils/logger';
import { Persona } from '../config/personas.config';

interface Message {
  id: string;
  sender: string;
  senderRole?: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
  avatarColor?: string;
  avatar?: string;
  avatarUrl?: string;
}

interface ChatWindowProps {
  allPersonas: Persona[];
  selectedPersonaIds: string[];
  context: any;
  chatHistory: Message[];
  setChatHistory: React.Dispatch<React.SetStateAction<Message[]>>;
  summary?: any;
  setSummary?: React.Dispatch<React.SetStateAction<any>>;
  onLoadingChange?: (isLoading: boolean) => void;
}

// Simple markdown renderer for basic formatting
const renderMarkdown = (text: string) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-zinc-700 px-1 py-0.5 rounded text-sm">$1</code>')
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold text-lime-400 mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-lime-400 mt-4 mb-2">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-lime-400 mt-4 mb-2">$1</h1>')
    .replace(/^\* (.*$)/gm, '<li class="ml-4">• $1</li>')
    .replace(/^- (.*$)/gm, '<li class="ml-4">• $1</li>')
    .replace(/^\d+\. (.*$)/gm, '<li class="ml-4">$&</li>')
    .replace(/\n\n/g, '</p><p class="mb-2">')
    .replace(/\n/g, '<br>');
};

export const ChatWindow = ({ allPersonas, selectedPersonaIds, context, chatHistory, setChatHistory, summary, setSummary, onLoadingChange }: ChatWindowProps) => {
  // Clear chat function that also clears summary from parent if needed
  const clearChat = () => {
    if (window.confirm('Clear all chat history and summary? This cannot be undone.')) {
      setChatHistory([]);
      if (setSummary) {
        setSummary(null);
      }
      localStorage.removeItem('personasay_chat_state');
      logger.info('Chat history and summary cleared');
    }
  };
  
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [requestMock, setRequestMock] = useState(false);
  const [expandedSvg, setExpandedSvg] = useState<string | null>(null);
  const [attachError, setAttachError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Get count of currently selected personas
  const selectedPersonasCount = allPersonas.filter(p => selectedPersonaIds.includes(p.id)).length;

  // Debug: Log when selectedPersonaIds prop changes
  useEffect(() => {
    logger.debug('ChatWindow - selectedPersonaIds prop changed:', selectedPersonaIds);
    logger.debug('ChatWindow - filtered personas:', allPersonas.filter(p => selectedPersonaIds.includes(p.id)).map(p => p.name));
  }, [selectedPersonaIds, allPersonas]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const sendMessage = async () => {
    logger.group('=== SEND MESSAGE CALLED ===');
    logger.debug('Message:', inputMessage);
    logger.debug('Raw selectedPersonaIds:', selectedPersonaIds);
    logger.debug('All available personas:', allPersonas.map(p => ({ id: p.id, name: p.name })));
    
    // Get currently selected personas (always fresh from current state)
    const currentlySelectedPersonas = allPersonas.filter(p => selectedPersonaIds.includes(p.id)).map(p => ({
      ...p,
      avatarColor: '#10B981',
      avatarUrl: ''
    }));
    
    logger.debug('Filtered currently selected personas:', currentlySelectedPersonas.map(p => ({ id: p.id, name: p.name })));

    // Check for @mentions in the message FIRST (before validation)
    const mentionRegex = /@(\w+)/g;
    const mentions = [...inputMessage.matchAll(mentionRegex)].map(match => match[1].toLowerCase());
    
    logger.debug('Detected mentions:', mentions);
    logger.debug('All personas:', allPersonas.map(p => ({ id: p.id, name: p.name, firstName: p.name.split(' ')[0].toLowerCase() })));
    
    // If mentions exist, use ONLY mentioned personas (regardless of selection)
    // Else, use currently selected personas
    let targetPersonas = currentlySelectedPersonas;
    if (mentions.length > 0) {
      logger.debug('Checking mentions against personas...');
      const mentionedPersonas = allPersonas.filter(persona => {
        const firstName = persona.name.split(' ')[0].toLowerCase();
        const firstNameMatches = mentions.includes(firstName);
        const idMatches = mentions.includes(persona.id.toLowerCase());
        const fullNameMatches = mentions.includes(persona.name.toLowerCase().replace(/\s+/g, ''));
        
        logger.debug(`   ${persona.name}: firstName="${firstName}" (${firstNameMatches}), id="${persona.id}" (${idMatches}), fullName (${fullNameMatches})`);
        
        return firstNameMatches || idMatches || fullNameMatches;
      });
      
      logger.debug('Mentioned personas found:', mentionedPersonas.map(p => ({ id: p.id, name: p.name })));
      
      if (mentionedPersonas.length > 0) {
        targetPersonas = mentionedPersonas.map(p => ({
          ...p,
          avatarColor: '#10B981',
          avatarUrl: ''
        }));
        logger.debug('Using mentioned personas:', targetPersonas.map(p => p.name));
      } else {
        logger.warn('No matching personas found for mentions:', mentions);
        logger.warn('   Available persona names/IDs:', allPersonas.map(p => `${p.name} (@${p.id})`));
        if (currentlySelectedPersonas.length === 0) {
          alert(`No persona found matching: @${mentions.join(', @')}.\n\nAvailable personas: ${allPersonas.map(p => `@${p.id} (${p.name})`).join(', ')}`);
          return;
        }
        targetPersonas = currentlySelectedPersonas;
      }
    }

    // Validate AFTER checking for mentions
    if (!inputMessage.trim() || targetPersonas.length === 0) {
      logger.error('Cannot send - validation failed');
      logger.groupEnd();
      logger.debug('   - Has message:', !!inputMessage.trim());
      logger.debug('   - Has target personas:', targetPersonas.length);
      if (targetPersonas.length === 0 && mentions.length > 0) {
        alert('Please select at least one persona or use a valid @mention');
      }
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'You',
      content: inputMessage,
      timestamp: new Date(),
      isUser: true,
    };

    setChatHistory((prev: Message[]) => [...prev, userMessage]);

    setInputMessage('');
    setIsLoading(true);
    if (onLoadingChange) onLoadingChange(true);

    try {
      logger.group('=== SENDING TO BACKEND ===');
      logger.debug('Prompt:', inputMessage);
      logger.debug('Target personas (will respond):', targetPersonas.map(p => ({ id: p.id, name: p.name })));
      logger.debug('Total:', targetPersonas.length);
      logger.debug('Mock Generation:', requestMock ? 'ON' : 'OFF');
      logger.debug('Attached Files:', attachedFiles.length);
      
      let response: Response;
      logger.debug(`Attached files count: ${attachedFiles.length}`);
      if (attachedFiles.length > 0) {
        logger.debug('Using /chat-attachments endpoint');
        attachedFiles.forEach((f) => logger.debug(`   - ${f.name} (${f.type})`));
        const form = new FormData();
        form.append('prompt', inputMessage);
        form.append('personas', JSON.stringify(targetPersonas));
        form.append('context', JSON.stringify(context));
        form.append('history', JSON.stringify(chatHistory.map(msg => ({
          role: msg.isUser ? 'user' : 'assistant',
          content: msg.content,
          sender: msg.sender
        }))));
        form.append('generate_mock', String(requestMock));
        attachedFiles.forEach((f) => form.append('files', f));
        response = await fetch(`${config.api.baseUrl}/chat-attachments`, { method: 'POST', body: form });
      } else {
        response = await fetch(`${config.api.baseUrl}${config.api.endpoints.chat}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: inputMessage,
            personas: targetPersonas,
            context: context,
            generate_mock: requestMock,
            history: chatHistory.map(msg => ({
              role: msg.isUser ? 'user' : 'assistant',
              content: msg.content,
              sender: msg.sender
            }))
          }),
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      logger.debug('Received backend response:', {
        total_replies: data.replies?.length || 0,
        replies: data.replies?.map((r: any) => ({ 
          name: r.name, 
          persona_id: r.persona_id,
          has_mock: !!r.mock_svg,
          mock_length: r.mock_svg?.length || 0,
          response_length: r.response?.length || 0
        })) || []
      });
      
      // Debug: Log first reply in full to see structure
      if (data.replies && data.replies.length > 0) {
        logger.debug('First reply object keys:', Object.keys(data.replies[0]));
        logger.debug('First reply sample:', {
          ...data.replies[0],
          response: data.replies[0].response?.substring(0, 100) + '...',
          mock_svg: data.replies[0].mock_svg ? data.replies[0].mock_svg.substring(0, 100) + '...' : 'NO MOCK'
        });
      }
      
      // Add persona responses to chat history
      const personaResponses: Message[] = data.replies.flatMap((reply: any) => {
        logger.debug(`Processing reply from ${reply.name || reply.persona}`);
        const matchedPersona = targetPersonas.find(p => p.id === reply.persona_id || p.name === reply.persona);
        const textMsg: Message = {
          id: `${Date.now()}-${reply.persona_id || reply.persona}`,
          sender: reply.name || reply.persona,
          senderRole: matchedPersona?.title || reply.role || '',
          content: reply.response,
          timestamp: new Date(),
          isUser: false,
          avatarColor: matchedPersona?.avatarColor,
          avatar: matchedPersona?.avatar,
          avatarUrl: matchedPersona?.avatarUrl
        };
        const extras: Message[] = [textMsg];
        if (reply.mock_svg && typeof reply.mock_svg === 'string' && reply.mock_svg.includes('<svg')) {
          let svg = reply.mock_svg.trim();
          // Strip possible markdown fences and normalize size for responsive display
          svg = svg.replace(/```[a-zA-Z]*\n?/g, '').replace(/```/g, '').trim();
          // Make SVG responsive by setting width to 100% and removing explicit height
          // The viewBox will preserve aspect ratio
          svg = svg
            .replace(/width="[^"]*"/i, 'width="100%"')
            .replace(/height="[^"]*"/i, '');
          extras.push({
            id: `${Date.now()}-${reply.persona_id || reply.persona}-mock`,
            sender: reply.name || reply.persona,
            senderRole: textMsg.senderRole,
            content: svg,
            timestamp: new Date(),
            isUser: false,
            avatarColor: textMsg.avatarColor,
            avatar: textMsg.avatar,
            avatarUrl: textMsg.avatarUrl
          });
        }
        return extras;
      });

      logger.debug(`Adding ${personaResponses.length} persona responses to chat history`);
      logger.groupEnd();
      setChatHistory((prev: Message[]) => [...prev, ...personaResponses]);
    } catch (error) {
      logger.error('Error sending message:', error);
      logger.groupEnd();
      
      // Fallback to simulated responses if backend fails
      const fallbackResponses: Message[] = targetPersonas.map((persona) => ({
        id: `${Date.now()}-${persona.id}`,
        sender: persona.name,
        content: `As ${persona.name} (${persona.title} at ${persona.company}), I would respond: This is a simulated response from ${persona.name}. In a real implementation, this would be generated by the AI with memory of our conversation.`,
        timestamp: new Date(),
        isUser: false,
        avatarColor: persona.avatarColor,
        avatar: persona.avatar,
        avatarUrl: persona.avatarUrl
      }));
      
      setChatHistory((prev: Message[]) => [...prev, ...fallbackResponses]);
    } finally {
      setIsLoading(false);
      if (onLoadingChange) onLoadingChange(false);
      setAttachedFiles([]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const exportToWord = () => {
    // Only export summary, not the chat history
    if (!summary) {
      alert('Please generate a summary first before exporting');
      return;
    }

    // Helper function to safely convert summary to HTML
    const formatSummaryForExport = (summaryText: string) => {
      if (!summaryText) return '';
      
      // Convert markdown-like formatting to HTML (black and white only)
      return summaryText
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code style="background-color: #f5f5f5; color: #000000; padding: 2px 4px; border-radius: 3px; border: 1px solid #cccccc;">$1</code>')
        .replace(/^### (.*$)/gm, '<h3 style="color: #000000; margin-top: 20px; margin-bottom: 10px; font-weight: bold;">$1</h3>')
        .replace(/^## (.*$)/gm, '<h2 style="color: #000000; margin-top: 25px; margin-bottom: 15px; font-weight: bold;">$1</h2>')
        .replace(/^# (.*$)/gm, '<h1 style="color: #000000; margin-top: 30px; margin-bottom: 20px; font-weight: bold;">$1</h1>')
        .replace(/^\* (.*$)/gm, '<li style="margin-left: 20px;">• $1</li>')
        .replace(/^\d+\. (.*$)/gm, '<li style="margin-left: 20px;">$&</li>')
        .replace(/\n\n/g, '</p><p style="margin-bottom: 10px;">')
        .replace(/\n/g, '<br>');
    };

    // Create HTML content - SUMMARY ONLY, not the chat history
    const htmlContent = `
      <html>
        <head>
          <meta charset="utf-8">
          <title>PersonaSay - Analysis Summary & KPIs</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; color: #000000; background-color: #ffffff; max-width: 800px; }
            h1 { color: #000000; border-bottom: 3px solid #000000; font-weight: bold; padding-bottom: 10px; }
            h2 { color: #000000; margin-top: 30px; margin-bottom: 15px; font-weight: bold; border-left: 4px solid #000000; padding-left: 10px; }
            h3 { color: #333333; margin-top: 20px; margin-bottom: 10px; font-weight: bold; }
            .metadata { background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #cccccc; }
            .summary-section { padding: 20px; line-height: 1.8; }
            .kpi-highlight { background-color: #fffacd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffa500; margin: 20px 0; }
            strong { color: #000000; font-weight: bold; }
            li { margin: 8px 0; line-height: 1.6; }
            p { margin: 10px 0; }
          </style>
        </head>
        <body>
          <h1>PersonaSay - Analysis Summary & KPIs</h1>
          <div class="metadata">
            <p><strong>Export Date:</strong> ${new Date().toLocaleString()}</p>
            <p><strong>Participants:</strong> ${allPersonas.filter(p => selectedPersonaIds.includes(p.id)).map(p => `${p.name} (${p.title})`).join(', ')}</p>
            <p><strong>Total Messages Analyzed:</strong> ${chatHistory.length}</p>
          </div>
          
          <div class="summary-section">
            ${formatSummaryForExport(summary)}
          </div>
          
          <hr style="margin: 30px 0; border: none; border-top: 1px solid #cccccc;">
          <p style="text-align: center; color: #666666; font-size: 12px;">Generated by PersonaSay - Multi-Persona Analysis Platform</p>
        </body>
      </html>
    `;

    // Create blob and download - SUMMARY ONLY
    const blob = new Blob([htmlContent], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `PersonaSay_Summary_${new Date().toISOString().slice(0, 10)}.doc`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    logger.info('Summary exported successfully (chat history excluded)');
  };

  return (
    <div className="flex flex-col h-[650px] rounded-2xl backdrop-blur-sm" style={{backgroundColor: 'rgba(3, 94, 117, 0.18)', border: '1px solid rgba(45, 212, 191, 0.18)'}}>
      {/* Chat Header */}
      <div className="p-6 border-b flex justify-between items-center" style={{borderColor: 'rgba(34, 211, 238, 0.18)'}}>
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-2 h-2 rounded-full" style={{background: 'linear-gradient(45deg, #22d3ee, #2dd4bf)'}}></div>
            <h3 className="text-lg font-semibold text-white tracking-tight">Chat Interface</h3>
          </div>
          <p className="text-sm text-gray-300 ml-5">{selectedPersonasCount} agents active</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={clearChat}
            disabled={chatHistory.length === 0}
            className="text-white px-3 py-2.5 rounded-xl font-medium transition-all duration-200 text-sm flex items-center space-x-2 disabled:cursor-not-allowed backdrop-blur-sm disabled:opacity-50"
            style={{
              backgroundColor: 'rgba(220, 38, 38, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.3)'
            }}
            onMouseEnter={(e) => {
              if (!e.currentTarget.disabled) {
                e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.3)';
                e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.5)';
              }
            }}
            onMouseLeave={(e) => {
              if (!e.currentTarget.disabled) {
                e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.2)';
                e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)';
              }
            }}
            title="Clear chat history"
          >
            <span>🗑️</span>
          </button>
          <button
          onClick={exportToWord}
          disabled={chatHistory.length === 0}
          className="text-white px-4 py-2.5 rounded-xl font-medium transition-all duration-200 text-sm flex items-center space-x-2 disabled:cursor-not-allowed backdrop-blur-sm"
          style={{
            backgroundColor: 'rgba(6, 78, 94, 0.6)',
            border: '1px solid rgba(34, 211, 238, 0.18)'
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.backgroundColor = 'rgba(8, 112, 135, 0.65)';
              e.currentTarget.style.borderColor = 'rgba(45, 212, 191, 0.25)';
            }
          }}
          onMouseLeave={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.backgroundColor = 'rgba(6, 78, 94, 0.6)';
              e.currentTarget.style.borderColor = 'rgba(34, 211, 238, 0.18)';
            }
          }}
          title={`Export conversation${summary ? ' with summary' : ''} to Word document`}
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Export</span>
        </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6 custom-scrollbar">
        {chatHistory.length === 0 && (
          <div className="text-center text-gray-500 py-16">
            <p className="text-sm text-gray-600">Ask a question to start the conversation</p>
          </div>
        )}
        {chatHistory.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start flex-col'}`}
          >
            {!message.isUser && (
              <div className="flex items-center space-x-2 mb-3">
                {(() => {
                  const persona = allPersonas.find(p => p.name === message.sender);
                  return persona ? (
                    <div className="w-6 h-6 rounded-full overflow-hidden border" style={{borderColor: 'rgba(34, 211, 238, 0.35)'}}>
                      {persona.avatar.startsWith('/') ? (
                        <img 
                          src={persona.avatar} 
                          alt={persona.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            target.parentElement!.innerHTML = `<div class=\"w-full h-full bg-cyan-600 flex items-center justify-center text-white text-xs font-bold\">${persona.name.charAt(0)}</div>`;
                          }}
                        />
                      ) : (
                        <div className="w-full h-full bg-cyan-600 flex items-center justify-center text-white text-xs font-bold">
                          {persona.avatar}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-cyan-600 flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"/>
                      </svg>
                    </div>
                  );
                })()}
                <div className="flex items-baseline space-x-2">
                  <span className="text-xs font-medium" style={{color: '#22d3ee'}}>{message.sender}</span>
                  {message.senderRole && (
                    <span className="text-xs text-gray-400">({message.senderRole})</span>
                  )}
                </div>
              </div>
            )}
            <div
              className={`max-w-[85%] p-4 rounded-xl ${
                message.isUser
                  ? 'text-white self-end'
                  : 'text-white self-start'
              }`}
              style={{
                backgroundColor: message.isUser ? 'rgba(1, 35, 43, 0.7)' : (message.content.trim().startsWith('<svg') ? 'transparent' : 'rgba(1, 35, 43, 0.45)'),
                border: '1px solid rgba(34, 211, 238, 0.18)'
              }}
            >
              {message.content.trim().startsWith('<svg') ? (
                <div className="w-full" style={{ backgroundColor: 'transparent' }}>
                  <div className="flex justify-end mb-2">
                    <button
                      onClick={() => setExpandedSvg(message.content)}
                      className="text-white/90 p-1 rounded border"
                      style={{ borderColor: 'rgba(34, 211, 238, 0.35)', backgroundColor: 'rgba(6, 78, 94, 0.6)' }}
                      title="Expand mock"
                      aria-label="Expand mock"
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M4 9V4h5M20 15v5h-5M15 4h5v5M9 20H4v-5"/>
                      </svg>
                    </button>
                  </div>
                  <div
                    style={{ overflowX: 'auto', overflowY: 'visible' }}
                    dangerouslySetInnerHTML={{ __html: message.content }}
                  />
                </div>
              ) : (
                <div 
                  className="text-sm leading-relaxed text-gray-200"
                  dangerouslySetInnerHTML={{ 
                    __html: renderMarkdown(message.content) 
                  }}
                />
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start flex-col">
            <div className="flex items-center space-x-2 mb-3">
              <div className="flex items-center -space-x-1">
                {allPersonas.filter(p => selectedPersonaIds.includes(p.id)).slice(0, 3).map((persona, index) => (
                  <div key={persona.id} className="w-5 h-5 rounded-full overflow-hidden border bg-cyan-600" style={{ zIndex: 10 - index, borderColor: 'rgba(34, 211, 238, 0.35)'}}>
                    {persona.avatar.startsWith('/') ? (
                      <img 
                        src={persona.avatar} 
                        alt={persona.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                          target.parentElement!.innerHTML = `<div class=\"w-full h-full bg-cyan-600 flex items-center justify-center text-white text-xs font-bold\">${persona.name.charAt(0)}</div>`;
                        }}
                      />
                    ) : (
                      <div className="w-full h-full bg-cyan-600 flex items-center justify-center text-white text-xs font-bold">
                        {persona.avatar}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              <span className="text-xs font-medium" style={{color: '#22d3ee'}}>Personas Reasoning</span>
            </div>
            <div className="p-4 rounded-xl max-w-[85%] self-start" style={{backgroundColor: 'rgba(1, 35, 43, 0.45)', border: '1px solid rgba(34, 211, 238, 0.18)'}}>
              <div className="flex space-x-1 mb-2">
                <div className="w-1 h-1 rounded-full animate-bounce" style={{backgroundColor: '#22d3ee'}}></div>
                <div className="w-1 h-1 rounded-full animate-bounce" style={{ backgroundColor: '#22d3ee', animationDelay: '0.1s' }}></div>
                <div className="w-1 h-1 rounded-full animate-bounce" style={{ backgroundColor: '#22d3ee', animationDelay: '0.2s' }}></div>
              </div>
              <p className="text-xs text-gray-400">Analyzing and generating responses...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t" style={{borderColor: 'rgba(34, 211, 238, 0.15)'}}>
        <div className="flex space-x-3 items-end">
          <div className="flex-1">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your question here... Add @persona name to ask a specific persona (e.g., @alex)"
              className="w-full rounded-lg px-4 py-2.5 text-white placeholder-cyan-200/50 focus:outline-none transition-all text-sm border"
              style={{
                backgroundColor: 'rgba(4, 47, 56, 0.6)',
                borderColor: 'rgba(34, 211, 238, 0.18)'
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'rgba(45, 212, 191, 0.55)';
                e.currentTarget.style.backgroundColor = 'rgba(6, 78, 94, 0.7)';
                e.currentTarget.style.boxShadow = '0 0 0 3px rgba(34, 211, 238, 0.15)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'rgba(34, 211, 238, 0.18)';
                e.currentTarget.style.backgroundColor = 'rgba(4, 47, 56, 0.6)';
                e.currentTarget.style.boxShadow = 'none';
              }}
              disabled={selectedPersonasCount === 0}
            />
          </div>
          {/* hidden file input lives near the controls */}
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
                const ext = (f.name.split('.').pop() || '').toLowerCase();
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
                logger.debug(`Files attached: ${valid.length}`);
                valid.forEach(f => logger.debug(`   - ${f.name} (${f.type}, ${f.size} bytes)`));
                setAttachedFiles(valid);
              }
            }}
          />
          {attachedFiles.length > 0 && (
            <div className="text-xs text-cyan-300/80 mr-2">
              {attachedFiles.length} attachment{attachedFiles.length > 1 ? 's' : ''}
            </div>
          )}
          {attachError && (
            <div className="text-xs mr-2 px-2 py-1 rounded border" style={{ color: '#fca5a5', borderColor: 'rgba(239, 68, 68, 0.35)', backgroundColor: 'rgba(127, 29, 29, 0.25)' }}>
              {attachError}
            </div>
          )}
          {/* Attach icon button */}
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
          {/* Mock toggle icon button */}
          <button
            onClick={() => setRequestMock(v => !v)}
            aria-pressed={requestMock}
            role="switch"
            className="relative text-white p-2.5 rounded-lg transition-colors border"
            style={{
              backgroundColor: requestMock ? 'rgba(8, 112, 135, 0.85)' : 'rgba(6, 78, 94, 0.6)',
              borderColor: requestMock ? 'rgba(45, 212, 191, 0.35)' : 'rgba(34, 211, 238, 0.18)',
              boxShadow: requestMock ? '0 0 10px rgba(34, 211, 238, 0.25)' : 'none'
            }}
            title={`Mock: ${requestMock ? 'ON' : 'OFF'}`}
            aria-label={`Mock: ${requestMock ? 'ON' : 'OFF'}`}
          >
            {/* magic-wand icon for mock toggle */}
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              {/* wand handle */}
              <path strokeWidth="2" strokeLinecap="round" d="M4 20L12 12"/>
              {/* wand tip sparkles */}
              <path strokeWidth="2" strokeLinecap="round" d="M15 6l3-3"/>
              <path strokeWidth="2" strokeLinecap="round" d="M14 4v4"/>
              <path strokeWidth="2" strokeLinecap="round" d="M12 6h4"/>
              <path strokeWidth="2" strokeLinecap="round" d="M17 8l2 2"/>
            </svg>
            {/* ON/OFF indicator dot */}
            <span
              className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full"
              style={{ backgroundColor: requestMock ? '#22d3ee' : 'rgba(255,255,255,0.35)' }}
            />
          </button>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || selectedPersonasCount === 0 || isLoading}
            className="text-white p-2.5 rounded-lg transition-colors border disabled:cursor-not-allowed"
            style={{
              background: (!inputMessage.trim() || selectedPersonasCount === 0 || isLoading) 
                ? 'rgba(1, 35, 43, 0.5)'
                : 'linear-gradient(45deg, #22d3ee, #2dd4bf)',
              borderColor: (!inputMessage.trim() || selectedPersonasCount === 0 || isLoading) 
                ? 'rgba(34, 211, 238, 0.1)'
                : 'rgba(34, 211, 238, 0.25)',
              boxShadow: (!inputMessage.trim() || selectedPersonasCount === 0 || isLoading) 
                ? 'none' 
                : '0 0 12px rgba(34, 211, 238, 0.25)'
            }}
            onMouseEnter={(e) => {
              const isDisabled = !inputMessage.trim() || selectedPersonasCount === 0 || isLoading;
              if (!isDisabled) {
                e.currentTarget.style.background = 'linear-gradient(45deg, #06b6d4, #14b8a6)';
                e.currentTarget.style.boxShadow = '0 0 16px rgba(34, 211, 238, 0.35)';
              }
            }}
            onMouseLeave={(e) => {
              const isDisabled = !inputMessage.trim() || selectedPersonasCount === 0 || isLoading;
              if (!isDisabled) {
                e.currentTarget.style.background = 'linear-gradient(45deg, #22d3ee, #2dd4bf)';
                e.currentTarget.style.boxShadow = '0 0 12px rgba(34, 211, 238, 0.25)';
              } else {
                e.currentTarget.style.background = 'rgba(1, 35, 43, 0.5)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l7-7-7-7" />
            </svg>
          </button>
        </div>
      </div>
      {expandedSvg && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
          onClick={() => setExpandedSvg(null)}
        >
          <div
            className="relative bg-transparent max-w-[95vw] max-h-[90vh] w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setExpandedSvg(null)}
              className="absolute -top-2 -right-2 text-white/90 text-xs px-2 py-1 rounded border"
              style={{ borderColor: 'rgba(34, 211, 238, 0.35)', backgroundColor: 'rgba(6, 78, 94, 0.6)' }}
              title="Close"
            >Close</button>
            <div className="w-full h-full overflow-auto" dangerouslySetInnerHTML={{ __html: expandedSvg }} />
          </div>
        </div>
      )}
    </div>
  );
};
