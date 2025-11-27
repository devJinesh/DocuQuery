import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Loader, CheckCircle, File } from 'lucide-react';
import { uploadDocument } from '../api';

const DocumentUpload = ({ onUploadSuccess, darkMode }) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState([]);

  const onDrop = useCallback(async (files) => {
    setUploading(true);
    setProgress(files.map(f => ({ name: f.name, status: 'uploading' })));

    for (let i = 0; i < files.length; i++) {
      try {
        const result = await uploadDocument(files[i]);
        setProgress(prev => 
          prev.map((p, idx) => idx === i ? { ...p, status: 'success', id: result.id } : p)
        );
        onUploadSuccess?.(result);
      } catch (error) {
        console.error('Upload failed:', error);
        setProgress(prev => 
          prev.map((p, idx) => idx === i ? { ...p, status: 'error', error: error.message } : p)
        );
      }
    }

    setUploading(false);
    setTimeout(() => setProgress([]), 3000);
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: true,
  });

  const dragClass = isDragActive
    ? darkMode ? 'border-purple-500 bg-blue-900/20' : 'border-purple-500 bg-blue-50'
    : darkMode ? 'border-gray-700 hover:border-gray-600 bg-gray-800/50' : 'border-gray-300 hover:border-gray-400 bg-white';

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${dragClass}`}
      >
        <input {...getInputProps()} />
        <Upload className={`mx-auto h-16 w-16 mb-4 ${
          isDragActive ? 'text-purple-500' : darkMode ? 'text-gray-600' : 'text-gray-400'
        }`} />
        {isDragActive ? (
          <p className="text-lg text-purple-600 font-medium">Drop PDF files here...</p>
        ) : (
          <div>
            <p className={`text-lg mb-2 font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
              Drag & drop PDF files here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supports multiple files up to 500MB each
            </p>
          </div>
        )}
      </div>

      {progress.length > 0 && (
        <div className="space-y-2">
          {progress.map((p, idx) => (
            <div
              key={idx}
              className={`flex items-center justify-between p-3 rounded-lg ${
                darkMode ? 'bg-gray-800' : 'bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-3">
                <File className={`h-5 w-5 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`} />
                <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-900'}`}>
                  {p.name}
                </span>
              </div>
              <div>
                {p.status === 'uploading' && (
                  <Loader className="h-5 w-5 text-purple-500 animate-spin" />
                )}
                {p.status === 'success' && (
                  <span className="text-green-500 text-sm font-medium">✓ Uploaded</span>
                )}
                {p.status === 'error' && (
                  <span className="text-red-500 text-sm font-medium">✗ Failed</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
