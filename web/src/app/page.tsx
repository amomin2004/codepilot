'use client';

import { useState, useEffect } from 'react';
import { Search, FileText, Clock, Filter, Code, Copy, ExternalLink } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { searchCode, getStatus, SearchResult, StatusResponse } from '@/lib/api';

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [pathFilter, setPathFilter] = useState('');
  const [langFilter, setLangFilter] = useState('');
  const [resultCount, setResultCount] = useState(5);

  // Load status on mount
  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const statusData = await getStatus();
      setStatus(statusData);
    } catch (err) {
      console.error('Failed to load status:', err);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults([]);
    setLatency(null);

    try {
      const response = await searchCode(query, resultCount, {
        pathContains: pathFilter || undefined,
        lang: langFilter || undefined,
      });

      setResults(response.results);
      setLatency(response.latency_ms);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getLanguageFromExt = (path: string): string => {
    const ext = path.split('.').pop()?.toLowerCase();
    const langMap: { [key: string]: string } = {
      py: 'python',
      ts: 'typescript',
      tsx: 'typescript',
      js: 'javascript',
      jsx: 'javascript',
      go: 'go',
      java: 'java',
      rs: 'rust',
      cpp: 'cpp',
      c: 'c',
      h: 'c',
      rb: 'ruby',
      php: 'php',
      swift: 'swift',
      scala: 'scala',
      sh: 'bash',
      sql: 'sql',
    };
    return langMap[ext || ''] || 'text';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Status Bar */}
      {status && (
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-center space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${status.indexed ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-gray-600">
                  {status.indexed ? `${status.chunks} chunks indexed` : 'Not indexed'}
                </span>
              </div>
              {status.last_ingest && (
                <div className="flex items-center space-x-1 text-gray-500">
                  <Clock className="h-4 w-4" />
                  <span>Last indexed: {new Date(status.last_ingest).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
          <div className="space-y-4">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Search code semantically... (e.g., 'How do I validate JWT tokens?')"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg text-black placeholder-gray-500"
                disabled={loading}
              />
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Filter className="h-4 w-4 inline mr-1" />
                  Path contains
                </label>
                <input
                  type="text"
                  value={pathFilter}
                  onChange={(e) => setPathFilter(e.target.value)}
                  placeholder="e.g., auth, middleware"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black placeholder-gray-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Language
                </label>
                <select
                  value={langFilter}
                  onChange={(e) => setLangFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                >
                  <option value="">All languages</option>
                  <option value="python">Python</option>
                  <option value="typescript">TypeScript</option>
                  <option value="javascript">JavaScript</option>
                  <option value="go">Go</option>
                  <option value="java">Java</option>
                  <option value="rust">Rust</option>
                  <option value="cpp">C++</option>
                  <option value="c">C</option>
                  <option value="ruby">Ruby</option>
                  <option value="php">PHP</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Results
                </label>
                <select
                  value={resultCount}
                  onChange={(e) => setResultCount(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                >
                  <option value={5}>5 results</option>
                  <option value={10}>10 results</option>
                  <option value={20}>20 results</option>
                </select>
              </div>
            </div>

            {/* Search Button */}
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                  <span>Searching...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <Search className="h-4 w-4" />
                  <span>Search Code</span>
                </div>
              )}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <div className="text-red-600">⚠️</div>
              <div className="text-red-800">{error}</div>
            </div>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-4">
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                Search Results ({results.length})
              </h2>
              {latency && (
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Clock className="h-4 w-4" />
                  <span>{latency}ms</span>
                </div>
              )}
            </div>

            {/* Results List */}
            {results.map((result, index) => (
              <div key={index} className="bg-white rounded-lg border shadow-sm overflow-hidden">
                {/* Result Header */}
                <div className="p-4 border-b bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-gray-500" />
                      <div>
                        <div className="font-medium text-gray-900">
                          {result.path}
                        </div>
                        <div className="text-sm text-gray-600">
                          Lines {result.start_line}-{result.end_line} • {result.lang} • Score: {result.score.toFixed(3)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => copyToClipboard(result.preview)}
                        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                        title="Copy code"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                      <button
                        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                        title="Open in GitHub"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Code Preview */}
                <div className="p-0">
                  <SyntaxHighlighter
                    language={getLanguageFromExt(result.path)}
                    style={tomorrow}
                    showLineNumbers={true}
                    startingLineNumber={result.start_line}
                    customStyle={{
                      margin: 0,
                      borderRadius: 0,
                      fontSize: '14px',
                    }}
                  >
                    {result.preview}
                  </SyntaxHighlighter>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && query && !error && (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
            <p className="text-gray-600">
              Try adjusting your search query or filters.
            </p>
          </div>
        )}

        {/* Welcome State */}
        {!query && !loading && (
          <div className="text-center py-12">
            <div className="bg-white rounded-xl shadow-sm border p-8 max-w-2xl mx-auto">
              <Code className="h-16 w-16 text-blue-600 mx-auto mb-6" />
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Search Your Code Semantically
              </h2>
              <p className="text-gray-600 mb-6">
                Ask questions about your code in natural language. Find functions, classes, 
                and patterns without knowing exact names or keywords.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-medium text-blue-900 mb-2">Example queries:</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• "How do I validate JWT tokens?"</li>
                    <li>• "WebSocket connection handling"</li>
                    <li>• "Database migration functions"</li>
                    <li>• "Error handling middleware"</li>
                  </ul>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="font-medium text-green-900 mb-2">Features:</h3>
                  <ul className="text-sm text-green-800 space-y-1">
                    <li>• Semantic similarity search</li>
                    <li>• Multi-language support</li>
                    <li>• Path and language filters</li>
                    <li>• Syntax-highlighted results</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}