import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, Mic, MicOff, Paperclip, Sparkles, Volume2, 
  ExternalLink, FileText, CheckCircle2, XCircle, Clock, Presentation 
} from 'lucide-react';
import { api } from '../services/api';
import { ToolActivityTimeline } from '../components/ToolActivityTimeline';
import { PermissionModal } from '../components/PermissionModal';
import { VoiceWaveform } from '../components/VoiceWaveform';

const SUGGESTIONS = [
  "Check my LMS and email and tell me what I need to finish today.",
  "Prepare me for tomorrow's AI exam.",
  "Create a 10-slide presentation about AI.",
  "Do I have any assignments due this week?",
  "Draft an email to Prof. Martinez asking for an extension.",
  "Open Calculator."
];

export function Chat({
  initialMessage = '',
  isListening,
  isSpeaking,
  onToggleVoice,
  speakText,
  stopSpeaking,
  onOpenPermission
}) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      content: "Hello Alex. I am JARVIS, your permission-aware autonomous AI academic agent. I can check your LMS deadlines, search academic emails, prepare exam study guides, generate PowerPoint presentations, schedule reminders, and control authorized Windows applications. What would you like to accomplish today?",
      steps: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStepMessage, setCurrentStepMessage] = useState('');
  const [pendingPermission, setPendingPermission] = useState(null);
  const [activeAudioUrl, setActiveAudioUrl] = useState(null);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (initialMessage) {
      handleSendMessage(initialMessage);
    }
  }, [initialMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, currentStepMessage]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || inputValue;
    if (!query.trim() || isLoading) return;

    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      content: query.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);
    setCurrentStepMessage('JARVIS is analyzing request & planning actions...');

    try {
      const response = await api.sendMessage(query.trim(), null, true);

      if (response.status === 'waiting_for_permission' && response.permission_request) {
        setPendingPermission(response.permission_request);
      }

      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        content: response.final_response || (response.permission_request ? "Awaiting your authorization to proceed with this sensitive action." : "Task completed."),
        steps: response.steps || [],
        referenced_files: response.referenced_files || [],
        audio_url: response.audio_url,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMsg]);

      if (response.audio_url) {
        setActiveAudioUrl(response.audio_url);
      } else if (response.final_response) {
        speakText(response.final_response);
      }

    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          content: `JARVIS Error: ${err.message}`,
          steps: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
      setCurrentStepMessage('');
    }
  };

  const handleApprovePermission = async (reqId) => {
    setPendingPermission(null);
    setIsLoading(true);
    setCurrentStepMessage('Permission granted. Executing sensitive action...');

    try {
      const response = await api.approvePermission(reqId);
      const updateMsg = {
        id: Date.now().toString(),
        sender: 'assistant',
        content: response.final_response || "Authorized action executed successfully.",
        steps: response.steps || [],
        referenced_files: response.referenced_files || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, updateMsg]);
      if (response.final_response) {
        speakText(response.final_response);
      }
    } catch (err) {
      alert(`Approval error: ${err.message}`);
    } finally {
      setIsLoading(false);
      setCurrentStepMessage('');
    }
  };

  const handleDenyPermission = async (reqId) => {
    setPendingPermission(null);
    setIsLoading(true);
    setCurrentStepMessage('Permission denied by user. Halting execution...');

    try {
      const response = await api.denyPermission(reqId);
      const updateMsg = {
        id: Date.now().toString(),
        sender: 'assistant',
        content: response.final_response || "Action canceled per your instruction.",
        steps: response.steps || [],
        referenced_files: response.referenced_files || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, updateMsg]);
    } catch (err) {
      alert(`Denial error: ${err.message}`);
    } finally {
      setIsLoading(false);
      setCurrentStepMessage('');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsLoading(true);
    setCurrentStepMessage(`Uploading and indexing ${file.name} into RAG vector store...`);

    try {
      const res = await api.uploadDocument(formData);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: 'assistant',
          content: `Document **${res.title}** uploaded and indexed (${res.chunks_indexed} chunks). Summary:\n\n${res.summary}\n\nYou can now ask me questions or generate practice quizzes from this document!`,
          steps: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } catch (err) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setIsLoading(false);
      setCurrentStepMessage('');
    }
  };

  const handleOpenFile = async (filePath) => {
    try {
      await api.openPresentation(filePath);
    } catch (e) {
      alert(`Could not open file: ${e.message}`);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto px-4 py-6">
      
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div
              key={m.id}
              className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-sky-400 p-0.5 shrink-0 shadow-md shadow-cyan-500/20">
                  <div className="w-full h-full bg-slate-950 rounded-full flex items-center justify-center font-extrabold text-[10px] text-cyan-400 font-mono">
                    J
                  </div>
                </div>
              )}

              <div className={`max-w-2xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
                    isUser
                      ? 'bg-gradient-to-r from-cyan-600 to-sky-600 text-white rounded-tr-none font-medium'
                      : 'bg-[#121826] border border-slate-800 text-slate-100 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>

                  {/* Render Execution Timeline if available */}
                  {!isUser && m.steps && m.steps.length > 0 && (
                    <ToolActivityTimeline steps={m.steps} />
                  )}

                  {/* Referenced / Generated Files Card */}
                  {!isUser && m.referenced_files && m.referenced_files.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <span className="text-[11px] font-mono text-cyan-400 font-bold uppercase tracking-wider block">
                        Generated Artifacts
                      </span>
                      {m.referenced_files.map((file, fIdx) => (
                        <div key={fIdx} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/80 border border-cyan-500/30">
                          <div className="flex items-center gap-2">
                            <Presentation className="w-4 h-4 text-cyan-400" />
                            <span className="text-xs font-mono font-bold text-white">{file.name}</span>
                          </div>
                          <button
                            onClick={() => handleOpenFile(file.path)}
                            className="px-3 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-xs font-semibold flex items-center gap-1.5 transition"
                          >
                            <span>Open on Windows</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Audio Speech Button */}
                  {!isUser && (
                    <div className="flex items-center justify-between pt-2 mt-2 border-t border-slate-800/60 text-[10px] text-slate-400">
                      <span className="font-mono">{m.timestamp}</span>
                      <button
                        onClick={() => speakText(m.content)}
                        className="hover:text-cyan-400 flex items-center gap-1 transition"
                        title="Speak response"
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>Speak</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-white shrink-0">
                  AR
                </div>
              )}
            </div>
          );
        })}

        {/* Loading Step Bar */}
        {isLoading && (
          <div className="flex items-center gap-3 p-3.5 rounded-2xl bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-xs font-mono animate-pulse">
            <Sparkles className="w-4 h-4 animate-spin text-cyan-400" />
            <span>{currentStepMessage || 'Autonomous reasoning in progress...'}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts Pill Carousel */}
      {messages.length <= 2 && (
        <div className="py-2 flex items-center gap-2 overflow-x-auto text-xs no-scrollbar">
          {SUGGESTIONS.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(s)}
              className="px-3 py-1.5 rounded-full bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 whitespace-nowrap transition text-xs"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input Form Bar */}
      <div className="mt-3 pt-3 border-t border-slate-800/80">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2 p-1.5 rounded-2xl bg-[#121826] border border-slate-700/80 shadow-xl focus-within:border-cyan-400 focus-within:ring-1 focus-within:ring-cyan-400 transition"
        >
          {/* File Upload Button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.docx,.txt"
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            title="Upload PDF, DOCX or Notes"
            className="p-2.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          {/* Text Input */}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your academic or system request to JARVIS..."
            className="flex-1 bg-transparent px-2 py-2 text-sm text-white placeholder-slate-500 focus:outline-none"
            disabled={isLoading}
          />

          {/* Push to talk button in chat */}
          <button
            type="button"
            onClick={onToggleVoice}
            title={isListening ? "Listening... click to stop" : "Speak command"}
            className={`p-2.5 rounded-xl transition ${
              isListening
                ? 'bg-rose-500 text-white animate-pulse'
                : 'hover:bg-slate-800 text-slate-400 hover:text-cyan-400'
            }`}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          {/* Send Button */}
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-black font-bold disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-cyan-500/20 transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Permission Modal */}
      {pendingPermission && (
        <PermissionModal
          permissionRequest={pendingPermission}
          onApprove={handleApprovePermission}
          onDeny={handleDenyPermission}
        />
      )}
    </div>
  );
}
