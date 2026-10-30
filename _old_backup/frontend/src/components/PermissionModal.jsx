import React from 'react';
import { ShieldAlert, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function PermissionModal({ permissionRequest, onApprove, onDeny }) {
  if (!permissionRequest) return null;

  let parsedParams = {};
  if (typeof permissionRequest.parameters === 'string') {
    try {
      parsedParams = JSON.parse(permissionRequest.parameters);
    } catch {
      parsedParams = { raw: permissionRequest.parameters };
    }
  } else {
    parsedParams = permissionRequest.parameters || {};
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-lg overflow-hidden bg-[#111622] border border-amber-500/40 rounded-2xl shadow-2xl shadow-amber-950/40">
        
        {/* Header */}
        <div className="flex items-center gap-3 px-6 py-4 bg-gradient-to-r from-amber-950/40 via-amber-900/20 to-transparent border-b border-amber-500/20">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white tracking-wide">
                Security Authorization Required
              </h3>
              <StatusBadge status="SENSITIVE" size="xs" />
            </div>
            <p className="text-xs text-amber-300/80">
              JARVIS is requesting permission to execute an external action.
            </p>
          </div>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-4">
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
              Requested Tool Action
            </span>
            <span className="text-sm font-semibold font-mono text-cyan-400">
              {permissionRequest.tool_name}
            </span>
          </div>

          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block mb-1.5">
              Action Parameters
            </span>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs font-mono text-slate-300 max-h-48 overflow-y-auto space-y-1">
              {Object.entries(parsedParams).map(([k, v]) => (
                <div key={k} className="flex flex-col sm:flex-row sm:gap-2 border-b border-slate-800/50 pb-1 last:border-0 last:pb-0">
                  <span className="text-slate-400 font-semibold">{k}:</span>
                  <span className="text-slate-200 break-words">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                </div>
              ))}
            </div>
          </div>

          {permissionRequest.reason && (
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs text-amber-200/90">
              <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
              <span>{permissionRequest.reason}</span>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 bg-slate-950/60 border-t border-slate-800">
          <button
            onClick={() => onDeny(permissionRequest.id)}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-rose-300 hover:text-white bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/60 rounded-xl transition duration-150"
          >
            <XCircle className="w-4 h-4" />
            Deny
          </button>
          <button
            onClick={() => onApprove(permissionRequest.id)}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-black bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 rounded-xl shadow-lg shadow-emerald-500/20 transition duration-150 font-bold"
          >
            <CheckCircle2 className="w-4 h-4" />
            Allow Execution
          </button>
        </div>
      </div>
    </div>
  );
}
