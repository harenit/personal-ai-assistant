import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Cpu, Database, ShieldCheck, CheckCircle2, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

export function Settings() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    setLoading(true);
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (e) {
      console.error('Health check error:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <SettingsIcon className="w-6 h-6 text-cyan-400" />
            System Configuration & Diagnostics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Status of local Ollama LLM provider, database connections, and security allowlists.
          </p>
        </div>

        <button
          onClick={checkHealth}
          disabled={loading}
          className="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-check System</span>
        </button>
      </div>

      {/* Diagnostics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* LLM & Model */}
        <div className="p-6 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Local LLM Architecture</h3>
            </div>
            <StatusBadge status={health?.ollama === 'ok' ? 'ONLINE' : 'OFFLINE'} size="xs" />
          </div>

          <div className="space-y-2.5 text-xs font-mono text-slate-300">
            <div className="flex justify-between py-1.5 border-b border-slate-800/80">
              <span className="text-slate-500">Provider:</span>
              <span className="font-bold text-cyan-400">Ollama (Local)</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800/80">
              <span className="text-slate-500">Endpoint:</span>
              <span>http://localhost:11434</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800/80">
              <span className="text-slate-500">Active Model:</span>
              <span className="text-emerald-400 font-bold">{health?.configured_model || 'llama3.1:8b'}</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Embedding Model:</span>
              <span>nomic-embed-text:latest</span>
            </div>
          </div>
        </div>

        {/* Database & Storage */}
        <div className="p-6 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Database & Persistence</h3>
            </div>
            <StatusBadge status="CONNECTED" size="xs" />
          </div>

          <div className="space-y-2.5 text-xs font-mono text-slate-300">
            <div className="flex justify-between py-1.5 border-b border-slate-800/80">
              <span className="text-slate-500">Engine:</span>
              <span className="font-bold text-indigo-400">SQLite 3 + SQLAlchemy</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800/80">
              <span className="text-slate-500">Path:</span>
              <span className="truncate max-w-[200px]">data/jarvis.db</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800/80">
              <span className="text-slate-500">Vector Store:</span>
              <span>Local Cosine / Embeddings</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Demo Environment:</span>
              <span className="text-cyan-400 font-bold">Active (DEMO_MODE=true)</span>
            </div>
          </div>
        </div>

        {/* Security & Tool Policies */}
        <div className="p-6 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-4 shadow-xl col-span-full">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Security & Permission Policies</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-300">
            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2">
              <h4 className="font-mono text-cyan-400 font-bold uppercase text-[11px]">
                Low-Risk Automated Tools
              </h4>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Can execute automatically: Read LMS assignments, announcements, exams, summarize documents, generate quizzes, flashcards, PowerPoint slides, local reminders, open allowlisted applications and educational URLs.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2">
              <h4 className="font-mono text-amber-400 font-bold uppercase text-[11px]">
                Sensitive Actions (Gated)
              </h4>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Require explicit student approval via pop-up dialog: Sending external emails, submitting official LMS assignments, modifying calendar commitments, or deleting documents.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
