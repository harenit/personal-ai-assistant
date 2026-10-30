import React, { useState, useEffect } from 'react';
import { BookOpen, CheckCircle, Clock, Send, Upload, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

export function Assignments({ onAskJarvis }) {
  const [assignments, setAssignments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('all');
  const [submittingId, setSubmittingId] = useState(null);
  const [submissionText, setSubmissionText] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [aData, cData] = await Promise.all([
          api.getAssignments(),
          api.getCourses()
        ]);
        setAssignments(aData || []);
        setCourses(cData || []);
      } catch (e) {
        console.error('Assignments load error:', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filtered = selectedCourse === 'all'
    ? assignments
    : assignments.filter(a => a.course_code === selectedCourse);

  const handleSubmit = async (assignmentId) => {
    if (!submissionText.trim()) return;
    try {
      // Calls submission via agent or direct API (both are protected)
      await api.submitAssignment(assignmentId, submissionText.trim());
      alert('Assignment submitted successfully!');
      setSubmittingId(null);
      setSubmissionText('');
      const updated = await api.getAssignments();
      setAssignments(updated);
    } catch (e) {
      alert(`Submission error: ${e.message}`);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Title & Filter */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-cyan-400" />
            LMS Academic Assignments
          </h1>
          <p className="text-xs text-slate-400 mt-1">Official Canvas/Blackboard synced course tasks and deadlines.</p>
        </div>

        {/* Filter Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">Course:</span>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-semibold text-slate-200 focus:outline-none"
          >
            <option value="all">All Enrolled Courses</option>
            {courses.map(c => (
              <option key={c.id} value={c.code}>{c.code} — {c.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Assignment Cards Grid */}
      <div className="space-y-4">
        {filtered.map((item) => {
          const isPending = item.status === 'pending';
          const isSubmitting = submittingId === item.id;

          return (
            <div
              key={item.id}
              className="p-6 rounded-2xl bg-[#0D121D] border border-slate-800 hover:border-slate-700 transition space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                      {item.course_code}
                    </span>
                    <span className="text-xs text-slate-400">• {item.course_name}</span>
                  </div>
                  <h3 className="text-base font-bold text-white">{item.title}</h3>
                </div>

                <div className="flex items-center gap-3">
                  <StatusBadge status={item.status} />
                  <span className="text-xs font-mono font-semibold text-slate-300">
                    {item.points} pts
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{item.description}</p>

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/60 text-xs">
                <div className="flex items-center gap-1.5 text-slate-400 font-mono">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  <span>Due: <strong className="text-slate-200">{item.due_date}</strong></span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onAskJarvis(`Help me complete the assignment: ${item.title}`)}
                    className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 font-semibold text-xs flex items-center gap-1.5 transition"
                  >
                    <Sparkles className="w-3 h-3 text-cyan-400" />
                    <span>Get Help from JARVIS</span>
                  </button>

                  {isPending && (
                    <button
                      onClick={() => setSubmittingId(isSubmitting ? null : item.id)}
                      className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-black font-bold text-xs flex items-center gap-1.5 transition"
                    >
                      <Upload className="w-3 h-3" />
                      <span>{isSubmitting ? 'Cancel' : 'Submit Work'}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* In-place submission form */}
              {isSubmitting && (
                <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 space-y-3 animate-in fade-in">
                  <div className="flex items-center justify-between text-xs text-amber-400 font-semibold">
                    <span>Sensitive Action: Official LMS Submission</span>
                    <StatusBadge status="SENSITIVE" size="xs" />
                  </div>
                  <textarea
                    rows={3}
                    value={submissionText}
                    onChange={(e) => setSubmissionText(e.target.value)}
                    placeholder="Enter submission text, code repo URL, or project notes..."
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                  />
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => handleSubmit(item.id)}
                      className="px-4 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs transition"
                    >
                      Confirm Submission
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
