import React from 'react';
import { Mic, MicOff, ShieldAlert, Cpu, Sparkles } from 'lucide-react';
import { VoiceWaveform } from './VoiceWaveform';

export function Header({
  title,
  isListening,
  isSpeaking,
  onToggleVoice,
  pendingPermissionsCount = 0,
  onOpenPermissions
}) {
  return (
    <header className="h-16 px-8 border-b border-slate-800/80 bg-[#0A0D14]/90 backdrop-blur-md flex items-center justify-between sticky top-0 z-30">
      <div>
        <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          {title}
        </h2>
      </div>

      <div className="flex items-center gap-4">
        {/* Voice Waveform if active */}
        <VoiceWaveform isListening={isListening} isSpeaking={isSpeaking} />

        {/* Demo Mode Badge */}
        <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/50 text-[11px] font-mono text-cyan-300">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
          DEMO MODE
        </div>

        {/* Local LLM indicator */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          Ollama: llama3.1:8b
        </div>

        {/* Pending Permissions Alert */}
        {pendingPermissionsCount > 0 && (
          <button
            onClick={onOpenPermissions}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/60 text-amber-300 text-xs font-semibold animate-pulse hover:bg-amber-500/30 transition"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{pendingPermissionsCount} Pending Auth</span>
          </button>
        )}

        {/* Voice Push-to-Talk Toggle Button */}
        <button
          onClick={onToggleVoice}
          title={isListening ? "Listening... Click to stop" : "Click to speak to JARVIS"}
          className={`relative flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
            isListening
              ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30 animate-pulse'
              : 'bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
          }`}
        >
          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-cyan-400" />}
          <span>{isListening ? "Listening..." : "Push to Talk"}</span>
        </button>
      </div>
    </header>
  );
}
