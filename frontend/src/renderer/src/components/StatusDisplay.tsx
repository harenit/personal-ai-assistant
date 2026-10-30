import type { AIState } from "../types/assistant";

const STATE_COPY: Record<AIState, { label: string; detail: string }> = {
  connecting: { label: "CONNECTING", detail: "Reaching the AURA core..." },
  idle: { label: "IDLE", detail: "Awaiting your command" },
  listening: { label: "LISTENING", detail: "Go ahead, I'm listening..." },
  thinking: { label: "THINKING", detail: "Thinking through your request..." },
  speaking: { label: "SPEAKING", detail: "Responding..." },
  working: { label: "WORKING", detail: "Performing your computer task..." },
  waiting_permission: { label: "APPROVAL NEEDED", detail: "Awaiting your authorization..." },
  success: { label: "SUCCESS", detail: "Task completed happily!" },
  error: { label: "ATTENTION", detail: "Something didn't go quite right..." },
};

export default function StatusDisplay({ state }: { state: AIState }): JSX.Element {
  const copy = STATE_COPY[state];
  return (
    <div className="status-display" data-state={state}>
      <span className="status-indicator" />
      <span className="status-label">{copy.label}</span>
      <span className="status-detail">{copy.detail}</span>
    </div>
  );
}
