import React from 'react';

export function VoiceWaveform({ isListening, isSpeaking }) {
  if (!isListening && !isSpeaking) return null;

  return (
    <div className="flex items-center gap-1 h-5 px-2">
      {[0.4, 0.8, 1.0, 0.6, 0.9, 0.5, 0.7].map((height, i) => (
        <span
          key={i}
          className={`w-1 rounded-full ${
            isListening ? 'bg-cyan-400' : 'bg-emerald-400'
          } wave-bar`}
          style={{
            height: `${height * 100}%`,
            animationDelay: `${i * 0.15}s`
          }}
        />
      ))}
    </div>
  );
}
