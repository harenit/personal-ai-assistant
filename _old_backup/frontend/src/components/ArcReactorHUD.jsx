import React, { useState, useEffect } from 'react';
import { 
  Mic, MicOff, Volume2, Sparkles, Terminal, Activity, 
  Cpu, HardDrive, Shield, Bell, ChevronUp, Play, Folder,
  CheckCircle2, AlertTriangle, Radio
} from 'lucide-react';

export function ArcReactorHUD({
  state = 'idle', // 'idle' | 'listening' | 'processing' | 'speaking' | 'waiting_permission'
  transcript = '',
  statusMessage = 'SYSTEM READY // AWAITING DIRECTIVE',
  telemetry = { cpu_percent: 43, ram_percent: 71, disk_percent: 64 },
  isListening = false,
  isSpeaking = false,
  onToggleVoice,
  onExecuteCommand,
  onExpandPanel
}) {
  const [pulseDegree, setPulseDegree] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPulseDegree(prev => (prev + 1) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Determine state-based visuals
  const isActionActive = isListening || state === 'listening';
  const isReasoning = state === 'processing' || state === 'planning';
  const isVocalizing = isSpeaking || state === 'speaking';
  const isWarning = state === 'waiting_permission';

  const glowColor = isWarning 
    ? '#f59e0b' 
    : isActionActive 
      ? '#00ffff' 
      : isReasoning 
        ? '#38bdf8' 
        : isVocalizing 
          ? '#22d3ee' 
          : '#00f0ff';

  return (
    <div className="relative w-full min-h-[640px] flex flex-col items-center justify-center bg-[#010813] text-[#00f0ff] font-mono select-none overflow-hidden rounded-2xl border border-cyan-500/20 shadow-[0_0_50px_rgba(0,240,255,0.08)]">
      {/* Background Cyber Grid & Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(0,180,255,0.07)_0%,rgba(1,8,19,0.95)_70%)] pointer-events-none" />
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `linear-gradient(#00f0ff 1px, transparent 1px), linear-gradient(90deg, #00f0ff 1px, transparent 1px)`,
          backgroundSize: '32px 32px'
        }}
      />

      {/* ================= TOP-LEFT: HI-TECH INTERFACE & HEX GRID ================= */}
      <div className="absolute top-6 left-8 flex flex-col items-start space-y-2 z-10">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-xs tracking-[0.25em] font-bold text-cyan-300 drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]">
            HI-TECH INTERFACE
          </span>
        </div>
        
        {/* Angled Tech Leader Line */}
        <div className="flex items-center space-x-1">
          <div className="w-16 h-[1px] bg-cyan-400/60" />
          <div className="w-3 h-[1px] bg-cyan-400 rotate-45 transform origin-left" />
        </div>

        {/* Hexagonal Mesh (Matching Image) */}
        <div className="pt-2 opacity-70">
          <svg width="110" height="60" viewBox="0 0 110 60" className="stroke-cyan-400 fill-cyan-950/20 stroke-[1.2]">
            <polygon points="15,5 30,5 38,18 30,31 15,31 7,18" />
            <polygon points="38,5 53,5 61,18 53,31 38,31 30,18" />
            <polygon points="61,5 76,5 84,18 76,31 61,31 53,18" />
            <polygon points="26,24 41,24 49,37 41,50 26,50 18,37" />
            <polygon points="49,24 64,24 72,37 64,50 49,50 41,37" />
            <polygon points="72,24 87,24 95,37 87,50 72,50 64,37" />
          </svg>
        </div>

        <div className="text-[10px] text-cyan-400/60 tracking-wider">
          NODE: WIN11.JARVIS // ACTIVE
        </div>
      </div>

      {/* ================= TOP-RIGHT: 43% TELEMETRY & EQUALIZER ================= */}
      <div className="absolute top-6 right-8 flex flex-col items-end space-y-2 z-10">
        <div className="flex items-baseline space-x-1">
          <span className="text-3xl font-extrabold tracking-tighter text-cyan-300 drop-shadow-[0_0_12px_rgba(0,240,255,0.7)]">
            {telemetry?.cpu_percent ?? 43}%
          </span>
          <span className="text-[10px] text-cyan-400/70 font-semibold tracking-wider">CPU LOAD</span>
        </div>

        {/* Tech Line Connector */}
        <div className="w-32 h-[1px] bg-gradient-to-l from-cyan-400 to-transparent" />

        {/* Audio / Activity Equalizer Bars */}
        <div className="flex items-end space-x-1.5 h-7 pt-1">
          {[40, 75, 25, 90, 60, 85, 30, 95, 50, 70].map((h, i) => (
            <div
              key={i}
              className={`w-1.5 rounded-sm transition-all duration-300 ${
                isActionActive || isVocalizing 
                  ? 'bg-cyan-400 animate-pulse shadow-[0_0_6px_#00f0ff]' 
                  : 'bg-cyan-500/40'
              }`}
              style={{
                height: isActionActive ? `${Math.max(20, (h * Math.random() + 20))}%` : `${h}%`
              }}
            />
          ))}
        </div>

        <div className="text-[10px] text-cyan-400/50 uppercase tracking-widest">
          MEM: {telemetry?.ram_percent ?? 71}% // DISK: {telemetry?.disk_percent ?? 64}%
        </div>
      </div>

      {/* ================= BOTTOM-LEFT: 71% TELEMETRY & CHEVRON ================= */}
      <div className="absolute bottom-8 left-8 flex flex-col items-start space-y-2 z-10">
        <div className="flex items-center space-x-3">
          <div className="flex flex-col items-center justify-center p-1.5 border border-cyan-400/40 rounded bg-cyan-950/20">
            <ChevronUp className="w-4 h-4 text-cyan-300 animate-bounce" />
            <ChevronUp className="w-4 h-4 -mt-2 text-cyan-400/80" />
          </div>
          <div>
            <div className="text-3xl font-extrabold tracking-tighter text-cyan-300 drop-shadow-[0_0_12px_rgba(0,240,255,0.7)]">
              {telemetry?.ram_percent ?? 71}%
            </div>
            <div className="text-[10px] text-cyan-400/60 uppercase tracking-wider">
              MEMORY ALLOCATION
            </div>
          </div>
        </div>

        {/* Tech Border Hook */}
        <div className="flex items-center space-x-1 w-32">
          <div className="w-2 h-2 border-l border-b border-cyan-400" />
          <div className="flex-1 h-[1px] bg-gradient-to-r from-cyan-400 to-transparent" />
        </div>

        <div className="text-[10px] text-cyan-400/50">
          WAKE WORD: "HEY JARVIS" [READY]
        </div>
      </div>

      {/* ================= BOTTOM-RIGHT: FUTURISTIC & HEX MESH ================= */}
      <div className="absolute bottom-8 right-8 flex flex-col items-end space-y-2 z-10">
        <div className="opacity-70">
          <svg width="90" height="50" viewBox="0 0 90 50" className="stroke-cyan-400 fill-cyan-950/20 stroke-[1.2]">
            <polygon points="15,5 30,5 38,18 30,31 15,31 7,18" />
            <polygon points="38,5 53,5 61,18 53,31 38,31 30,18" />
            <polygon points="26,24 41,24 49,37 41,50 26,50 18,37" />
            <polygon points="49,24 64,24 72,37 64,50 49,50 41,37" />
          </svg>
        </div>

        <div className="w-24 h-[1px] bg-gradient-to-l from-cyan-400 to-transparent" />

        <div className="text-sm font-black tracking-[0.3em] text-cyan-300 drop-shadow-[0_0_10px_rgba(0,240,255,0.7)]">
          FUTURISTIC
        </div>

        <div className="text-[10px] text-cyan-400/60 tracking-wider">
          SECURITY PROTOCOL: LEVEL 1 ENGAGED
        </div>
      </div>

      {/* ================= CENTER: ARC REACTOR CORE (FROM IMAGE) ================= */}
      <div className="relative flex items-center justify-center my-6 z-20">
        
        {/* Left Curved Bracket / Vent */}
        <div className="absolute -left-52 w-16 h-72 border-l-2 border-y-2 border-cyan-400/60 rounded-l-full flex flex-col items-start justify-center pl-2 space-y-2 pointer-events-none opacity-80">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="w-4 h-1.5 bg-cyan-400/60 rounded-sm" />
          ))}
        </div>

        {/* Right Curved Bracket / Vent */}
        <div className="absolute -right-52 w-16 h-72 border-r-2 border-y-2 border-cyan-400/60 rounded-r-full flex flex-col items-end justify-center pr-2 space-y-2 pointer-events-none opacity-80">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="w-4 h-1.5 bg-cyan-400/60 rounded-sm" />
          ))}
        </div>

        {/* Main SVG Arc Reactor */}
        <div 
          onClick={onToggleVoice}
          className="relative w-80 h-80 sm:w-96 sm:h-96 flex items-center justify-center cursor-pointer group transition-transform duration-500 hover:scale-[1.03]"
          title="Click to Activate JARVIS Voice"
        >
          {/* Ambient Outer Halo */}
          <div 
            className="absolute inset-0 rounded-full blur-2xl opacity-40 transition-all duration-700 pointer-events-none"
            style={{
              backgroundColor: glowColor,
              transform: isActionActive ? 'scale(1.2)' : 'scale(1.0)'
            }}
          />

          <svg 
            viewBox="0 0 400 400" 
            className="w-full h-full drop-shadow-[0_0_25px_rgba(0,240,255,0.5)]"
          >
            {/* 1. Outermost Solid Thin Guide Ring */}
            <circle cx="200" cy="200" r="190" fill="none" stroke="#00f0ff" strokeWidth="1.5" strokeOpacity="0.4" />

            {/* 2. Outer Segmented Tech Ring (Rotating Clockwise) */}
            <g 
              style={{ 
                transformOrigin: '200px 200px',
                animation: isReasoning ? 'spin 3s linear infinite' : 'spin 30s linear infinite' 
              }}
            >
              {[...Array(36)].map((_, i) => {
                const angle = i * 10;
                const isHighlight = i % 3 === 0;
                return (
                  <rect
                    key={i}
                    x="197"
                    y="18"
                    width={isHighlight ? "6" : "3"}
                    height={isHighlight ? "16" : "10"}
                    fill="#00f0ff"
                    opacity={isHighlight ? "0.9" : "0.5"}
                    transform={`rotate(${angle} 200 200)`}
                  />
                );
              })}
            </g>

            {/* 3. Middle Thick Track with High-Tech Arc Blocks (From image) */}
            <circle 
              cx="200" 
              cy="200" 
              r="155" 
              fill="none" 
              stroke="#00f0ff" 
              strokeWidth="6" 
              strokeOpacity="0.3" 
            />
            
            {/* Rotating Segmented Tech Dial */}
            <g
              style={{
                transformOrigin: '200px 200px',
                animation: isReasoning ? 'spin-reverse 4s linear infinite' : 'spin-reverse 45s linear infinite'
              }}
            >
              <circle
                cx="200"
                cy="200"
                r="155"
                fill="none"
                stroke="#00ffff"
                strokeWidth="12"
                strokeDasharray="40 15 80 25 120 40"
                strokeLinecap="round"
                opacity="0.85"
                filter="drop-shadow(0 0 6px #00ffff)"
              />
              <circle
                cx="200"
                cy="200"
                r="140"
                fill="none"
                stroke="#00f0ff"
                strokeWidth="2"
                strokeDasharray="4 8"
                opacity="0.6"
              />
            </g>

            {/* 4. Fine Tick-Mark Graduation Ring */}
            <circle cx="200" cy="200" r="126" fill="none" stroke="#00f0ff" strokeWidth="1" strokeOpacity="0.5" />
            <g style={{ transformOrigin: '200px 200px', animation: 'spin 60s linear infinite' }}>
              {[...Array(60)].map((_, i) => (
                <line
                  key={i}
                  x1="200"
                  y1="76"
                  x2="200"
                  y2={i % 5 === 0 ? "84" : "80"}
                  stroke="#00f0ff"
                  strokeWidth={i % 5 === 0 ? "2" : "1"}
                  opacity={i % 5 === 0 ? "0.9" : "0.4"}
                  transform={`rotate(${i * 6} 200 200)`}
                />
              ))}
            </g>

            {/* 5. Inner Concentric Heavy Borders */}
            <circle cx="200" cy="200" r="110" fill="none" stroke="#00f0ff" strokeWidth="3" strokeOpacity="0.8" />
            <circle cx="200" cy="200" r="95" fill="none" stroke="#00f0ff" strokeWidth="8" strokeOpacity="0.25" />

            {/* 6. High-Tech Segmented Radial Gauge (From Image) */}
            <g style={{ transformOrigin: '200px 200px', animation: isActionActive ? 'spin 6s linear infinite' : 'spin 20s linear infinite' }}>
              <circle
                cx="200"
                cy="200"
                r="95"
                fill="none"
                stroke="#00f0ff"
                strokeWidth="10"
                strokeDasharray="28 8 50 14 70 20"
                opacity="0.9"
                filter="drop-shadow(0 0 8px #00f0ff)"
              />
            </g>

            {/* 7. Central Core Glow Bulb & Iris Rings */}
            <circle 
              cx="200" 
              cy="200" 
              r="68" 
              fill="#011425" 
              stroke="#00f0ff" 
              strokeWidth="3" 
              opacity="0.95" 
            />

            {/* Concentric Inner Lens Rings */}
            <circle cx="200" cy="200" r="54" fill="none" stroke="#00ffff" strokeWidth="2" strokeDasharray="16 8" opacity="0.8" />
            <circle cx="200" cy="200" r="40" fill="none" stroke="#00f0ff" strokeWidth="4" strokeOpacity="0.6" />
            
            {/* Center Core Light (Pulsating) */}
            <circle 
              cx="200" 
              cy="200" 
              r="26" 
              fill={glowColor}
              className={isActionActive ? "animate-ping" : ""}
              opacity={isActionActive ? "0.95" : "0.75"}
              filter="drop-shadow(0 0 16px #00ffff)"
            />
            <circle cx="200" cy="200" r="16" fill="#ffffff" opacity="0.9" filter="drop-shadow(0 0 8px #ffffff)" />

            {/* Horizontal & Vertical Crosshair Lines */}
            <line x1="160" y1="200" x2="185" y2="200" stroke="#00f0ff" strokeWidth="2.5" opacity="0.8" />
            <line x1="215" y1="200" x2="240" y2="200" stroke="#00f0ff" strokeWidth="2.5" opacity="0.8" />
            <line x1="200" y1="160" x2="200" y2="185" stroke="#00f0ff" strokeWidth="2.5" opacity="0.8" />
            <line x1="200" y1="215" x2="200" y2="240" stroke="#00f0ff" strokeWidth="2.5" opacity="0.8" />
          </svg>

          {/* Central Overlay Icon */}
          <div className="absolute flex flex-col items-center justify-center pointer-events-none">
            {isActionActive ? (
              <Mic className="w-8 h-8 text-white drop-shadow-[0_0_10px_#00ffff] animate-pulse" />
            ) : isSpeaking ? (
              <Volume2 className="w-8 h-8 text-white drop-shadow-[0_0_10px_#00ffff] animate-pulse" />
            ) : (
              <Radio className="w-7 h-7 text-cyan-200 group-hover:scale-110 transition-transform drop-shadow-[0_0_8px_#00f0ff]" />
            )}
          </div>
        </div>
      </div>

      {/* ================= STATUS TICKER & INTENT DECODER ================= */}
      <div className="flex flex-col items-center space-y-2 z-20 max-w-xl text-center px-4">
        {/* State Badge */}
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-400/40 text-xs tracking-wider">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-bold text-cyan-200 uppercase">
            {isActionActive 
              ? 'LISTENING TO COMMAND...' 
              : isReasoning 
                ? 'REASONING & SELECTING TOOLS...' 
                : isVocalizing 
                  ? 'SPEAKING RESPONSE...' 
                  : isWarning
                    ? 'SECURITY CONFIRMATION REQUIRED'
                    : 'JARVIS ONLINE // READY'}
          </span>
        </div>

        {/* Real-time Subtitle / Status Display */}
        <div className="text-sm sm:text-base font-semibold text-cyan-100 drop-shadow-[0_0_8px_rgba(0,240,255,0.4)] min-h-[28px]">
          {transcript ? (
            <span className="italic">"{transcript}"</span>
          ) : (
            statusMessage
          )}
        </div>

        <div className="text-[11px] text-cyan-400/60">
          Tip: Say <span className="text-cyan-200 font-bold">"Hey JARVIS"</span>, press <span className="text-cyan-200 font-bold">Ctrl + Space</span>, or click the Arc Reactor
        </div>
      </div>

      {/* ================= QUICK SCI-FI DIRECTIVE DOCK ================= */}
      <div className="flex flex-wrap items-center justify-center gap-2 mt-6 mb-4 z-20 px-4">
        {[
          { label: 'Check Assignments', cmd: 'Do I have any assignments due this week?' },
          { label: 'Open Calculator', cmd: 'Open Calculator.' },
          { label: 'Search Drive Files', cmd: 'Search files for syllabus or lecture notes.' },
          { label: 'Create AI Slides', cmd: 'Create a 10-slide presentation about AI and open it.' },
          { label: 'Draft Professor Email', cmd: 'Draft an email to Prof. Martinez asking for an extension.' },
          { label: 'Open Explorer', cmd: 'Open File Explorer.' }
        ].map((item, idx) => (
          <button
            key={idx}
            onClick={() => onExecuteCommand && onExecuteCommand(item.cmd)}
            className="px-3 py-1.5 text-xs rounded border border-cyan-500/30 bg-cyan-950/30 text-cyan-300 hover:bg-cyan-500/20 hover:border-cyan-400 hover:shadow-[0_0_12px_rgba(0,240,255,0.4)] transition-all cursor-pointer"
          >
            {item.label}
          </button>
        ))}
        {onExpandPanel && (
          <button
            onClick={onExpandPanel}
            className="px-3 py-1.5 text-xs rounded border border-cyan-400/60 bg-cyan-500/20 text-cyan-100 hover:bg-cyan-400/30 shadow-[0_0_10px_rgba(0,240,255,0.3)] transition-all cursor-pointer flex items-center space-x-1"
          >
            <Terminal className="w-3.5 h-3.5 mr-1" />
            <span>Open Command Terminal</span>
          </button>
        )}
      </div>

      {/* CSS Keyframe Animations */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes spin-reverse {
          from { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }
      `}</style>
    </div>
  );
}
