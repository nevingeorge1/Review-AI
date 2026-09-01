import React from 'react';
import {
  Code2,
  History,
  BarChart3,
  BookOpen,
  Settings,
  Sparkles,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Zap,
} from 'lucide-react';
import { clsx } from 'clsx';

export type NavTab = 'workspace' | 'history' | 'analytics' | 'docs' | 'settings';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  reviewCount: number;
  backendConnected: boolean;
}

interface NavItem {
  id: NavTab;
  label: string;
  icon: React.ElementType;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'workspace',  label: 'Code Review',   icon: Sparkles },
  { id: 'history',    label: 'History',       icon: History },
  { id: 'analytics',  label: 'Analytics',     icon: BarChart3 },
  { id: 'docs',       label: 'Rules Engine',  icon: BookOpen },
  { id: 'settings',   label: 'Settings',      icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  reviewCount,
  backendConnected,
}) => {
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <aside
      className={clsx(
        'relative flex flex-col h-full border-r border-white/[0.08] bg-slate-950/95 backdrop-blur-2xl transition-all duration-300 flex-shrink-0 select-none z-30',
        collapsed ? 'w-[68px]' : 'w-[240px]'
      )}
    >
      {/* Brand Header */}
      <div className={clsx(
        'flex items-center h-[64px] border-b border-white/[0.06] flex-shrink-0',
        collapsed ? 'justify-center px-2' : 'px-5 gap-3'
      )}>
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-glow-subtle border border-white/20">
          <Code2 className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="text-[15px] font-bold tracking-tight text-white">
                Review<span className="text-cyan-400">AI</span>
              </span>
            </div>
            <p className="text-[11px] font-medium text-slate-400 truncate">
              Code Intelligence
            </p>
          </div>
        )}
      </div>

      {/* Navigation Group */}
      <nav className="flex-1 py-4 px-2.5 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              title={collapsed ? item.label : undefined}
              className={clsx(
                'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-[13.5px] transition-all duration-150 cursor-pointer text-left',
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/15 to-blue-500/10 text-cyan-400 font-semibold border border-cyan-500/25 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] font-medium border border-transparent',
                collapsed && 'justify-center px-0'
              )}
            >
              <Icon className={clsx('w-4 h-4 flex-shrink-0', isActive ? 'text-cyan-400' : 'text-slate-400')} />
              {!collapsed && (
                <>
                  <span className="flex-1 truncate">{item.label}</span>
                  {item.id === 'history' && reviewCount > 0 && (
                    <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-950/80 text-cyan-400 border border-cyan-500/30">
                      {reviewCount}
                    </span>
                  )}
                </>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom Minimal System Status */}
      {!collapsed && (
        <div className="p-4 border-t border-white/[0.06] space-y-2.5">
          <div className="flex items-center justify-between text-[11px] font-medium">
            <span className="text-slate-400">System Status</span>
            <div className="flex items-center gap-1.5">
              <span className={clsx('w-2 h-2 rounded-full', backendConnected ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-rose-500')} />
              <span className={backendConnected ? 'text-emerald-400' : 'text-rose-400'}>
                {backendConnected ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.06] space-y-1.5 text-[11.5px]">
            <div className="flex items-center justify-between text-slate-300">
              <span className="flex items-center gap-1.5 text-slate-400">
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" /> Static Engine
              </span>
              <span className="font-semibold text-emerald-400">15 Rules</span>
            </div>
            <div className="flex items-center justify-between text-slate-300">
              <span className="flex items-center gap-1.5 text-slate-400">
                <Zap className="w-3.5 h-3.5 text-indigo-400" /> Local AI
              </span>
              <span className="font-semibold text-indigo-300 truncate max-w-[80px]">Qwen2.5</span>
            </div>
          </div>
        </div>
      )}

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-[76px] w-6 h-6 rounded-full bg-slate-900 border border-white/20 flex items-center justify-center text-slate-400 hover:text-white hover:border-cyan-400 transition-colors shadow-md z-40 cursor-pointer"
        title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
      >
        {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>
    </aside>
  );
};
