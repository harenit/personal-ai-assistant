import React, { useState, useEffect } from 'react';
import { GraduationCap, Calendar, MapPin, Sparkles, BookOpen, Clock } from 'lucide-react';
import { api } from '../services/api';

export function Exams({ onAskJarvis }) {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getExams();
        setExams(data || []);
      } catch (e) {
        console.error('Exams load error:', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
          <GraduationCap className="w-6 h-6 text-amber-400" />
          Examination & Midterm Schedule
        </h1>
        <p className="text-xs text-slate-400 mt-1">Official semester testing schedule, rooms, and syllabus outlines.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {exams.map((exam) => (
          <div
            key={exam.id}
            className="p-6 rounded-3xl bg-[#0D121D] border border-amber-500/20 hover:border-amber-500/40 transition space-y-4 shadow-xl shadow-amber-950/10"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40">
                  {exam.course_code}
                </span>
                <h3 className="text-lg font-bold text-white mt-1.5">{exam.title}</h3>
                <p className="text-xs text-slate-400">{exam.course_name}</p>
              </div>

              <div className="text-right">
                <span className="text-xs font-mono font-bold text-amber-400 block">
                  {exam.weight_percent}% Grade Weight
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 py-2 text-xs text-slate-300 font-mono">
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800">
                <Calendar className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>{exam.date}</span>
              </div>
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800">
                <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                <span>{exam.start_time} - {exam.end_time}</span>
              </div>
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 col-span-2">
                <MapPin className="w-4 h-4 text-rose-400 shrink-0" />
                <span>Classroom: <strong className="text-white">{exam.room}</strong></span>
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-mono text-slate-400 font-semibold uppercase tracking-wider">
                Exam Syllabus Topics:
              </span>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                {exam.topics}
              </p>
            </div>

            <div className="pt-2">
              <button
                onClick={() => onAskJarvis(`Prepare me for tomorrow's ${exam.title} in ${exam.course_code}`)}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-black font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition"
              >
                <Sparkles className="w-4 h-4" />
                <span>Generate Revision Plan & Practice Quiz with JARVIS</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
