import React, { useState, useEffect } from 'react';
import { Bell, AlertTriangle, User, Clock } from 'lucide-react';
import { api } from '../services/api';

export function Announcements() {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getAnnouncements();
        setAnnouncements(data || []);
      } catch (e) {
        console.error('Announcements load error:', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
          <Bell className="w-6 h-6 text-sky-400" />
          Course Bulletins & Announcements
        </h1>
        <p className="text-xs text-slate-400 mt-1">Official communications from faculty, professors, and campus administration.</p>
      </div>

      <div className="space-y-4">
        {announcements.map((item) => (
          <div
            key={item.id}
            className={`p-6 rounded-2xl bg-[#0D121D] border transition space-y-3 ${
              item.is_urgent ? 'border-amber-500/40 bg-amber-950/10' : 'border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {item.course_code}
                </span>
                {item.is_urgent && (
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-400 px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/40 animate-pulse">
                    <AlertTriangle className="w-3 h-3" />
                    URGENT
                  </span>
                )}
                <h3 className="text-base font-bold text-white">{item.title}</h3>
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
                <span className="flex items-center gap-1">
                  <User className="w-3.5 h-3.5 text-cyan-400" />
                  {item.author}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {item.created_at}
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/40 p-4 rounded-xl border border-slate-800/60 whitespace-pre-wrap">
              {item.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
