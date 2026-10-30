import React, { useState, useEffect } from 'react';
import { CheckSquare, Plus, Clock, Trash2, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export function Reminders() {
  const [reminders, setReminders] = useState([]);
  const [title, setTitle] = useState('');
  const [dueDateTime, setDueDateTime] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadReminders();
  }, []);

  const loadReminders = async () => {
    try {
      const data = await api.getReminders(true);
      setReminders(data || []);
    } catch (e) {
      console.error('Error loading reminders:', e);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim() || !dueDateTime.trim()) return;

    setLoading(true);
    try {
      await api.createReminder({
        title: title.trim(),
        due_datetime: dueDateTime.trim(),
        description: description.trim()
      });
      setTitle('');
      setDueDateTime('');
      setDescription('');
      await loadReminders();
    } catch (err) {
      alert(`Error creating reminder: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteReminder(id);
      await loadReminders();
    } catch (err) {
      alert(`Error deleting reminder: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
          <CheckSquare className="w-6 h-6 text-cyan-400" />
          Study Reminders & Task Alerts
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Persistent SQLite scheduled alerts monitored automatically by JARVIS background scheduler.
        </p>
      </div>

      {/* Create Reminder Card */}
      <div className="p-6 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-4 shadow-xl">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Plus className="w-4 h-4 text-cyan-400" />
          Set New Reminder
        </h2>

        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Reminder Task</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Study AI Midterm Backpropagation, Finish Lab 3"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Due Date / Time</label>
              <input
                type="text"
                value={dueDateTime}
                onChange={(e) => setDueDateTime(e.target.value)}
                placeholder="e.g. tomorrow at 7 PM, 2026-09-29 19:00"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                required
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-400 font-semibold">Notes (Optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Review lecture slides 4 and 5 before starting"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading || !title.trim() || !dueDateTime.trim()}
              className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs shadow-md shadow-cyan-500/20 disabled:opacity-50 transition"
            >
              Add Reminder
            </button>
          </div>
        </form>
      </div>

      {/* Reminders List */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-white">Active Alerts ({reminders.length})</h3>

        <div className="space-y-2.5">
          {reminders.map((r) => (
            <div
              key={r.id}
              className={`p-4 rounded-2xl border transition flex items-center justify-between ${
                r.is_completed
                  ? 'bg-slate-950/40 border-slate-800/50 opacity-60'
                  : 'bg-[#0D121D] border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className={`text-xs font-bold ${r.is_completed ? 'line-through text-slate-400' : 'text-white'}`}>
                    {r.title}
                  </h4>
                  {r.is_completed && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40">
                      TRIGGERED
                    </span>
                  )}
                </div>
                {r.description && <p className="text-[11px] text-slate-400">{r.description}</p>}
                <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono">
                  <Clock className="w-3 h-3 text-cyan-400" />
                  <span>Scheduled for: {r.due}</span>
                </div>
              </div>

              <button
                onClick={() => handleDelete(r.id)}
                className="p-2 rounded-xl hover:bg-slate-800 text-slate-500 hover:text-rose-400 transition"
                title="Delete reminder"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}

          {reminders.length === 0 && (
            <div className="py-8 text-center text-xs text-slate-500">
              No reminders set.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
