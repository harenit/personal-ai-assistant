import React, { useState, useEffect } from 'react';
import { Mail, Search, Send, Clock, User, Reply, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

export function Email({ onAskJarvis }) {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [replyText, setReplyText] = useState('');
  const [isDrafting, setIsDrafting] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEmails();
  }, []);

  const loadEmails = async () => {
    try {
      const data = await api.getEmails();
      setEmails(data || []);
      if (data && data.length > 0 && !selectedEmail) {
        handleSelectEmail(data[0].id);
      }
    } catch (e) {
      console.error('Error loading emails:', e);
    }
  };

  const handleSelectEmail = async (id) => {
    try {
      const full = await api.readEmail(id);
      setSelectedEmail(full);
      setIsDrafting(false);
      setReplyText('');
    } catch (e) {
      console.error('Error reading email:', e);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      return loadEmails();
    }
    setLoading(true);
    try {
      const results = await api.searchEmails(searchQuery.trim());
      setEmails(results || []);
    } catch (e) {
      alert(`Search error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSendDraft = async () => {
    if (!replyText.trim() || !selectedEmail) return;
    try {
      await api.sendEmail(
        selectedEmail.sender,
        `Re: ${selectedEmail.subject}`,
        replyText.trim()
      );
      alert('Email sent successfully!');
      setIsDrafting(false);
      setReplyText('');
      await loadEmails();
    } catch (e) {
      alert(`Send error: ${e.message}`);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <Mail className="w-6 h-6 text-sky-400" />
            University Academic Email
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Communication channel with professors, TAs, and academic advising.
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search professor or topic..."
              className="pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition"
          >
            Search
          </button>
        </form>
      </div>

      {/* Email Inbox Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Email List */}
        <div className="p-4 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-2 max-h-[650px] overflow-y-auto">
          {emails.map((m) => {
            const isSelected = selectedEmail?.id === m.id;
            return (
              <div
                key={m.id}
                onClick={() => handleSelectEmail(m.id)}
                className={`p-4 rounded-2xl border cursor-pointer transition space-y-1.5 ${
                  isSelected
                    ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-200'
                    : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-900 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white truncate max-w-[150px]">{m.sender_name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">{m.received_at}</span>
                </div>
                <h4 className="text-xs font-semibold truncate text-slate-200">{m.subject}</h4>
                <p className="text-[11px] text-slate-400 line-clamp-2">{m.snippet}</p>
              </div>
            );
          })}
        </div>

        {/* Selected Email View */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-[#0D121D] border border-slate-800 flex flex-col justify-between space-y-6">
          {selectedEmail ? (
            <>
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-3 pb-4 border-b border-slate-800">
                  <div className="space-y-1">
                    <h3 className="text-base font-bold text-white">{selectedEmail.subject}</h3>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <span className="text-cyan-400 font-semibold">{selectedEmail.sender_name}</span>
                      <span>&lt;{selectedEmail.sender}&gt;</span>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-slate-500">{selectedEmail.received_at}</span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-200 leading-relaxed whitespace-pre-wrap min-h-[200px]">
                  {selectedEmail.body}
                </div>
              </div>

              {/* Reply Section */}
              <div className="space-y-3 pt-3 border-t border-slate-800">
                {!isDrafting ? (
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setIsDrafting(true)}
                      className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-white flex items-center gap-2 transition"
                    >
                      <Reply className="w-3.5 h-3.5" />
                      <span>Compose Reply</span>
                    </button>
                    <button
                      onClick={() => onAskJarvis(`Draft a polite academic reply to email "${selectedEmail.subject}" from ${selectedEmail.sender_name}`)}
                      className="px-4 py-2 rounded-xl bg-cyan-950/80 hover:bg-cyan-900/80 border border-cyan-800/60 text-xs font-bold text-cyan-300 flex items-center gap-2 transition"
                    >
                      <span>Draft with JARVIS</span>
                    </button>
                  </div>
                ) : (
                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400 font-semibold">Replying to: {selectedEmail.sender}</span>
                      <StatusBadge status="SENSITIVE" size="xs" />
                    </div>
                    <textarea
                      rows={4}
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Write your email response here..."
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                    />
                    <div className="flex items-center justify-between">
                      <button
                        onClick={() => setIsDrafting(false)}
                        className="text-xs text-slate-400 hover:text-slate-200"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSendDraft}
                        className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 text-black font-bold text-xs flex items-center gap-2 shadow-lg shadow-cyan-500/20"
                      >
                        <Send className="w-3.5 h-3.5" />
                        <span>Send Email</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="py-24 text-center text-xs text-slate-500">
              Select an email from the list to view its contents.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
