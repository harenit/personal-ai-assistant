import React, { useState } from 'react';
import { 
  CheckCircle, PlayCircle, Wrench, ShieldAlert, Sparkles, ChevronDown, ChevronRight, Clock
} from 'lucide-react';

export function ToolActivityTimeline({ steps = [] }) {
  const [expandedSteps, setExpandedSteps] = useState({});

  if (!steps || steps.length === 0) return null;

  const toggleExpand = (idx) => {
    setExpandedSteps(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const getStepIcon = (actionType) => {
    switch (actionType) {
      case 'plan':
        return <Sparkles className="w-3.5 h-3.5 text-cyan-400" />;
      case 'tool_select':
      case 'tool_result':
        return <Wrench className="w-3.5 h-3.5 text-sky-400" />;
      case 'permission_request':
        return <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />;
      case 'final_response':
        return <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />;
      default:
        return <PlayCircle className="w-3.5 h-3.5 text-indigo-400" />;
    }
  };

  return (
    <div className="my-3 p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800 text-xs font-semibold text-slate-300">
        <span className="flex items-center gap-1.5 font-mono">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          Autonomous Execution Trace
        </span>
        <span className="text-[11px] text-slate-500 font-mono">
          {steps.length} {steps.length === 1 ? 'step' : 'steps'}
        </span>
      </div>

      <div className="relative pl-6 space-y-3 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {steps.map((step, idx) => {
          const hasDetails = step.result || (step.arguments && Object.keys(step.arguments).length > 0);
          const isExpanded = !!expandedSteps[idx];

          return (
            <div key={idx} className="relative group text-xs">
              {/* Dot Icon */}
              <div className="absolute -left-6 top-0.5 flex items-center justify-center w-5 h-5 rounded-full bg-slate-900 border border-slate-700 shadow-sm">
                {getStepIcon(step.action_type)}
              </div>

              {/* Step Summary */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-200">
                      {step.status_message}
                    </span>
                    {step.tool_name && (
                      <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-sky-950/80 text-sky-400 border border-sky-800/50">
                        {step.tool_name}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-1 text-[10px] text-slate-500 font-mono shrink-0">
                  <Clock className="w-3 h-3" />
                  {step.timestamp}
                  {hasDetails && (
                    <button
                      onClick={() => toggleExpand(idx)}
                      className="p-1 hover:text-slate-300 text-slate-500 transition ml-1"
                    >
                      {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                    </button>
                  )}
                </div>
              </div>

              {/* Expandable Parameters / Observation */}
              {isExpanded && hasDetails && (
                <div className="mt-2 p-2.5 rounded-lg bg-black/60 border border-slate-800/70 text-[11px] font-mono text-slate-300 space-y-1.5 overflow-x-auto">
                  {step.arguments && Object.keys(step.arguments).length > 0 && (
                    <div>
                      <span className="text-slate-500 font-bold block">Inputs:</span>
                      <pre className="text-slate-300 whitespace-pre-wrap">{JSON.stringify(step.arguments, null, 2)}</pre>
                    </div>
                  )}
                  {step.result && (
                    <div>
                      <span className="text-slate-500 font-bold block">Observation:</span>
                      <pre className="text-cyan-300/90 whitespace-pre-wrap">{JSON.stringify(step.result, null, 2)}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
