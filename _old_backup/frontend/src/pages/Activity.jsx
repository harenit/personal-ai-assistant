import React, { useState, useEffect } from 'react';
import { Activity as ActivityIcon, ShieldCheck, Clock, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

export function Activity() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getActivityLogs(60);
      setLogs(data || []);
    } catch (e) {
      console.error('Activity logs error:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <ActivityIcon className="w-6 h-6 text-cyan-400" />
            Security & Agent Audit Trail
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Complete, immutable log of all autonomous tool selections, system actions, and permission decisions.
          </p>
        </div>

        <button
          onClick={loadLogs}
          disabled={loading}
          className="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit</span>
        </button>
      </div>

      {/* Activity Table */}
      <div className="rounded-3xl bg-[#0D121D] border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-[11px] font-mono uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-3.5">Timestamp</th>
                <th className="px-6 py-3.5">Event Type</th>
                <th className="px-6 py-3.5">Tool / Action</th>
                <th className="px-6 py-3.5">Activity Details</th>
                <th className="px-6 py-3.5">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-900/40 transition">
                  <td className="px-6 py-3.5 text-slate-400 whitespace-nowrap">
                    {log.timestamp}
                  </td>
                  <td className="px-6 py-3.5">
                    <span className="font-semibold text-cyan-400">
                      {log.event_type}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 text-slate-300 font-bold">
                    {log.tool_name || '—'}
                  </td>
                  <td className="px-6 py-3.5 text-slate-300 max-w-md font-sans">
                    {log.details}
                  </td>
                  <td className="px-6 py-3.5 whitespace-nowrap">
                    <StatusBadge status={log.status} size="xs" />
                  </td>
                </tr>
              ))}

              {logs.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500 font-sans">
                    No activity logs recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
