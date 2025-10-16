'use client';

import { useState, useEffect } from 'react';
import { Upload, FileText, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { triggerIngest, getStatus, StatusResponse } from '@/lib/api';

export default function IngestPage() {
  const [repoPath, setRepoPath] = useState('');
  const [sourceType, setSourceType] = useState<'github' | 'local'>('github');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Advanced options
  const [window, setWindow] = useState(80);
  const [overlap, setOverlap] = useState(15);
  const [minLines, setMinLines] = useState(10);

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

  const handleIngest = async () => {
    if (!repoPath.trim()) return;

    setLoading(true);
    setError(null);
    setIngestResult(null);

    try {
      const result = await triggerIngest(repoPath, {
        window,
        overlap,
      });
      setIngestResult(result);
      // Reload status to get updated counts
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingestion failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Page Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Repository Ingestion</h1>
            <p className="text-sm text-gray-600 mt-1">Index a code repository for semantic search</p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Ingestion Form */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Index Repository
            </h2>
            
            <div className="space-y-4">
              {/* Source Type Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Repository Source
                </label>
                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setSourceType('github')}
                    className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                      sourceType === 'github'
                        ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                    }`}
                    disabled={loading}
                  >
                    <div className="text-center">
                      <div className="text-lg mb-1">🌐</div>
                      <div>GitHub URL</div>
                      <div className="text-xs mt-1 opacity-75">Public repositories</div>
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => setSourceType('local')}
                    className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                      sourceType === 'local'
                        ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                    }`}
                    disabled={loading}
                  >
                    <div className="text-center">
                      <div className="text-lg mb-1">📁</div>
                      <div>Local Path</div>
                      <div className="text-xs mt-1 opacity-75">Server filesystem</div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Repository Path Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {sourceType === 'github' ? 'GitHub Repository URL' : 'Local Repository Path'}
                </label>
                <input
                  type="text"
                  value={repoPath}
                  onChange={(e) => setRepoPath(e.target.value)}
                  placeholder={
                    sourceType === 'github'
                      ? 'e.g., https://github.com/facebook/react'
                      : 'e.g., /path/to/your/repo or data/fastapi/fastapi'
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black placeholder-gray-500"
                  disabled={loading}
                />
                <p className="text-sm text-gray-500 mt-1">
                  {sourceType === 'github'
                    ? 'Enter the full GitHub repository URL (e.g., https://github.com/user/repo)'
                    : 'Enter the path to the repository on the server filesystem'}
                </p>
              </div>

              {/* Advanced Options */}
              <div className="border-t pt-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Advanced Options</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Window Size
                    </label>
                    <input
                      type="number"
                      value={window}
                      onChange={(e) => setWindow(parseInt(e.target.value))}
                      min="10"
                      max="200"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                      disabled={loading}
                    />
                    <p className="text-xs text-gray-500">Lines per chunk</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Overlap
                    </label>
                    <input
                      type="number"
                      value={overlap}
                      onChange={(e) => setOverlap(parseInt(e.target.value))}
                      min="0"
                      max={window - 1}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                      disabled={loading}
                    />
                    <p className="text-xs text-gray-500">Overlapping lines</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Min Lines
                    </label>
                    <input
                      type="number"
                      value={minLines}
                      onChange={(e) => setMinLines(parseInt(e.target.value))}
                      min="1"
                      max="50"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                      disabled={loading}
                    />
                    <p className="text-xs text-gray-500">Min non-blank lines</p>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleIngest}
                disabled={loading || !repoPath.trim()}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                    <span>Indexing Repository...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <Upload className="h-4 w-4" />
                    <span>Start Indexing</span>
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <div className="text-red-800">{error}</div>
              </div>
            </div>
          )}

          {/* Success Display */}
          {ingestResult && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <h3 className="text-lg font-medium text-green-900">
                  Indexing Complete!
                </h3>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-white p-3 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {ingestResult.files_scanned}
                  </div>
                  <div className="text-gray-600">Files Scanned</div>
                </div>
                <div className="bg-white p-3 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {ingestResult.files_read}
                  </div>
                  <div className="text-gray-600">Files Read</div>
                </div>
                <div className="bg-white p-3 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {ingestResult.chunks_total}
                  </div>
                  <div className="text-gray-600">Chunks Created</div>
                </div>
                <div className="bg-white p-3 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {ingestResult.duration_seconds}s
                  </div>
                  <div className="text-gray-600">Duration</div>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-white rounded-lg">
                <div className="text-sm text-gray-600">
                  <strong>Average lines per chunk:</strong> {ingestResult.avg_lines_per_chunk}
                </div>
                {ingestResult.files_skipped > 0 && (
                  <div className="text-sm text-gray-600">
                    <strong>Files skipped:</strong> {ingestResult.files_skipped}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Status Card */}
          {status && (
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                System Status
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Index Status</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Indexed</span>
                      <span className={`text-sm font-medium ${status.indexed ? 'text-green-600' : 'text-red-600'}`}>
                        {status.indexed ? 'Yes' : 'No'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Chunks</span>
                      <span className="text-sm font-medium text-gray-900">{status.chunks}</span>
                    </div>
                    {status.last_ingest && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Last Ingest</span>
                        <span className="text-sm font-medium text-gray-900">
                          {new Date(status.last_ingest).toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">System Components</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Model Loaded</span>
                      <span className={`text-sm font-medium ${status.model_loaded ? 'text-green-600' : 'text-red-600'}`}>
                        {status.model_loaded ? 'Yes' : 'No'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Index Loaded</span>
                      <span className={`text-sm font-medium ${status.index_loaded ? 'text-green-600' : 'text-red-600'}`}>
                        {status.index_loaded ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Quick Start Guide */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-blue-900 mb-4">
              Quick Start Guide
            </h2>
            
            <div className="space-y-4 text-sm text-blue-800">
              <div>
                <strong>1. Prepare your repository:</strong>
                <p className="mt-1">Make sure your code repository is accessible from the API server.</p>
              </div>
              
              <div>
                <strong>2. Start indexing:</strong>
                <p className="mt-1">Enter the path to your repository and click "Start Indexing".</p>
              </div>
              
              <div>
                <strong>3. Wait for completion:</strong>
                <p className="mt-1">The process typically takes 5-30 seconds depending on repository size.</p>
              </div>
              
              <div>
                <strong>4. Start searching:</strong>
                <p className="mt-1">Once indexed, go back to the <a href="/" className="underline">search page</a> to start searching your code!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
