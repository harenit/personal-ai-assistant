import React from 'react';

export function StatusBadge({ status, size = 'sm' }) {
  const norm = (status || '').toUpperCase();

  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';

  if (norm === 'LOW_RISK' || norm === 'COMPLETED' || norm === 'SUCCESS' || norm === 'GRADED' || norm === 'APPROVED') {
    colorClasses = 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60';
  } else if (norm === 'SENSITIVE' || norm === 'PENDING' || norm === 'WAITING_FOR_PERMISSION' || norm === 'URGENT') {
    colorClasses = 'bg-amber-950/80 text-amber-400 border-amber-800/60 animate-pulse';
  } else if (norm === 'DENIED' || norm === 'FAILED' || norm === 'ERROR' || norm === 'OVERDUE') {
    colorClasses = 'bg-rose-950/80 text-rose-400 border-rose-800/60';
  } else if (norm === 'PLANNING' || norm === 'EXECUTING' || norm === 'RUNNING') {
    colorClasses = 'bg-cyan-950/80 text-cyan-400 border-cyan-800/60';
  }

  const sizeClasses = size === 'xs' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span className={`inline-flex items-center gap-1 font-mono font-medium rounded-full border ${colorClasses} ${sizeClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}
