export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: any;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  updated_at: string;
}

export interface Document {
  id: string;
  filename: string;
  status: string;
  created_at: string;
}

export interface Citation {
  id: string;
  content: string;
  source: string;
  title: string;
  url?: string;
  page?: number;
  score?: number;
  source_type: string;
}

export interface AgentProgress {
  event: 'node_update' | 'final_answer' | 'critique' | 'error' | 'conversation_created';
  node?: string;
  content?: string | any;
  conversation_id?: string;
}
