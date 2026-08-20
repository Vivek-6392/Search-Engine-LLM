"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Send, Bot, Loader2, Library, LayoutTemplate, LogOut, Upload, FileText, Plus, File as FileIcon, Trash2, MessageSquare } from "lucide-react";
import { streamChat, getAuthToken, fetchConversations, getConversation, uploadDocument, fetchDocuments, deleteDocument, deleteConversation } from "@/lib/api";
import { AgentProgress } from "@/types";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MessageContent = ({ content }: { content: string }) => {
  const sourceMatch = content.match(/\*\*Sources\*\*|### Sources|Sources:/i);
  
  if (sourceMatch && sourceMatch.index !== undefined) {
    const mainContent = content.substring(0, sourceMatch.index).trim();
    const sourcesContent = content.substring(sourceMatch.index + sourceMatch[0].length).trim();
    
    return (
      <div className="space-y-4">
        <div className="prose prose-sm prose-invert max-w-none text-gray-200">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{mainContent}</ReactMarkdown>
        </div>
        <details className="group border border-gray-700/50 rounded-lg bg-[#161b22]/50 overflow-hidden mt-4">
          <summary className="cursor-pointer px-4 py-2.5 hover:bg-gray-800/80 text-xs font-medium text-gray-400 select-none flex items-center justify-between transition-colors">
            View Sources
            <span className="text-gray-500 group-open:rotate-180 transition-transform duration-200">▼</span>
          </summary>
          <div className="p-4 text-xs text-gray-400 border-t border-gray-700/50 prose prose-sm prose-invert max-w-none break-words">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{sourcesContent}</ReactMarkdown>
          </div>
        </details>
      </div>
    );
  }
  
  return (
    <div className="prose prose-sm prose-invert max-w-none text-gray-200">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
};

export default function Home() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string; sources?: any[] }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentProgress, setCurrentProgress] = useState<string>("");
  const [progressNodes, setProgressNodes] = useState<string[]>([]);
  const [conversations, setConversations] = useState<{ id: string; title: string }[]>([]);
  const [documents, setDocuments] = useState<{ id: string; filename: string; status: string }[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();
  const [isUploading, setIsUploading] = useState(false);
  
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auth guard and initial data fetch
  useEffect(() => {
    if (!getAuthToken()) {
      router.replace("/login");
    } else {
      loadConversations();
      loadDocuments();
    }
  }, [router]);

  const loadDocuments = async () => {
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  };

  const loadConversations = async () => {
    try {
      const data = await fetchConversations();
      setConversations(data);
    } catch (err) {
      console.error("Failed to fetch conversations", err);
    }
  };

  const handleSelectConversation = async (id: string) => {
    try {
      setCurrentConversationId(id);
      const conv = await getConversation(id);
      setMessages(conv.messages.map((m: any) => ({ role: m.role, content: m.content })));
    } catch (err) {
      console.error("Failed to load conversation", err);
    }
  };

  const handleNewConversation = () => {
    setCurrentConversationId(undefined);
    setMessages([]);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      setIsUploading(true);
      await uploadDocument(file);
      alert("Document uploaded successfully! It is now being processed in the background.");
      loadDocuments(); // Refresh documents list
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to upload document.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDeleteDocument = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this document?")) return;
    try {
      await deleteDocument(id);
      loadDocuments();
    } catch (err) {
      console.error("Failed to delete document", err);
      alert("Failed to delete document.");
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation?")) return;
    try {
      await deleteConversation(id);
      if (currentConversationId === id) {
        handleNewConversation();
      }
      loadConversations();
    } catch (err) {
      console.error("Failed to delete conversation", err);
      alert("Failed to delete conversation.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.replace("/login");
  };

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentProgress]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMessage = query.trim();
    setQuery("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);
    setProgressNodes([]);
    setCurrentProgress("Initializing DeepSearch agents...");

    let finalAnswer = "";
    let citations = [];

    try {
      await streamChat(userMessage, currentConversationId, (data: AgentProgress) => {
        if (data.event === "node_update" && data.node) {
          setProgressNodes((prev) => [...prev, data.node!]);
          setCurrentProgress(`Agent active: ${data.node}`);
        } else if (data.event === "final_answer") {
          finalAnswer = data.content;
        } else if (data.event === "critique") {
          setCurrentProgress(`Critic checking: ${data.content.approved ? 'Approved' : 'Needs revision'}`);
        } else if (data.event === "conversation_created") {
          setCurrentConversationId(data.conversation_id);
        }
      });
      
      setMessages((prev) => [...prev, { role: "assistant", content: finalAnswer }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error while processing your request." }]);
    } finally {
      setIsLoading(false);
      setCurrentProgress("");
      loadConversations(); // Refresh list to get potentially new conversation title
    }
  };

  return (
    <div className="flex h-screen bg-[#0f1115] text-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-[#161b22] border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800 flex items-center justify-between text-indigo-400 font-semibold text-lg">
          <div className="flex items-center gap-2">
            <Library className="w-5 h-5" />
            DeepSearch AI
          </div>
          <button onClick={handleNewConversation} className="p-1.5 hover:bg-gray-800 rounded text-gray-400 hover:text-white transition-colors" title="New Chat">
            <Plus className="w-4 h-4" />
          </button>
        </div>
        <div className="p-4 flex-1 overflow-y-auto space-y-1">
          <p className="text-xs text-gray-500 font-semibold mb-3 uppercase tracking-wider">Recent Research</p>
          {conversations.length === 0 ? (
             <div className="text-xs text-gray-600 italic">No conversations yet</div>
          ) : (
             conversations.map(conv => (
                 <div 
                  key={conv.id} 
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`text-sm py-2 px-3 rounded cursor-pointer transition-colors group flex items-center justify-between ${currentConversationId === conv.id ? 'bg-indigo-500/10 text-indigo-300' : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'}`}
                >
                  <div className="flex items-center gap-2 truncate pr-2">
                    <MessageSquare className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="truncate">{conv.title || "New Conversation"}</span>
                  </div>
                  <button 
                    onClick={(e) => handleDeleteConversation(conv.id, e)} 
                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 hover:bg-gray-700 rounded transition-all flex-shrink-0" 
                    title="Delete Conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
             ))
          )}
        </div>
        <div className="p-4 border-t border-gray-800 flex flex-col gap-2">
          <p className="text-xs text-gray-500 font-semibold mb-1 uppercase tracking-wider">Uploaded Documents</p>
          <div className="max-h-32 overflow-y-auto mb-2 space-y-1">
            {documents.length === 0 ? (
              <div className="text-xs text-gray-600 italic">No documents uploaded</div>
            ) : (
              documents.map(doc => (
                <div key={doc.id} className="text-xs py-1.5 px-2 hover:bg-gray-800 rounded flex items-center justify-between group">
                  <div className="flex items-center gap-1.5 truncate text-gray-400">
                    <FileIcon className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="truncate">{doc.filename}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`flex-shrink-0 text-[10px] px-1.5 py-0.5 rounded ${
                      doc.status === 'indexed' ? 'bg-green-500/20 text-green-400' : 
                      doc.status === 'failed' ? 'bg-red-500/20 text-red-400' : 
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {doc.status}
                    </span>
                    <button onClick={(e) => handleDeleteDocument(doc.id, e)} className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 hover:bg-gray-700 rounded transition-all" title="Delete Document">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <input 
             type="file" 
             ref={fileInputRef} 
             onChange={handleFileUpload} 
             className="hidden" 
             accept=".txt,.pdf,.csv" 
          />
          <button 
             onClick={() => fileInputRef.current?.click()}
             disabled={isUploading}
             className="w-full text-sm text-gray-400 flex items-center justify-center gap-2 hover:text-gray-200 hover:bg-gray-800 py-2 rounded-lg transition-colors border border-gray-700 hover:border-gray-600 disabled:opacity-50 mt-2"
          >
            {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            {isUploading ? "Uploading..." : "Upload Document"}
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative overflow-hidden">
        {/* Header */}
        <header className="h-14 border-b border-gray-800 flex items-center justify-between px-6 bg-[#0f1115]/80 backdrop-blur-sm z-10">
          <div className="font-medium text-gray-200">Multi-Agent Engine</div>
          <div className="flex items-center gap-3">
            <div className="text-xs px-2 py-1 bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/20">
              v0.1.0-alpha
            </div>
            <button onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors px-2 py-1 rounded-lg hover:bg-gray-800">
              <LogOut className="w-3.5 h-3.5" />
              Logout
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto space-y-6">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <Library className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-gray-500">
                What would you like to research?
              </h1>
              <p className="text-gray-400">
                DeepSearch utilizes a multi-agent LangGraph workflow to plan, retrieve, verify, and synthesize complex answers.
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-4 max-w-4xl mx-auto ${msg.role === 'user' ? 'justify-end' : ''}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-indigo-600/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
                    <Bot className="w-5 h-5 text-indigo-400" />
                  </div>
                )}
                <div className={`px-5 py-3.5 rounded-2xl max-w-[85%] leading-relaxed ${
                  msg.role === 'user' 
                    ? 'bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-900/20' 
                    : 'bg-[#1c2128] border border-gray-800 rounded-bl-none'
                }`}>
                  {msg.role === 'assistant' ? (
                    <MessageContent content={msg.content} />
                  ) : (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {/* Progress Indicator */}
          {isLoading && (
            <div className="flex gap-4 max-w-4xl mx-auto">
              <div className="w-8 h-8 rounded-full bg-indigo-600/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
                <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
              </div>
              <div className="px-5 py-4 rounded-2xl bg-[#1c2128] border border-gray-800 rounded-bl-none text-sm text-gray-400 min-w-[300px]">
                <div className="flex items-center gap-2 mb-2 font-medium text-gray-300">
                  {currentProgress}
                </div>
                <div className="flex flex-wrap gap-2">
                  {progressNodes.map((node, i) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-800 border border-gray-700 rounded text-xs">
                      {node}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-[#0f1115] border-t border-gray-800">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={handleSubmit} className="relative flex items-end shadow-xl rounded-2xl bg-[#161b22] border border-gray-700 focus-within:border-indigo-500 transition-colors">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Ask a complex research question..."
                className="w-full bg-transparent text-gray-100 placeholder-gray-500 p-4 min-h-[60px] max-h-[200px] resize-none outline-none"
                rows={1}
              />
              <button 
                type="submit" 
                disabled={!query.trim() || isLoading}
                className="p-3 m-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
            <div className="text-center mt-2 text-xs text-gray-600">
              DeepSearch AI can make mistakes. Verify important information.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
