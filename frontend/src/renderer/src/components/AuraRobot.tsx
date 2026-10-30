import { forwardRef, useState } from "react";
import type { AIState } from "../types/assistant";

interface AuraRobotProps {
  state: AIState;
  onTap?: () => void;
  statusDetail?: string;
}

/**
 * AURA Robot — Central Animated Companion Interface.
 *
 * Drives all visual robot states:
 * - idle: Gentle floating & breathing, soft antenna beacon, natural periodic blinking
 * - listening: Glowing antenna halo, soundwave rings radiating with mic level (--core-level)
 * - thinking: Holographic data rings rotating around head, cognitive eye shimmer
 * - speaking: Voice waveform visualizer reacting to speech audio, lively speaking bounce
 * - working: Floating holographic HUD screen with data streams and task indicators
 * - waiting_permission: Holographic amber shield badge, questioning tilt
 * - success: Celebration leap, golden star sparkles
 * - error: Concerned tilt, sympathetic recovery aura
 */
const AuraRobot = forwardRef<HTMLDivElement, AuraRobotProps>(function AuraRobot(
  { state, onTap, statusDetail },
  ref
) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      className={`aura-robot-container state-${state} ${hovered ? "is-hovered" : ""}`}
      data-state={state}
      ref={ref}
      onClick={onTap}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      title="AURA — Click to activate voice or speak 'Hey Aura'"
    >
      {/* 1. Holographic Ambient Background Glow */}
      <div className="aura-ambient-glow" />

      {/* 2. Holographic Pedestal / Base Energy Projector */}
      <div className="aura-pedestal">
        <div className="pedestal-ring ring-outer" />
        <div className="pedestal-ring ring-middle" />
        <div className="pedestal-ring ring-inner" />
        <div className="pedestal-core" />
      </div>

      {/* 3. State-Specific Holographic Overlays */}
      {/* Thinking Mode: Orbiting tech rings */}
      <div className="aura-thinking-rings">
        <div className="tech-ring ring-cw" />
        <div className="tech-ring ring-ccw" />
        <span className="glyph glyph-1">◆</span>
        <span className="glyph glyph-2">⚡</span>
        <span className="glyph glyph-3">✦</span>
      </div>

      {/* Working Mode: Holographic Projection Screen */}
      <div className="aura-working-screen">
        <div className="working-screen-glass">
          <div className="working-header">
            <span className="dot dot-red" />
            <span className="dot dot-yellow" />
            <span className="dot dot-green" />
            <span className="working-title">AURA://PROCESS</span>
          </div>
          <div className="working-code-lines">
            <div className="code-line line-1" />
            <div className="code-line line-2" />
            <div className="code-line line-3" />
          </div>
        </div>
      </div>

      {/* Waiting for Permission: Holographic Shield Badge */}
      <div className="aura-shield-badge">
        <div className="shield-icon">🛡️</div>
        <span className="shield-pulse" />
      </div>

      {/* Success Mode: Celebration Sparkles */}
      <div className="aura-sparkles">
        <span className="sparkle s-1">✨</span>
        <span className="sparkle s-2">⭐</span>
        <span className="sparkle s-3">🌟</span>
        <span className="sparkle s-4">✨</span>
      </div>

      {/* Error Mode: Sympathetic Alert Badge */}
      <div className="aura-error-badge">
        <span className="sweat-drop">💧</span>
      </div>

      {/* 4. The Central Robot Body */}
      <div className="aura-character-wrap">
        <img
          src="/aura_robot_transparent.png"
          alt="AURA Robot Companion"
          className="aura-robot-image"
          onError={(e) => {
            // Fallback to original image if transparent fails to load
            (e.target as HTMLImageElement).src = "/aura_robot.png";
          }}
        />

        {/* Antenna Beacon FX (positioned on top antenna sphere) */}
        <div className="aura-antenna-beacon">
          <div className="beacon-dot" />
          <div className="beacon-ring ring-1" />
          <div className="beacon-ring ring-2" />
          <div className="beacon-ring ring-3" />
        </div>

        {/* Cute Natural Eyelid Blink Overlay */}
        <div className="aura-blink-overlay">
          <div className="blink-eye eye-left" />
          <div className="blink-eye eye-right" />
        </div>

        {/* Speaking Audio Wavebar Visualizer */}
        <div className="aura-speech-visualizer">
          <span className="vbar vb-1" />
          <span className="vbar vb-2" />
          <span className="vbar vb-3" />
          <span className="vbar vb-4" />
          <span className="vbar vb-5" />
          <span className="vbar vb-6" />
          <span className="vbar vb-7" />
        </div>
      </div>

      {/* 5. Floating Interactive Status Tag */}
      <div className="aura-floating-status">
        <span className="status-mode-dot" />
        <span className="status-mode-label">
          {state === "idle" && "AURA • READY"}
          {state === "listening" && "LISTENING..."}
          {state === "thinking" && "THINKING..."}
          {state === "speaking" && "SPEAKING..."}
          {state === "working" && "EXECUTING TASK..."}
          {state === "waiting_permission" && "APPROVAL REQUIRED"}
          {state === "success" && "TASK COMPLETE ✨"}
          {state === "error" && "ASSISTANCE READY"}
          {state === "connecting" && "CONNECTING..."}
        </span>
        {statusDetail && <span className="status-mode-detail">{statusDetail}</span>}
      </div>
    </div>
  );
});

export default AuraRobot;
