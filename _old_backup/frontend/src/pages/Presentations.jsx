import React, { useState, useEffect } from 'react';
import { Presentation, Sparkles, Download, ExternalLink, Clock, Play } from 'lucide-react';
import { api } from '../services/api';

export function Presentations() {
  const [presentations, setPresentations] = useState([]);
  const [topic, setTopic] = useState('');
  const [slideCount, setSlideCount] = useState(10);
  const [audience, setAudience] = useState('College Students');
  const [keyPoints, setKeyPoints] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPresentations();
  }, []);

  const loadPresentations = async () => {
    try {
      const data = await api.getPresentations();
      setPresentations(data || []);
    } catch (e) {
      console.error('Presentations load error:', e);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    try {
      const pointsArray = keyPoints
        ? keyPoints.split(',').map(s => s.trim()).filter(Boolean)
        : null;

      await api.generatePresentation({
        topic: topic.trim(),
        slide_count: Number(slideCount),
        audience,
        key_points: pointsArray
      });

      setTopic('');
      setKeyPoints('');
      await loadPresentations();
      alert('PowerPoint presentation successfully generated!');
    } catch (err) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleOpen = async (filePath) => {
    try {
      await api.openPresentation(filePath);
    } catch (err) {
      alert(`Could not launch presentation: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
          <Presentation className="w-6 h-6 text-cyan-400" />
          AI PowerPoint Presentation Generator
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Generates genuine Microsoft PowerPoint (.pptx) decks formatted with structured sections, bullets, and speaker notes.
        </p>
      </div>

      {/* Generator Form */}
      <div className="p-6 rounded-3xl bg-[#0D121D] border border-cyan-500/20 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          Create New Presentation
        </h2>

        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Presentation Topic / Title</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Artificial Intelligence Seminar, Binary Trees, Deep Learning Architectures"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Slide Count</label>
              <input
                type="number"
                min="3"
                max="20"
                value={slideCount}
                onChange={(e) => setSlideCount(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Target Audience</label>
              <select
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-400"
              >
                <option value="College Students">College Students / Academic</option>
                <option value="Seminar / Conference">Professor & Seminar Panel</option>
                <option value="Beginners">Beginners & Non-technical</option>
                <option value="Industry Engineering Team">Industry Engineering Team</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400 font-semibold">Key Subtopics (comma separated)</label>
              <input
                type="text"
                value={keyPoints}
                onChange={(e) => setKeyPoints(e.target.value)}
                placeholder="e.g. Neural Networks, Backprop, Ethics, Scaling"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={loading || !topic.trim()}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-black font-bold text-xs shadow-lg shadow-cyan-500/20 disabled:opacity-50 transition flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Generating PPTX Slides...' : 'Generate Presentation (.pptx)'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Gallery of Created Presentations */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <span>Generated Presentations</span>
          <span className="text-xs font-mono text-cyan-400">({presentations.length})</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {presentations.map((p) => (
            <div
              key={p.id}
              className="p-5 rounded-2xl bg-[#0D121D] border border-slate-800 hover:border-slate-700 transition space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
                  <Presentation className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-white leading-snug">{p.title}</h4>
                <p className="text-xs text-slate-400 line-clamp-2">{p.description}</p>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono">
                  <Clock className="w-3 h-3" />
                  <span>{p.created_at}</span>
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
                <button
                  onClick={() => handleOpen(p.file_path)}
                  className="flex-1 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center justify-center gap-1.5 transition"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>Open in PowerPoint</span>
                </button>
                <a
                  href={p.download_url}
                  download
                  className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 transition"
                  title="Download PPTX"
                >
                  <Download className="w-4 h-4" />
                </a>
              </div>
            </div>
          ))}

          {presentations.length === 0 && (
            <div className="col-span-full py-12 text-center text-xs text-slate-500">
              No presentations generated yet. Enter a topic above to create one.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
