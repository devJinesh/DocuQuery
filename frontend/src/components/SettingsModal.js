import React, { useState, useEffect } from 'react';
import { X, Settings, AlertCircle, Check } from 'lucide-react';

const SettingsModal = ({ isOpen, onClose, darkMode }) => {
  const [apiBaseUrl, setApiBaseUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('apiSettings');
    if (saved) {
      const settings = JSON.parse(saved);
      setApiBaseUrl(settings.apiBaseUrl || '');
      setApiKey(settings.apiKey || '');
      setModel(settings.model || '');
    }
  }, [isOpen]);

  const handleSave = () => {
    const settings = {
      apiBaseUrl: apiBaseUrl.trim(),
      apiKey: apiKey.trim(),
      model: model.trim(),
    };
    
    if (settings.apiBaseUrl || settings.apiKey || settings.model) {
      localStorage.setItem('apiSettings', JSON.stringify(settings));
    } else {
      localStorage.removeItem('apiSettings');
    }
    
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 1500);
  };

  const handleClear = () => {
    setApiBaseUrl('');
    setApiKey('');
    setModel('');
    localStorage.removeItem('apiSettings');
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 1500);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className={`w-full max-w-2xl rounded-xl shadow-2xl transition-colors ${
        darkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        {/* Header */}
        <div className={`flex items-center justify-between p-6 border-b ${
          darkMode ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <div className="flex items-center space-x-3">
            <Settings className={`h-6 w-6 ${darkMode ? 'text-purple-400' : 'text-purple-600'}`} />
            <h2 className={`text-xl font-semibold ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>
              API Configuration
            </h2>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg transition-colors ${
              darkMode 
                ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
                : 'hover:bg-gray-100 text-gray-500 hover:text-gray-700'
            }`}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Info Alert */}
          <div className={`flex space-x-3 p-4 rounded-lg ${
            darkMode 
              ? 'bg-purple-900 bg-opacity-30 border border-purple-800'
              : 'bg-purple-50 border border-purple-200'
          }`}>
            <AlertCircle className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
              darkMode ? 'text-purple-400' : 'text-purple-600'
            }`} />
            <div className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              <p className="font-medium mb-1">Optional Configuration</p>
              <p>Leave these fields empty to use the default backend configuration. Custom settings are stored locally in your browser.</p>
              <p className="mt-2 text-xs opacity-75">
                <strong>Security Note:</strong> For deployed apps, use backend configuration only. Frontend storage is suitable for local/personal use.
              </p>
            </div>
          </div>

          {/* API Base URL */}
          <div className="space-y-2">
            <label className={`block text-sm font-medium ${
              darkMode ? 'text-gray-200' : 'text-gray-700'
            }`}>
              API Base URL
            </label>
            <input
              type="text"
              value={apiBaseUrl}
              onChange={(e) => setApiBaseUrl(e.target.value)}
              placeholder="e.g., https://api.openai.com/v1 or https://integrate.api.nvidia.com/v1"
              className={`w-full px-4 py-2.5 rounded-lg border transition-colors focus:outline-none focus:ring-2 ${
                darkMode
                  ? 'bg-gray-900 border-gray-600 text-gray-100 placeholder-gray-500 focus:border-purple-500 focus:ring-purple-500'
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500'
              }`}
            />
            <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
              The base URL for your OpenAI-compatible API endpoint
            </p>
          </div>

          {/* API Key */}
          <div className="space-y-2">
            <label className={`block text-sm font-medium ${
              darkMode ? 'text-gray-200' : 'text-gray-700'
            }`}>
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your API key"
              className={`w-full px-4 py-2.5 rounded-lg border transition-colors focus:outline-none focus:ring-2 ${
                darkMode
                  ? 'bg-gray-900 border-gray-600 text-gray-100 placeholder-gray-500 focus:border-purple-500 focus:ring-purple-500'
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500'
              }`}
            />
            <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
              Your API authentication key
            </p>
          </div>

          {/* Model Name */}
          <div className="space-y-2">
            <label className={`block text-sm font-medium ${
              darkMode ? 'text-gray-200' : 'text-gray-700'
            }`}>
              Model Name
            </label>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="e.g., gpt-4, gpt-3.5-turbo, or moonshotai/kimi-k2-instruct-0905"
              className={`w-full px-4 py-2.5 rounded-lg border transition-colors focus:outline-none focus:ring-2 ${
                darkMode
                  ? 'bg-gray-900 border-gray-600 text-gray-100 placeholder-gray-500 focus:border-purple-500 focus:ring-purple-500'
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500'
              }`}
            />
            <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
              The model identifier to use for chat completions
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className={`flex justify-between p-6 border-t ${
          darkMode ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <button
            onClick={handleClear}
            className={`px-6 py-2.5 rounded-lg font-medium transition-all ${
              darkMode
                ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Clear Settings
          </button>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className={`px-6 py-2.5 rounded-lg font-medium transition-all ${
                darkMode
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saved}
              className={`px-6 py-2.5 rounded-lg font-medium transition-all flex items-center space-x-2 ${
                saved
                  ? darkMode
                    ? 'bg-green-600 text-white'
                    : 'bg-green-500 text-white'
                  : darkMode
                    ? 'bg-purple-600 text-white hover:bg-purple-700'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
            >
              {saved ? (
                <>
                  <Check className="h-5 w-5" />
                  <span>Saved!</span>
                </>
              ) : (
                <span>Save Settings</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
