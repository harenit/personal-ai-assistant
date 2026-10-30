import React, { useState, useEffect } from 'react';
import { 
  BookOpen, GraduationCap, Bell, CheckSquare, Sparkles, 
  ArrowUpRight, Clock, AlertCircle, Laptop, ExternalLink 
} from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { ArcReactorHUD } from '../components/ArcReactorHUD';

export function Dashboard({ onNavigateToTab, onQuickAsk, voice }) {
  const [assignments, setAssignments] = useState([]);
  const [exams, setExams] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [telemetry, setTelemetry] = useState({ cpu_percent: 43, ram_percent: 71, disk_percent: 64 });
  const [loading, setLoading] = useState(true);
  const [quickInput, setQuickInput] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const [aData, eData, anData, rData, tData] = await Promise.all([
          api.getUpcomingAssignments(7).catch(() => []),
          api.getExams().catch(() => []),
          api.getAnnouncements().catch(() => []),
          api.getReminders().catch(() => []),
          api.getTelemetry().catch(() => ({ cpu_percent: 43, ram_percent: 71, disk_percent: 64 }))
        ]);
        setAssignments(aData || []);
        setExams(eData || []);
        setAnnouncements(anData || []);
        setReminders(rData || []);
        if (tData) setTelemetry(tData);
      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
    const interval = setInterval(async () => {
      try {
        const t = await api.getTelemetry();
        if (t) setTelemetry(t);
      } catch {}
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleQuickSubmit = (e) => {
    e.preventDefault();
    if (!quickInput.trim()) return;
    onQuickAsk(quickInput.trim());
  };

  const handleLaunchApp = async (appName) => {
    try {
      await api.openApp(appName);
    } catch (e) {
      alert(`Could not launch ${appName}: ${e.message}`);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* ================= HERO: SCI-FI ARC REACTOR HUD ================= */}
      <ArcReactorHUD
        state={voice?.isListening ? 'listening' : voice?.isSpeaking ? 'speaking' : 'idle'}
        transcript={voice?.transcript}
        telemetry={telemetry}
        isListening={voice?.isListening}
        isSpeaking={voice?.isSpeaking}
        onToggleVoice={() => {
          if (voice?.isListening) voice.stopListening();
          else voice.startListening();
        }}
        onExecuteCommand={(cmd) => onQuickAsk(cmd)}
        onExpandPanel={() => onNavigateToTab('chat')}
      />
      {/* Welcome Banner */}
      <div className="relative overflow-hidden p-8 rounded-3xl bg-gradient-to-r from-sky-950/60 via-slate-900 to-indigo-950/40 border border-cyan-500/20 shadow-2xl">
        <div className="relative z-10 space-y-4 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-xs font-mono text-cyan-300">
            <Sparkles className="w-3.5 h-3.5" />
            JARVIS Academic Assistant Active
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
            Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-300">Alex</span>
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            You have an AI Midterm tomorrow at 10:00 AM in Hall 304 and 2 pending assignments due within 48 hours. Let JARVIS prepare your revision plan or draft professor communications.
          </p>

          {/* Quick Command Bar */}
          <form onSubmit={handleQuickSubmit} className="flex items-center gap-2 pt-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={quickInput}
                onChange={(e) => setQuickInput(e.target.value)}
                placeholder="Ask JARVIS anything (e.g. 'Prepare me for tomorrow's AI exam' or 'Check my deadlines')..."
                className="w-full px-4 py-3 rounded-2xl bg-black/60 border border-slate-700/80 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition"
              />
            </div>
            <button
              type="submit"
              className="px-5 py-3 rounded-2xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-black font-bold text-sm shadow-lg shadow-cyan-500/20 transition shrink-0"
            >
              Ask JARVIS
            </button>
          </form>
        </div>
      </div>

      {/* Quick System Tools Bar */}
      <div className="p-4 rounded-2xl bg-[#0D121D] border border-slate-800 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <Laptop className="w-4 h-4 text-cyan-400" />
          <span>Real Windows System Actions:</span>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => handleLaunchApp('calculator')}
            className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition flex items-center gap-1.5"
          >
            <span>Open Calculator</span>
            <ExternalLink className="w-3 h-3 text-cyan-400" />
          </button>
          <button
            onClick={() => handleLaunchApp('notepad')}
            className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition flex items-center gap-1.5"
          >
            <span>Open Notepad</span>
            <ExternalLink className="w-3 h-3 text-cyan-400" />
          </button>
          <button
            onClick={() => handleLaunchApp('explorer')}
            className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition flex items-center gap-1.5"
          >
            <span>File Explorer</span>
            <ExternalLink className="w-3 h-3 text-cyan-400" />
          </button>
          <button
            onClick={() => onQuickAsk('Create a 10-slide presentation about AI')}
            className="px-3 py-1.5 rounded-xl bg-cyan-950/80 hover:bg-cyan-900/80 border border-cyan-700/60 text-xs font-semibold text-cyan-300 transition flex items-center gap-1.5"
          >
            <Sparkles className="w-3 h-3" />
            <span>Generate AI Slides</span>
          </button>
        </div>
      </div>

      {/* Grid Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Urgent Deadlines */}
        <div className="p-6 rounded-2xl bg-[#0D121D] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Upcoming Assignments</h3>
            </div>
            <button
              onClick={() => onNavigateToTab('assignments')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              View all <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {assignments.slice(0, 3).map((a) => (
              <div key={a.id} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-bold text-slate-200 line-clamp-1">{a.title}</h4>
                  <StatusBadge status="PENDING" size="xs" />
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>{a.course_code}</span>
                  <span className="text-amber-400 font-semibold">{a.due_date}</span>
                </div>
              </div>
            ))}
            {assignments.length === 0 && (
              <p className="text-xs text-slate-500 py-4 text-center">No assignments due in the next 7 days.</p>
            )}
          </div>
        </div>

        {/* Exams & Tests */}
        <div className="p-6 rounded-2xl bg-[#0D121D] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white">Exam Schedule</h3>
            </div>
            <button
              onClick={() => onNavigateToTab('exams')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              View all <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {exams.slice(0, 2).map((e) => (
              <div key={e.id} className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-1.5">
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-bold text-amber-200">{e.title}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40 font-bold">
                    {e.course_code}
                  </span>
                </div>
                <div className="text-[11px] text-slate-300 flex items-center justify-between">
                  <span>{e.date} • {e.start_time}</span>
                  <span className="text-cyan-300">{e.room}</span>
                </div>
                <p className="text-[10px] text-slate-400 line-clamp-1">{e.topics}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Announcements */}
        <div className="p-6 rounded-2xl bg-[#0D121D] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-sky-400" />
              <h3 className="text-sm font-bold text-white">Course Announcements</h3>
            </div>
            <button
              onClick={() => onNavigateToTab('announcements')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              View all <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {announcements.slice(0, 2).map((an) => (
              <div key={an.id} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                    {an.course_code}
                  </span>
                  {an.is_urgent && (
                    <span className="text-[10px] text-rose-400 font-bold">URGENT</span>
                  )}
                </div>
                <h4 className="text-xs font-bold text-slate-200">{an.title}</h4>
                <p className="text-[11px] text-slate-400 line-clamp-2">{an.content}</p>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
