import React, { useState, useEffect } from 'react';
import { FileText, Upload as UploadIcon, MessageSquare, Settings, Moon, Sun } from 'lucide-react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import SettingsModal from './components/SettingsModal';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('documents');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  const hasCustomSettings = () => !!localStorage.getItem('apiSettings');

  useEffect(() => {
    document.body.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const handleUploadSuccess = () => setRefreshTrigger(prev => prev + 1);

  const handleDocSelect = (doc) => {
    setSelectedDoc(doc);
    if (doc) setActiveTab('chat');
  };

  const tabs = [
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'upload', label: 'Upload', icon: UploadIcon },
    { id: 'chat', label: 'Chat', icon: MessageSquare },
  ];

  return (
    <div className={`h-screen flex flex-col ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'} shadow-sm border-b`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl shadow-lg">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className={`text-2xl font-bold ${
                  darkMode ? 'bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent' : 'text-gray-900'
                }`}>
                  DocuQuery
                </h1>
                <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  AI-Powered Document Analysis
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSettingsOpen(true)}
                className={`relative p-2 rounded-lg transition-colors ${
                  darkMode 
                    ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
                title="API Settings"
              >
                <Settings className="h-5 w-5" />
                {hasCustomSettings() && (
                  <span className="absolute -top-1 -right-1 h-3 w-3 bg-green-400 rounded-full border-2 border-white"></span>
                )}
              </button>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2 rounded-lg transition-colors ${
                  darkMode 
                    ? 'bg-gray-700 hover:bg-gray-600 text-yellow-400' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
                title={darkMode ? 'Light Mode' : 'Dark Mode'}
              >
                {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className={`w-80 ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'} border-r flex flex-col shadow-lg`}>
          {/* Tabs */}
          <div className={`flex ${darkMode ? 'border-gray-700' : 'border-gray-200'} border-b`}>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 border-b-2 transition-all ${
                  activeTab === tab.id
                    ? darkMode
                      ? 'border-purple-500 text-purple-400 bg-purple-900/30'
                      : 'border-purple-600 text-purple-600 bg-purple-50'
                    : darkMode
                      ? 'border-transparent text-gray-400 hover:text-gray-300 hover:bg-gray-700/30'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span className="font-medium text-sm">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === 'documents' && (
              <DocumentList
                onSelectDocument={handleDocSelect}
                refreshTrigger={refreshTrigger}
                darkMode={darkMode}
              />
            )}

            {activeTab === 'upload' && (
              <div>
                <h2 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  Upload Documents
                </h2>
                <DocumentUpload onUploadSuccess={handleUploadSuccess} darkMode={darkMode} />
              </div>
            )}

            {activeTab === 'chat' && (
              <div className="text-center text-gray-500 py-8">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Chat interface is displayed in the main area</p>
              </div>
            )}
          </div>
        </div>

        <div className={`flex-1 flex flex-col ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
          {activeTab === 'chat' || selectedDoc ? (
            <ChatInterface document={selectedDoc} darkMode={darkMode} />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className={`inline-block p-6 rounded-2xl mb-6 ${
                  darkMode ? 'bg-gray-800' : 'bg-white shadow-xl'
                }`}>
                  <FileText className={`h-24 w-24 mx-auto ${
                    darkMode ? 'text-gray-600' : 'text-gray-300'
                  }`} />
                </div>
                <h2 className={`text-3xl font-bold mb-3 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  Welcome to DocuQuery
                </h2>
                <p className={`text-lg mb-6 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  Upload a PDF document to analyze with AI
                </p>
                <button
                  onClick={() => setActiveTab('upload')}
                  className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl transform hover:scale-105 font-medium"
                >
                  Upload Your First Document
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <SettingsModal 
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        darkMode={darkMode}
      />
    </div>
  );
}

export default App;
