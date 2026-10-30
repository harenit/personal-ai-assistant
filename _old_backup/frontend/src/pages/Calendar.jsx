import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Clock, MapPin, Plus, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

export function Calendar() {
  const [events, setEvents] = useState([]);
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [location, setLocation] = useState('Campus');
  const [eventType, setEventType] = useState('study');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const data = await api.getCalendarEvents();
      setEvents(data || []);
    } catch (e) {
      console.error('Calendar load error:', e);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim() || !startTime.trim() || !endTime.trim()) return;

    setLoading(true);
    try {
      await api.createCalendarEvent({
        title: title.trim(),
        start_time: startTime.trim(),
        end_time: endTime.trim(),
        location,
        event_type: eventType
      });
      setTitle('');
      setStartTime('');
      setEndTime('');
      await loadEvents();
      alert('Calendar event scheduled successfully!');
    } catch (err) {
      alert(`Calendar error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id) => {
    try {
      await api.cancelCalendarEvent(id);
      await loadEvents();
    } catch (err) {
      alert(`Cancel error: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
          <CalendarIcon className="w-6 h-6 text-cyan-400" />
          Academic Schedule & Calendar
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Synchronized timetable containing lectures, exam sessions, and group study commitments.
        </p>
      </div>

      {/* Add Event Form */}
      <div className="p-6 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Plus className="w-4 h-4 text-cyan-400" />
            Schedule New Calendar Event
          </h2>
          <StatusBadge status="SENSITIVE" size="xs" />
        </div>

        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1.5 md:col-span-2">
              <label className="text-xs font-mono text-slate-400 font-semibold">Event Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. AI Group Study Session, Algorithms Office Hours"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Category</label>
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-400"
              >
                <option value="study">Study Session</option>
                <option value="class">Class / Lecture</option>
                <option value="exam">Exam / Quiz</option>
                <option value="personal">Personal Commitment</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Start Datetime</label>
              <input
                type="text"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                placeholder="YYYY-MM-DD HH:MM (e.g. 2026-09-29 14:00)"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">End Datetime</label>
              <input
                type="text"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                placeholder="YYYY-MM-DD HH:MM (e.g. 2026-09-29 16:00)"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Library Room 2B, Hall 304"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={loading || !title.trim()}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 text-black font-bold text-xs shadow-md shadow-cyan-500/20 disabled:opacity-50 transition"
            >
              Add to Calendar
            </button>
          </div>
        </form>
      </div>

      {/* Events List */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white">Scheduled Commitments ({events.length})</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {events.map((ev) => (
            <div
              key={ev.id}
              className="p-5 rounded-2xl bg-[#0D121D] border border-slate-800 hover:border-slate-700 transition space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-bold text-white">{ev.title}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-400 uppercase font-semibold">
                    {ev.event_type}
                  </span>
                </div>

                <div className="space-y-1 text-xs text-slate-400 font-mono">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{ev.start} - {ev.end}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-rose-400" />
                    <span>{ev.location}</span>
                  </div>
                </div>

                {ev.description && <p className="text-xs text-slate-300 pt-1">{ev.description}</p>}
              </div>

              <div className="flex justify-end pt-2 border-t border-slate-800">
                <button
                  onClick={() => handleCancel(ev.id)}
                  className="p-1.5 hover:text-rose-400 text-slate-500 transition"
                  title="Cancel event"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
