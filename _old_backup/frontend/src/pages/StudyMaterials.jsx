import React, { useState, useEffect } from 'react';
import { 
  FileText, Upload, Sparkles, HelpCircle, CheckCircle, 
  RotateCw, ChevronRight, BookOpen, Trash2, Award 
} from 'lucide-react';
import { api } from '../services/api';

export function StudyMaterials({ onAskJarvis }) {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [activeTab, setActiveTab] = useState('summary'); // summary, ask, quiz, flashcards
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [quizData, setQuizData] = useState([]);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizScore, setQuizScore] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [flippedCards, setFlippedCards] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data || []);
      if (data && data.length > 0 && !selectedDoc) {
        setSelectedDoc(data[0]);
      }
    } catch (e) {
      console.error('Error loading documents:', e);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const res = await api.uploadDocument(formData);
      await loadDocs();
      alert(`Indexed ${res.title} with ${res.chunks_indexed} vector chunks.`);
    } catch (err) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim() || !selectedDoc) return;
    setLoading(true);
    try {
      const res = await api.askDocument(selectedDoc.id, question.trim());
      setAnswer(res);
    } catch (err) {
      alert(`Question error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!selectedDoc) return;
    setLoading(true);
    setUserAnswers({});
    setQuizScore(null);
    try {
      const res = await api.generateQuiz(selectedDoc.id, selectedDoc.title, 10);
      setQuizData(res.quiz || []);
    } catch (err) {
      alert(`Quiz generation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAnswer = (qId, optionIdx) => {
    setUserAnswers(prev => ({ ...prev, [qId]: optionIdx }));
  };

  const handleGradeQuiz = () => {
    let score = 0;
    quizData.forEach(q => {
      if (userAnswers[q.id] === q.correct_index) {
        score += 1;
      }
    });
    setQuizScore(score);
  };

  const handleGenerateFlashcards = async () => {
    if (!selectedDoc) return;
    setLoading(true);
    setFlippedCards({});
    try {
      const res = await api.generateFlashcards(selectedDoc.id, selectedDoc.title, 8);
      setFlashcards(res.flashcards || []);
    } catch (err) {
      alert(`Flashcards error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleFlip = (id) => {
    setFlippedCards(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      await api.deleteDocument(docId);
      await loadDocs();
      setSelectedDoc(null);
    } catch (err) {
      alert(`Delete error: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <FileText className="w-6 h-6 text-cyan-400" />
            Study Materials & RAG Knowledge Base
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Semantic vector search, page citations, automatic quizzes, and active recall flashcards.
          </p>
        </div>

        <label className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-black font-bold text-xs flex items-center gap-2 cursor-pointer shadow-lg shadow-cyan-500/20 transition">
          <Upload className="w-4 h-4" />
          <span>Upload Study Material (PDF/DOCX/TXT)</span>
          <input
            type="file"
            onChange={handleUpload}
            accept=".pdf,.docx,.doc,.txt"
            className="hidden"
          />
        </label>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Document Library Sidebar */}
        <div className="p-5 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-4">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
            Indexed Documents ({documents.length})
          </h3>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {documents.map((doc) => {
              const isSelected = selectedDoc?.id === doc.id;
              return (
                <div
                  key={doc.id}
                  onClick={() => setSelectedDoc(doc)}
                  className={`p-3.5 rounded-2xl border text-left cursor-pointer transition flex items-center justify-between ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-300'
                      : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-900 text-slate-300'
                  }`}
                >
                  <div className="space-y-1 min-w-0 pr-2">
                    <h4 className="text-xs font-bold truncate text-white">{doc.title}</h4>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
                      <span>{doc.file_type.toUpperCase()}</span>
                      <span>•</span>
                      <span>{doc.chunk_count} chunks</span>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(doc.id);
                    }}
                    className="p-1 hover:text-rose-400 text-slate-500 transition shrink-0"
                    title="Delete document"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })}

            {documents.length === 0 && (
              <p className="text-xs text-slate-500 text-center py-8">
                No documents uploaded yet. Upload lecture notes, study guides, or slides above!
              </p>
            )}
          </div>
        </div>

        {/* Study Studio View */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-[#0D121D] border border-slate-800 space-y-5">
          {selectedDoc ? (
            <>
              {/* Document Tabs */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
                <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
                  <button
                    onClick={() => setActiveTab('summary')}
                    className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                      activeTab === 'summary' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Summary
                  </button>
                  <button
                    onClick={() => setActiveTab('ask')}
                    className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                      activeTab === 'ask' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Ask Document
                  </button>
                  <button
                    onClick={() => {
                      setActiveTab('quiz');
                      if (quizData.length === 0) handleGenerateQuiz();
                    }}
                    className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                      activeTab === 'quiz' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    10-MCQ Quiz
                  </button>
                  <button
                    onClick={() => {
                      setActiveTab('flashcards');
                      if (flashcards.length === 0) handleGenerateFlashcards();
                    }}
                    className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                      activeTab === 'flashcards' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Flashcards
                  </button>
                </div>

                <span className="text-xs font-mono text-cyan-400 font-bold truncate max-w-xs">
                  {selectedDoc.title}
                </span>
              </div>

              {/* TAB 1: SUMMARY */}
              {activeTab === 'summary' && (
                <div className="space-y-4">
                  <h4 className="text-xs font-mono uppercase text-slate-400 font-bold">
                    Executive Document Summary
                  </h4>
                  <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                    {selectedDoc.summary || "Generating summary..."}
                  </div>
                </div>
              )}

              {/* TAB 2: ASK DOCUMENT */}
              {activeTab === 'ask' && (
                <div className="space-y-4">
                  <form onSubmit={handleAsk} className="flex gap-2">
                    <input
                      type="text"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="Ask a question about this document..."
                      className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                    />
                    <button
                      type="submit"
                      disabled={loading || !question.trim()}
                      className="px-4 py-2.5 rounded-xl bg-cyan-500 text-black font-bold text-xs hover:bg-cyan-400 transition"
                    >
                      Ask
                    </button>
                  </form>

                  {answer && (
                    <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                      <h5 className="text-xs font-bold text-cyan-300">Answer:</h5>
                      <p className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">{answer.answer}</p>

                      {answer.citations && answer.citations.length > 0 && (
                        <div className="pt-2 border-t border-slate-800/80 space-y-1">
                          <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">Citations:</span>
                          <div className="flex flex-wrap gap-2">
                            {answer.citations.map((c, i) => (
                              <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-400">
                                {c.source} (Page {c.page})
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: 10-MCQ QUIZ */}
              {activeTab === 'quiz' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-mono uppercase text-slate-400 font-bold">
                      Practice Exam Quiz ({quizData.length} Questions)
                    </h4>
                    <button
                      onClick={handleGenerateQuiz}
                      className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                    >
                      <RotateCw className="w-3 h-3" /> Regenerate
                    </button>
                  </div>

                  {quizScore !== null && (
                    <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Award className="w-5 h-5 text-emerald-400" />
                        <span className="text-sm font-bold text-white">Quiz Score Result:</span>
                      </div>
                      <span className="text-base font-extrabold text-emerald-400 font-mono">
                        {quizScore} / {quizData.length} ({Math.round((quizScore / quizData.length) * 100)}%)
                      </span>
                    </div>
                  )}

                  <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                    {quizData.map((q, qIdx) => {
                      const selectedOption = userAnswers[q.id];
                      const isGraded = quizScore !== null;

                      return (
                        <div key={q.id || qIdx} className="p-4 rounded-2xl bg-slate-950/90 border border-slate-800 space-y-3">
                          <p className="text-xs font-bold text-white">
                            {qIdx + 1}. {q.question}
                          </p>

                          <div className="space-y-1.5">
                            {q.options.map((opt, optIdx) => {
                              const isSelected = selectedOption === optIdx;
                              const isCorrect = q.correct_index === optIdx;
                              let borderClasses = 'border-slate-800 hover:border-slate-700 text-slate-300';

                              if (isGraded) {
                                if (isCorrect) borderClasses = 'border-emerald-500 bg-emerald-950/30 text-emerald-300 font-bold';
                                else if (isSelected && !isCorrect) borderClasses = 'border-rose-500 bg-rose-950/30 text-rose-300';
                              } else if (isSelected) {
                                borderClasses = 'border-cyan-400 bg-cyan-950/40 text-cyan-300 font-bold';
                              }

                              return (
                                <button
                                  key={optIdx}
                                  onClick={() => handleSelectAnswer(q.id, optIdx)}
                                  className={`w-full text-left p-2.5 rounded-xl border text-xs transition flex items-center justify-between ${borderClasses}`}
                                >
                                  <span>{String.fromCharCode(65 + optIdx)}. {opt}</span>
                                  {isGraded && isCorrect && <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />}
                                </button>
                              );
                            })}
                          </div>

                          {isGraded && q.explanation && (
                            <p className="text-[11px] text-slate-400 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                              <strong className="text-cyan-400">Explanation:</strong> {q.explanation}
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="pt-2">
                    <button
                      onClick={handleGradeQuiz}
                      className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-black font-bold text-xs shadow-lg shadow-emerald-500/20 transition"
                    >
                      Grade Quiz
                    </button>
                  </div>
                </div>
              )}

              {/* TAB 4: FLASHCARDS */}
              {activeTab === 'flashcards' && (
                <div className="space-y-5">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-mono uppercase text-slate-400 font-bold">
                      Active Recall Flashcards ({flashcards.length})
                    </h4>
                    <button
                      onClick={handleGenerateFlashcards}
                      className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                    >
                      <RotateCw className="w-3 h-3" /> Regenerate
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {flashcards.map((card) => {
                      const isFlipped = !!flippedCards[card.id];
                      return (
                        <div
                          key={card.id}
                          onClick={() => toggleFlip(card.id)}
                          className={`p-5 rounded-2xl border cursor-pointer min-h-[160px] flex flex-col justify-between transition-all duration-300 shadow-md ${
                            isFlipped
                              ? 'bg-gradient-to-br from-indigo-950/80 to-slate-950 border-cyan-500/40 text-cyan-200'
                              : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-white'
                          }`}
                        >
                          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500">
                            <span>CARD #{card.id}</span>
                            <span className="text-cyan-400">{isFlipped ? "DEFINITION (CLICK TO FLIP)" : "CONCEPT (CLICK TO REVEAL)"}</span>
                          </div>

                          <div className="py-2 text-center">
                            <p className={`text-xs font-bold leading-relaxed ${isFlipped ? 'text-slate-200' : 'text-white text-sm'}`}>
                              {isFlipped ? card.back : card.front}
                            </p>
                          </div>

                          <div className="text-center text-[10px] text-slate-500 font-mono">
                            Tap to flip
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-20 text-slate-500 space-y-2">
              <BookOpen className="w-8 h-8 mx-auto text-slate-600" />
              <p className="text-xs">Select a document from the left library or upload notes to begin studying.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
