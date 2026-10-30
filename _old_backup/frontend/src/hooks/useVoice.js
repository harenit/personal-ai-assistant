import { useState, useEffect, useRef } from 'react';

// Web Audio API Synthesized Sci-Fi Chime (Zero external mp3 needed)
function playSciFiChime(type = 'activate') {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();

    if (type === 'activate') {
      // High-tech ascending two-tone chime
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      osc1.type = 'sine';
      osc2.type = 'triangle';

      osc1.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc1.frequency.exponentialRampToValueAtTime(880.00, ctx.currentTime + 0.12); // A5

      osc2.frequency.setValueAtTime(880.00, ctx.currentTime);
      osc2.frequency.exponentialRampToValueAtTime(1174.66, ctx.currentTime + 0.15); // D6

      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);

      osc1.start();
      osc2.start();
      osc1.stop(ctx.currentTime + 0.35);
      osc2.stop(ctx.currentTime + 0.35);
    } else if (type === 'complete') {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880.00, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.18);
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.25);
    }
  } catch {
    // AudioContext blocked or unsupported
  }
}

export function useVoice({ onTranscript, onWakeWord } = {}) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [wakeWordActive, setWakeWordActive] = useState(true);
  const [supported, setSupported] = useState(false);

  const recognitionRef = useRef(null);
  const isContinuousListening = useRef(true);
  const transcriptRef = useRef('');

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let currentText = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const text = event.results[i][0].transcript;
          currentText += text;

          // Check for wake word trigger
          const lower = text.toLowerCase().trim();
          if (lower.includes('hey jarvis') || lower.includes('jarvis') || lower.includes('alexa')) {
            playSciFiChime('activate');
            
            // Extract command after wake word if present
            let command = lower
              .replace(/hey jarvis/gi, '')
              .replace(/jarvis/gi, '')
              .replace(/alexa/gi, '')
              .trim();

            if (event.results[i].isFinal) {
              if (onWakeWord && command) {
                onWakeWord(command);
              } else if (onTranscript && command) {
                onTranscript(command);
              }
            }
          }
        }

        setTranscript(currentText);
        transcriptRef.current = currentText;
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition warning:', event.error);
        if (event.error === 'not-allowed') {
          setIsListening(false);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
        // Automatically restart if continuous wake-word mode is desired
        if (isContinuousListening.current) {
          try {
            recognition.start();
          } catch {
            // ignore rapid restart error
          }
        }
      };

      recognitionRef.current = recognition;

      // Start continuous listening initially
      try {
        recognition.start();
      } catch {
        // User may need to interact with page first
      }
    }

    // Global Hotkey: Ctrl + Space to trigger voice command
    const handleKeyDown = (e) => {
      if (e.ctrlKey && (e.code === 'Space' || e.key === ' ')) {
        e.preventDefault();
        playSciFiChime('activate');
        toggleListening();
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      isContinuousListening.current = false;
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const startListening = () => {
    if (!recognitionRef.current) return;
    try {
      setTranscript('');
      isContinuousListening.current = true;
      recognitionRef.current.start();
      playSciFiChime('activate');
    } catch {
      // already started
    }
  };

  const stopListening = () => {
    if (!recognitionRef.current) return;
    try {
      const finalVal = transcriptRef.current;
      isContinuousListening.current = false;
      recognitionRef.current.stop();
      if (finalVal && onTranscript) {
        onTranscript(finalVal);
      }
    } catch {
      // ignore
    }
  };

  const speakText = (text) => {
    if (!window.speechSynthesis || !text) return;
    window.speechSynthesis.cancel();

    const clean = text
      .replace(/[*#_`]/g, '')
      .replace(/\[.*?\]/g, '')
      .replace(/https?:\/\/\S+/g, 'link')
      .trim();

    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    // Pick best natural voice if available
    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(v => 
      (v.name.includes('Natural') || v.name.includes('David') || v.name.includes('George') || v.name.includes('Google US English')) && v.lang.startsWith('en')
    );
    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => {
      setIsSpeaking(false);
      playSciFiChime('complete');
    };
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  return {
    isListening,
    isSpeaking,
    transcript,
    supported,
    wakeWordActive,
    toggleListening,
    startListening,
    stopListening,
    speakText,
    stopSpeaking,
    playSciFiChime
  };
}
