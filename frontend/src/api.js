import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Documents API
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getDocuments = async (skip = 0, limit = 100) => {
  const response = await api.get('/documents', {
    params: { skip, limit },
  });
  return response.data;
};

export const getDocument = async (docId) => {
  const response = await api.get(`/documents/${docId}`);
  return response.data;
};

export const deleteDocument = async (docId) => {
  const response = await api.delete(`/documents/${docId}`);
  return response.data;
};

// Query API
export const queryDocument = async (question, docId = null, conversationId = null, apiSettings = null) => {
  const payload = {
    question,
    doc_id: docId,
    conversation_id: conversationId,
    stream: false,
  };

  // Add custom API settings if provided
  if (apiSettings) {
    if (apiSettings.apiBaseUrl) payload.api_base_url = apiSettings.apiBaseUrl;
    if (apiSettings.apiKey) payload.api_key = apiSettings.apiKey;
    if (apiSettings.model) payload.model = apiSettings.model;
  }

  const response = await api.post('/query', payload);
  return response.data;
};

// Conversations API
export const createConversation = async (title, docId = null) => {
  const response = await api.post('/conversations', {
    title,
    doc_id: docId,
  });
  return response.data;
};

export const getConversation = async (conversationId) => {
  const response = await api.get(`/conversations/${conversationId}`);
  return response.data;
};

// System API
export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const reindexDocuments = async (docId = null) => {
  const response = await api.post('/reindex', {
    doc_id: docId,
  });
  return response.data;
};

export default api;
