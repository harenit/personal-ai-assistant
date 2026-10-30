import { useEffect, useRef, useState } from "react";
import type { AIState, ChatMessage } from "../types/assistant";
import type { BackendStatus } from "../hooks/useBackendStatus";
import { SAMPLE_MESSAGES } from "../data/mockData";
import {
  converse,
  respondToText,
  playBase64WavControllable,
  synthesizeSpeech,
  type PendingConfirmation,
} from "../lib/voiceClient";
import { useVoiceConversation } from "../hooks/useVoiceConversation";
import { useAudioLevel } from "../hooks/useAudioLevel";
import { playWakeChime } from "../lib/chime";
import { getConversationHistory } from "../lib/memoryClient";
import AuraRobot from "./AuraRobot";
import StatusDisplay from "./StatusDisplay";
import ChatArea from "./ChatArea";
import Composer from "./Composer";
import ConfirmDialog from "./ConfirmDialog";

let messageCounter = 0;
function nextId(): string {
  messageCounter += 1;
  return `msg-${messageCounter}`;
}

/**
 * Home screen: AURA animated robot companion + status + chat + composer.
 */
interface HomeViewProps {
  backendStatus: BackendStatus;
}

export default function HomeView({ backendStatus }: HomeViewProps): JSX.Element {
  const [processingState, setProcessingState] = useState<"thinking" | "speaking" | null>(null);
  const [actionState, setActionState] = useState<"working" | "success" | "error" | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>(SAMPLE_MESSAGES);
  const [pendingConfirmation, setPendingConfirmation] = useState<PendingConfirmation | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [livePartialText, setLivePartialText] = useState<string | null>(null);

  // Restore stored conversation history from persistent memory
  useEffect(() => {
    getConversationHistory()
      .then((data) => {
        if (data.messages && data.messages.length > 0) {
          setMessages(
            data.messages.map((m, idx) => ({
              id: `stored-${idx}`,
              role: m.role,
              text: m.text,
              timestamp: Date.now() - (data.messages.length - idx) * 1000,
            }))
          );
        }
      })
      .catch(() => {});
  }, [backendStatus]);

  const { elementRef: coreRef, setLevelFromMicFrame, attachPlayback, reset: resetAudioLevel } = useAudioLevel();

  function addMessage(role: ChatMessage["role"], text: string): void {
    setMessages((prev) => [...prev, { id: nextId(), role, text, timestamp: Date.now() }]);
  }

  // Shared by the typed-message paths (handleSend/handleDialogConfirm) and
  // the wake acknowledgment — not by handleUtterance, which uses
  // speakWithBargeIn instead so talking over AURA stops it immediately.
  async function speakReply(reply: string | null, audioBase64: string): Promise<void> {
    if (reply !== null) addMessage("assistant", reply);
    setProcessingState("speaking");
    const playback = playBase64WavControllable(audioBase64);
    const stopLevel = attachPlayback(playback.audio);
    await playback.done;
    stopLevel();
    setProcessingState(null);
  }

  // Called by useVoiceConversation once VAD decides the user has finished an
  // utterance — resolving this ends the "thinking"/"speaking" span, after
  // which the hook resumes listening automatically if voice mode is still on.
  // Uses speakWithBargeIn (not the plain speakReply above) so talking over
  // AURA while it replies stops playback immediately.
  async function handleUtterance(wavBlob: Blob): Promise<void> {
    setLivePartialText(null);
    resetAudioLevel();
    setProcessingState("thinking");
    try {
      const { transcript, reply, audioBase64, confirmation } = await converse(wavBlob);
      if (transcript) addMessage("user", transcript);
      
      // If a task completed successfully
      if (!confirmation && reply) {
        setActionState("success");
        setTimeout(() => setActionState(null), 1800);
      }
      
      addMessage("assistant", reply);
      setProcessingState("speaking");
      await speakWithBargeIn(audioBase64);
      setProcessingState(null);
      setPendingConfirmation(confirmation);
    } catch {
      setActionState("error");
      setTimeout(() => setActionState(null), 2500);
      addMessage("assistant", "Sorry, I couldn't reach the voice backend just now.");
      setProcessingState(null);
    }
  }

  const auraApi = window.aura || window.jarvis;

  const { voiceModeActive, toggleVoiceMode, startFromWakeWord, speakWithBargeIn } = useVoiceConversation({
    onUtterance: handleUtterance,
    canListen: () => auraApi.settings.getMicrophone(),
    onSpeechStart: () => setLivePartialText(""),
    onPartialTranscript: (text) => setLivePartialText(text),
    onMicFrame: setLevelFromMicFrame,
    onPlaybackStart: attachPlayback,
    onError: (message) => addMessage("assistant", message),
  });

  // Lets the tray menu's "Activate Assistant" item toggle voice mode the same
  // way the mic button does, without resubscribing every render.
  const toggleVoiceModeRef = useRef(toggleVoiceMode);
  toggleVoiceModeRef.current = toggleVoiceMode;

  useEffect(() => {
    return auraApi.onActivateAssistant(() => toggleVoiceModeRef.current());
  }, []);

  // A wake-word detection ("Hey Aura" / "Aura") is distinct from a manual
  // mic press: play an instant chime, say a quick "Yes?" acknowledgment, and
  // only then start listening for the actual command.
  const startFromWakeWordRef = useRef(startFromWakeWord);
  startFromWakeWordRef.current = startFromWakeWord;

  useEffect(() => {
    return auraApi.onWakeTriggered(() => {
      void (async () => {
        playWakeChime();
        try {
          const audioBase64 = await synthesizeSpeech("Yes?");
          await speakReply(null, audioBase64);
        } catch {
          setProcessingState(null);
        }
        startFromWakeWordRef.current();
      })();
    });
  }, []);

  async function handleSend(text: string): Promise<void> {
    addMessage("user", text);
    resetAudioLevel();
    setProcessingState("thinking");
    try {
      const { reply, audioBase64, confirmation } = await respondToText(text);
      if (!confirmation && reply) {
        setActionState("success");
        setTimeout(() => setActionState(null), 1800);
      }
      await speakReply(reply, audioBase64);
      setPendingConfirmation(confirmation);
    } catch {
      setActionState("error");
      setTimeout(() => setActionState(null), 2500);
      addMessage("assistant", "Sorry, I couldn't reach the AI backend just now.");
      setProcessingState(null);
    }
  }

  // The confirmation dialog is a deterministic alternative to typing/saying
  // "yes"/"no" — it sends the exact same text through the exact same
  // pipeline, so the backend's confirmation flow needs no knowledge of it.
  async function handleDialogConfirm(answer: "yes" | "no"): Promise<void> {
    setConfirming(true);
    try {
      addMessage("user", answer === "yes" ? "Yes" : "No");
      resetAudioLevel();
      setActionState("working");
      const { reply, audioBase64, confirmation } = await respondToText(answer);
      if (answer === "yes") {
        setActionState("success");
        setTimeout(() => setActionState(null), 2000);
      } else {
        setActionState(null);
      }
      await speakReply(reply, audioBase64);
      setPendingConfirmation(confirmation);
    } catch {
      setActionState("error");
      setTimeout(() => setActionState(null), 2500);
      addMessage("assistant", "Sorry, I couldn't reach the AI backend just now.");
      setProcessingState(null);
    } finally {
      setConfirming(false);
    }
  }

  // Calculate high-fidelity state matching AURA's 8 visual states
  let state: AIState = "idle";
  if (pendingConfirmation) {
    state = "waiting_permission";
  } else if (actionState) {
    state = actionState;
  } else if (processingState) {
    state = processingState;
  } else if (voiceModeActive) {
    state = "listening";
  } else {
    state = "idle";
  }

  // The backend not being reachable overrides whatever the local state
  // machine thinks is happening
  const displayState: AIState = backendStatus === "online" ? state : "connecting";
  const composerDisabled =
    state === "thinking" || state === "speaking" || state === "working" || backendStatus !== "online";

  return (
    <div className="home-view">
      <div className="core-stage">
        <AuraRobot ref={coreRef} state={displayState} onTap={toggleVoiceMode} />
        <StatusDisplay state={displayState} />
      </div>

      <ChatArea messages={messages} livePartialText={livePartialText} />

      <Composer
        state={displayState}
        disabled={composerDisabled}
        onSend={handleSend}
        onMicPress={toggleVoiceMode}
      />

      {pendingConfirmation && (
        <ConfirmDialog prompt={pendingConfirmation.prompt} busy={confirming} onConfirm={handleDialogConfirm} />
      )}
    </div>
  );
}
