import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { queryDocument } from '../api';

const ChatInterface = ({ document, conversationId, darkMode }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { sender: 'user', text: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const saved = localStorage.getItem('apiSettings');
      const apiSettings = saved ? JSON.parse(saved) : null;

      const response = await queryDocument(input, document?.id, conversationId, apiSettings);

      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: response.answer,
        citations: response.citations,
        chunks: response.chunks,
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Query error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: `Error: ${errorMsg}`,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className={`border-b p-4 transition-colors ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'}`}>
        <div className="flex items-center space-x-3">
          {document ? (
            <>
              <FileText className={`h-5 w-5 ${darkMode ? 'text-purple-400' : 'text-purple-600'}`} />
              <div>
                <h2 className={`font-semibold ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>{document.name}</h2>
                <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  {document.page_count} pages
                </p>
              </div>
            </>
          ) : (
            <div>
              <h2 className={`font-semibold ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>DocuQuery</h2>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Select a document to start chatting</p>
            </div>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className={`flex-1 overflow-y-auto p-4 space-y-4 transition-colors ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        {messages.length === 0 && document && (
          <div className={`text-center py-12 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            <p className="text-lg mb-2">Ready to chat!</p>
            <p className="text-sm">Ask me anything about this document</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-3xl rounded-lg p-4 ${
                message.sender === 'user'
                  ? darkMode 
                    ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg'
                    : 'bg-purple-600 text-white'
                  : darkMode
                    ? 'bg-gray-800 text-gray-100 shadow-lg border border-gray-700'
                    : 'bg-white text-gray-900 shadow'
              }`}
            >
              <div className={`prose prose-sm max-w-none ${darkMode && message.sender !== 'user' ? 'prose-invert' : ''}`}>
                {message.sender === 'user' ? (
                  <p className="text-white m-0">{message.text}</p>
                ) : (
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                )}
              </div>
              
              {message.citations && message.citations.length > 0 && (
                <div className={`mt-3 pt-3 ${darkMode ? 'border-t border-gray-700' : 'border-t border-gray-200'}`}>
                  <p className={`text-xs mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Sources:</p>
                  <div className="flex flex-wrap gap-2">
                    {message.citations.map((page, idx) => (
                      <span
                        key={idx}
                        className={`inline-flex items-center px-2 py-1 rounded text-xs ${
                          darkMode 
                            ? 'bg-purple-900 text-purple-200'
                            : 'bg-purple-100 text-purple-800'
                        }`}
                      >
                        Page {page}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <p className={`text-xs mt-2 ${message.sender === 'user' ? 'opacity-70' : darkMode ? 'text-gray-500' : 'opacity-60'}`}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className={`rounded-lg p-4 shadow ${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'}`}>
              <Loader className={`h-5 w-5 animate-spin ${darkMode ? 'text-purple-400' : 'text-purple-500'}`} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className={`border-t p-4 transition-colors ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'}`}>
        {document ? (
          <div className="flex space-x-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about the document..."
              className={`flex-1 resize-none border rounded-lg p-3 focus:outline-none focus:ring-2 transition-colors ${
                darkMode 
                  ? 'bg-gray-900 border-gray-600 text-gray-100 placeholder-gray-500 focus:border-purple-500 focus:ring-purple-500'
                  : 'bg-white border-gray-300 text-gray-900 focus:border-purple-500 focus:ring-purple-500'
              }`}
              rows="2"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className={`px-6 rounded-lg transition-all ${
                darkMode
                  ? 'bg-purple-600 text-white hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500'
                  : 'bg-purple-600 text-white hover:bg-blue-700 disabled:bg-gray-300'
              } disabled:cursor-not-allowed`}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        ) : (
          <div className={`text-center py-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Please select a document to start chatting
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
