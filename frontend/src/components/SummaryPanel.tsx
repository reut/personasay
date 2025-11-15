import React, { useState } from 'react';
import { marked } from 'marked';
import { config } from '../config';
import { logger } from '../utils/logger';

interface SummaryPanelProps {
  context: any;
  chatHistory: any[];
  setSummary: (summary: any) => void;
  summary: any;
  allPersonas: any[];
  selectedPersonaIds: string[];
}

// Enhanced renderer for summary formatting with special KPI highlighting
const renderSummary = (text: string) => {
  // Split the summary to identify and specially format the KPI section
  const kpiSectionMatch = text.match(/## 6\. Success Metrics & KPIs[\s\S]*$/);
  
  if (kpiSectionMatch) {
    const beforeKpis = text.substring(0, kpiSectionMatch.index);
    const kpiSection = kpiSectionMatch[0];
    
    // Process both parts separately
    const processedBefore = processMarkdown(beforeKpis);
    const processedKpis = processKpiSection(kpiSection);
    
    return processedBefore + processedKpis;
  }
  
  // Process markdown content with cyan/teal HUD styling
  return processMarkdown(text);
};

// Special processor for KPI section with enhanced visual treatment
const processKpiSection = (text: string) => {
  let processed = text;
  
  // Main KPI section header with special styling
  processed = processed.replace(
    /## 6\. Success Metrics & KPIs/g, 
    '<div class="mt-8 mb-4 p-4 rounded-lg" style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(20, 184, 166, 0.15)); border-left: 4px solid #06b6d4;"><h2 class="text-xl font-bold text-cyan-300 flex items-center"><span class="w-3 h-3 bg-cyan-400 rounded-full mr-3"></span>Success Metrics & KPIs</h2></div>'
  );
  
  // Enhanced KPI item headers with badges
  processed = processed.replace(
    /\*\*KPI (\d+): ([^*]+)\*\*/g,
    '<div class="mt-6 mb-3 p-3 rounded-lg border border-cyan-400/30" style="background: rgba(8, 145, 178, 0.12);"><h3 class="text-lg font-semibold text-cyan-300 flex items-center"><span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-cyan-500/20 text-cyan-300 text-sm font-bold mr-3 border border-cyan-400/40">$1</span>$2</h3></div>'
  );
  
  // Style KPI attributes with icons/emojis for visual scanning
  processed = processed.replace(/- \*\*What to Measure\*\*:/g, '<li class="ml-6 text-gray-200 mb-2 flex items-start"><span class="text-cyan-400 mr-2 flex-shrink-0 font-bold">📊</span><strong class="text-cyan-300 mr-2">What to Measure:</strong>');
  processed = processed.replace(/- \*\*Target\*\*:/g, '<li class="ml-6 text-gray-200 mb-2 flex items-start"><span class="text-teal-400 mr-2 flex-shrink-0 font-bold">🎯</span><strong class="text-teal-300 mr-2">Target:</strong>');
  processed = processed.replace(/- \*\*Timeline\*\*:/g, '<li class="ml-6 text-gray-200 mb-2 flex items-start"><span class="text-amber-400 mr-2 flex-shrink-0 font-bold">⏱️</span><strong class="text-amber-300 mr-2">Timeline:</strong>');
  processed = processed.replace(/- \*\*How to Measure\*\*:/g, '<li class="ml-6 text-gray-200 mb-2 flex items-start"><span class="text-purple-400 mr-2 flex-shrink-0 font-bold">📏</span><strong class="text-purple-300 mr-2">How to Measure:</strong>');
  processed = processed.replace(/- \*\*Type\*\*:/g, '<li class="ml-6 text-gray-200 mb-2 flex items-start"><span class="text-blue-400 mr-2 flex-shrink-0 font-bold">🏷️</span><strong class="text-blue-300 mr-2">Type:</strong>');
  processed = processed.replace(/- \*\*Owner\*\*:/g, '<li class="ml-6 text-gray-200 mb-2 flex items-start"><span class="text-green-400 mr-2 flex-shrink-0 font-bold">👤</span><strong class="text-green-300 mr-2">Owner:</strong>');
  
  // Handle remaining markdown
  processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong class="text-cyan-300 font-semibold">$1</strong>');
  processed = processed.replace(/\*(.*?)\*/g, '<em class="text-teal-200 italic">$1</em>');
  processed = processed.replace(/\n\n/g, '</p><p class="mb-3 text-gray-200 leading-relaxed">');
  processed = processed.replace(/\n/g, '<br>');
  
  return processed;
};

const processMarkdown = (text: string) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-cyan-300 font-semibold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-teal-200 italic">$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-cyan-900/30 border border-cyan-400/30 px-2 py-1 rounded text-cyan-200 text-sm font-mono">$1</code>')
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold text-cyan-400 mt-6 mb-3 flex items-center"><span class="w-2 h-2 bg-cyan-500 rounded-full mr-2"></span>$1</h3>')
    .replace(/^## (\d+)\. (.*$)/gm, '<h2 class="text-xl font-bold text-cyan-300 mt-8 mb-4 flex items-center"><span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-300 text-sm font-bold mr-3 border border-cyan-400/40">$1</span>$2</h2>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-cyan-300 mt-8 mb-4 flex items-center"><span class="w-3 h-3 bg-cyan-500 rounded-full mr-3"></span>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-cyan-200 mt-8 mb-6">$1</h1>')
    .replace(/^\* (.*$)/gm, '<li class="ml-6 text-gray-200 mb-1 flex items-start"><span class="text-cyan-400 mr-2 flex-shrink-0">•</span><span>$1</span></li>')
    .replace(/^- (.*$)/gm, '<li class="ml-6 text-gray-200 mb-1 flex items-start"><span class="text-cyan-400 mr-2 flex-shrink-0">•</span><span>$1</span></li>')
    .replace(/^\d+\. (.*$)/gm, '<li class="ml-6 text-gray-200 mb-1">$&</li>')
    .replace(/\n\n/g, '</p><p class="mb-3 text-gray-200 leading-relaxed">')
    .replace(/\n/g, '<br>');
};

export const SummaryPanel = ({ context, chatHistory, setSummary, summary, allPersonas, selectedPersonaIds }: SummaryPanelProps) => {
  const [isLoading, setIsLoading] = useState(false);

  const generateSummary = async () => {
    if (chatHistory.length === 0) return;

    setIsLoading(true);

    try {
      // Send only selected personas to backend for focused summary
      const selectedPersonas = allPersonas.filter(p => selectedPersonaIds.includes(p.id));

      const response = await fetch(`${config.api.baseUrl}/summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context: context,
          history: chatHistory.map(msg => ({
            role: msg.isUser ? 'user' : 'assistant',
            content: msg.content,
            sender: msg.sender
          })),
          personas: selectedPersonas
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSummary(data.summary);
    } catch (error) {
      logger.error('Error generating summary:', error);
      setSummary('Error generating summary. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <div className="rounded-2xl p-6 mt-6 backdrop-blur-sm" style={{backgroundColor: 'rgba(3, 94, 117, 0.18)', border: '1px solid rgba(45, 212, 191, 0.18)'}}>
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-2 h-2 rounded-full" style={{background: 'linear-gradient(45deg, #22d3ee, #2dd4bf)'}}></div>
          <h3 className="text-lg font-semibold text-white tracking-tight">Analysis, Insights & KPIs</h3>
        </div>
        <button
          onClick={generateSummary}
          disabled={chatHistory.length === 0 || isLoading}
          className="text-white px-4 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center space-x-2 text-sm disabled:cursor-not-allowed backdrop-blur-sm"
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
        >
          {isLoading && (
            <div className="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin"></div>
          )}
          <span>{isLoading ? 'Analyzing...' : 'Generate Analysis + KPIs'}</span>
        </button>
      </div>

      {summary && (
        <div className="space-y-6">

          
          {/* Use single block approach to preserve HTML integrity */}
          <div className="bg-cyan-900/20 border border-cyan-400/20 rounded-xl p-6 backdrop-blur-sm">
            <h4 className="text-base font-semibold text-cyan-300 mb-4 flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full" style={{background: '#22d3ee'}}></div>
              <span className="text-cyan-300">Analysis & Insights</span>
            </h4>
            <div 
              className="text-sm text-gray-200 leading-relaxed prose prose-invert max-w-none"
              dangerouslySetInnerHTML={{ 
                __html: renderSummary(summary) 
              }}
            />
          </div>
        </div>
      )}

      {!summary && chatHistory.length > 0 && (
        <div className="text-center text-gray-600 py-12">
          <p className="text-sm">Generate analysis to see insights from the conversation</p>
        </div>
      )}

      {chatHistory.length === 0 && (
        <div className="text-center text-gray-600 py-12">
          <p className="text-sm">Start a conversation to enable analysis</p>
        </div>
      )}
    </div>
  );
};
