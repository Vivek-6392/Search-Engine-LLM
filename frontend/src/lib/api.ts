// Helper functions for API calls

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  const token = getAuthToken();
  const isFormData = options.body instanceof FormData;
  
  const headers: any = {
    ...options.headers,
    'Authorization': token ? `Bearer ${token}` : '',
  };

  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  } else if (headers['Content-Type']) {
    delete headers['Content-Type']; // Let browser set multipart with boundary
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    throw new Error('API request failed');
  }

  return response.json();
};

export const fetchConversations = () => fetchWithAuth('/conversations');
export const getConversation = (id: string) => fetchWithAuth(`/conversations/${id}`);
export const deleteConversation = (id: string) => fetchWithAuth(`/conversations/${id}`, { method: 'DELETE' });
export const fetchDocuments = () => fetchWithAuth('/documents');
export const deleteDocument = (id: string) => fetchWithAuth(`/documents/${id}`, { method: 'DELETE' });

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return fetchWithAuth('/documents/upload', {
    method: 'POST',
    body: formData,
  });
};

export const streamChat = async (query: string, conversationId?: string, onEvent?: (data: any) => void) => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify({
      query,
      conversation_id: conversationId,
      stream: true
    })
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  if (!response.body) throw new Error('No readable stream');

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split('\n\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') break;
        try {
          const parsed = JSON.parse(data);
          if (onEvent) onEvent(parsed);
        } catch (e) {
          console.error("Error parsing stream data:", e);
        }
      }
    }
  }
};
