import React, { useState, useEffect } from 'react';
import { File, Trash2, Loader } from 'lucide-react';
import { getDocuments, deleteDocument } from '../api';

const DocumentList = ({ onSelectDocument, refreshTrigger, darkMode }) => {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    loadDocs();
  }, [refreshTrigger]);

  const loadDocs = async () => {
    try {
      setLoading(true);
      const data = await getDocuments();
      setDocs(data.documents);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (docId, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(docId);
        setDocs(d => d.filter(doc => doc.id !== docId));
        if (selectedId === docId) {
          setSelectedId(null);
          onSelectDocument?.(null);
        }
      } catch (error) {
        console.error('Error deleting document:', error);
        alert('Failed to delete document');
      }
    }
  };

  const handleSelect = (doc) => {
    setSelectedId(doc.id);
    onSelectDocument?.(doc);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="h-8 w-8 text-purple-500 animate-spin" />
      </div>
    );
  }

  if (docs.length === 0) {
    return (
      <div className={`text-center py-12 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
        <File className={`mx-auto h-12 w-12 mb-4 opacity-50 ${darkMode ? 'text-gray-600' : 'text-gray-400'}`} />
        <p>No documents uploaded yet</p>
        <p className="text-sm mt-2">Upload a PDF to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {docs.map((doc) => {
        const isSelected = selectedId === doc.id;
        const borderClass = isSelected
          ? darkMode ? 'border-purple-500 bg-blue-900/20' : 'border-purple-500 bg-blue-50'
          : darkMode ? 'border-gray-700 hover:border-gray-600 hover:bg-gray-700/50' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50';

        return (
          <div
            key={doc.id}
            onClick={() => handleSelect(doc)}
            className={`p-4 rounded-lg border cursor-pointer transition-all ${borderClass}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <File className="h-5 w-5 text-red-500 flex-shrink-0" />
                  <h3 className={`font-medium truncate ${darkMode ? 'text-gray-200' : 'text-gray-900'}`}>
                    {doc.name}
                  </h3>
                  {!doc.processed && (
                    <Loader className="h-4 w-4 text-purple-500 animate-spin" />
                  )}
                </div>
                <div className={`flex items-center space-x-4 text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <span>{doc.page_count} pages</span>
                  <span>{formatSize(doc.file_size)}</span>
                  <span>{new Date(doc.upload_date).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2 ml-4">
                <button
                  onClick={(e) => handleDelete(doc.id, e)}
                  className={`p-2 rounded transition-colors ${
                    darkMode ? 'text-red-400 hover:bg-red-900/30' : 'text-red-600 hover:bg-red-50'
                  }`}
                  title="Delete document"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default DocumentList;
