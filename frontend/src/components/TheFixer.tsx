import React, { useState, useEffect } from 'react';
import { logger } from '../utils/logger';

interface TheFixerProps {
  apiKey: string;
}

interface FixerReport {
  timestamp: string;
  total_errors: number;
  recurring_issues: number;
  high_severity_errors: number;
  recurring_issues_details: Record<string, any>;
  high_severity_details: any[];
  recent_solutions: any[];
  error_categories: Record<string, number>;
}

interface FixerAnalysis {
  root_cause: string;
  immediate_fix: string[];
  prevention: string;
  alternatives: string[];
  priority: string;
  error_entry?: any;
}

export const TheFixer: React.FC<TheFixerProps> = ({ apiKey }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [report, setReport] = useState<FixerReport | null>(null);
  const [analysis, setAnalysis] = useState<FixerAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const fetchReport = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8001/fixer/report', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setReport(data);
      setErrorMessage('');
    } catch (error) {
      logger.error('Error fetching Fixer report:', error);
      setErrorMessage('Failed to fetch report');
    } finally {
      setLoading(false);
    }
  };

  const invokeFixer = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8001/fixer/invoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      logger.info('The Fixer invoked:', data);
      await fetchReport(); // Refresh report after invocation
    } catch (error) {
      logger.error('Error invoking The Fixer:', error);
      setErrorMessage('Failed to invoke The Fixer');
    } finally {
      setLoading(false);
    }
  };

  const analyzeError = async (errorMessage: string, context: any = {}) => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8001/fixer/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          error_message: errorMessage,
          context: context
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
      setErrorMessage('');
    } catch (error) {
      logger.error('Error analyzing with Fixer:', error);
      setErrorMessage('Failed to analyze error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchReport();
    }
  }, [isOpen]);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg shadow-lg z-50 flex items-center space-x-2"
      >
        <span className="text-xl">🔧</span>
        <span>The Fixer</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-6 w-11/12 max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-red-400">🔧 The Fixer</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="text-zinc-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        {errorMessage && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-2 rounded mb-4">
            {errorMessage}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Report Section */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-lime-400">Debug Report</h3>
              <button
                onClick={invokeFixer}
                disabled={loading}
                className="bg-red-600 hover:bg-red-700 disabled:bg-zinc-600 text-white px-3 py-1 rounded text-sm"
              >
                {loading ? 'Loading...' : 'Invoke Fixer'}
              </button>
            </div>

            {report && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-zinc-800 p-3 rounded">
                    <div className="text-2xl font-bold text-red-400">{report.total_errors}</div>
                    <div className="text-sm text-zinc-400">Total Errors</div>
                  </div>
                  <div className="bg-zinc-800 p-3 rounded">
                    <div className="text-2xl font-bold text-yellow-400">{report.recurring_issues}</div>
                    <div className="text-sm text-zinc-400">Recurring</div>
                  </div>
                  <div className="bg-zinc-800 p-3 rounded">
                    <div className="text-2xl font-bold text-red-500">{report.high_severity_errors}</div>
                    <div className="text-sm text-zinc-400">High Severity</div>
                  </div>
                </div>

                {Object.keys(report.error_categories).length > 0 && (
                  <div>
                    <h4 className="text-md font-semibold text-lime-400 mb-2">Error Categories</h4>
                    <div className="space-y-2">
                      {Object.entries(report.error_categories).map(([category, count]) => (
                        <div key={category} className="flex justify-between items-center bg-zinc-800 px-3 py-2 rounded">
                          <span className="text-zinc-300 capitalize">{category}</span>
                          <span className="text-lime-400 font-semibold">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Object.keys(report.recurring_issues_details).length > 0 && (
                  <div>
                    <h4 className="text-md font-semibold text-yellow-400 mb-2">Recurring Issues</h4>
                    <div className="space-y-2">
                      {Object.entries(report.recurring_issues_details).map(([issue, details]: [string, any]) => (
                        <div key={issue} className="bg-zinc-800 p-3 rounded">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-zinc-300 text-sm">{issue}</span>
                            <span className="text-yellow-400 font-semibold">{details.count}x</span>
                          </div>
                          <div className="text-xs text-zinc-500">
                            First: {new Date(details.first_occurrence).toLocaleString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Analysis Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-lime-400">Error Analysis</h3>
            
            <div className="space-y-3">
              <button
                onClick={() => analyzeError("CORS policy error: Access to fetch blocked", {endpoint: "/summary"})}
                className="w-full text-left bg-zinc-800 hover:bg-zinc-700 p-3 rounded border border-zinc-700"
              >
                <div className="text-red-400 font-semibold">CORS Error</div>
                <div className="text-sm text-zinc-400">Access to fetch blocked by CORS policy</div>
              </button>

              <button
                onClick={() => analyzeError("TypeError: Failed to fetch", {component: "SummaryPanel"})}
                className="w-full text-left bg-zinc-800 hover:bg-zinc-700 p-3 rounded border border-zinc-700"
              >
                <div className="text-red-400 font-semibold">Network Error</div>
                <div className="text-sm text-zinc-400">Failed to fetch resource</div>
              </button>

              <button
                onClick={() => analyzeError("AuthenticationError: Incorrect API key", {endpoint: "/summary"})}
                className="w-full text-left bg-zinc-800 hover:bg-zinc-700 p-3 rounded border border-zinc-700"
              >
                <div className="text-red-400 font-semibold">Auth Error</div>
                <div className="text-sm text-zinc-400">Incorrect API key provided</div>
              </button>
            </div>

            {analysis && (
              <div className="bg-zinc-800 p-4 rounded border border-zinc-700">
                <h4 className="text-md font-semibold text-lime-400 mb-3">Analysis Result</h4>
                
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-zinc-400">Root Cause</div>
                    <div className="text-zinc-300">{analysis.root_cause}</div>
                  </div>

                  <div>
                    <div className="text-sm text-zinc-400">Immediate Fix</div>
                    <div className="space-y-1">
                      {analysis.immediate_fix?.map((step: string, index: number) => (
                        <div key={index} className="text-zinc-300 text-sm">
                          {index + 1}. {step}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-zinc-400">Prevention</div>
                    <div className="text-zinc-300">{analysis.prevention}</div>
                  </div>

                  <div>
                    <div className="text-sm text-zinc-400">Priority</div>
                    <div className={`font-semibold ${
                      analysis.priority === 'high' ? 'text-red-400' : 
                      analysis.priority === 'medium' ? 'text-yellow-400' : 'text-green-400'
                    }`}>
                      {analysis.priority.toUpperCase()}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 