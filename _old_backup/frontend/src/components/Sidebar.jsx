import React from 'react';
import {
  LayoutDashboard,
  MessageSquare,
  BookOpen,
  GraduationCap,
  Bell,
  FileText,
  Presentation,
  CheckSquare,
  Mail,
  Calendar,
  Activity,
  Settings,
  Sparkles,
  Cpu
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'chat', label: 'Chat Agent', icon: MessageSquare, badge: 'AI' },
  { id: 'assignments', label: 'Assignments', icon: BookOpen },
  { id: 'exams', label: 'Exams', icon: GraduationCap },
  { id: 'announcements', label: 'Announcements', icon: Bell },
  { id: 'study', label: 'Study Materials', icon: FileText },
  { id: 'presentations', label: 'Presentations', icon: Presentation },
  { id: 'reminders', label: 'Reminders', icon: CheckSquare },
  { id: 'email', label: 'Email', icon: Mail },
  { id: 'calendar', label: 'Calendar', icon: Calendar },
  { id: 'activity', label: 'Activity Log', icon: Activity },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ currentTab, onSelectTab, pendingPermissionsCount = 0 }) {
  return (
    <aside className="w-64 bg-[#0D121D] border-r border-slate-800/80 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/70 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-sky-400 to-indigo-500 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-base font-extrabold tracking-wider text-white">JARVIS</h1>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/50">v1.0</span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Autonomous Student Agent</p>
          </div>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          const isChat = item.id === 'chat';
          const hasBadge = isChat && pendingPermissionsCount > 0;

          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 group ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/20 to-sky-500/10 text-cyan-300 border border-cyan-500/30 shadow-md shadow-cyan-950/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850/60 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                <span>{item.label}</span>
              </div>

              {hasBadge && (
                <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded-full bg-amber-500 text-black animate-bounce">
                  {pendingPermissionsCount}
                </span>
              )}

              {!hasBadge && item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] font-mono font-bold rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Student Profile Footer */}
      <div className="p-4 border-t border-slate-800/70 bg-slate-950/40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-cyan-400">
            AR
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-xs font-bold text-white truncate">Alex Rivers</h4>
            <p className="text-[10px] text-slate-400 truncate">CS & AI • Fall 2026</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
