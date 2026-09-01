import React from 'react';
import { Sparkles, Shield, RotateCcw, ChevronDown } from 'lucide-react';
import { CODE_SAMPLES } from '../../data/samples';

interface HeaderProps {
  pageTitle: string;
  pageSubtitle?: string;
  reviewMode?: string;
  onNewReview?: () => void;
  onLoadSample?: (id: string) => void;
  latencyMs?: number;
  rightContent?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  pageTitle,
  pageSubtitle,
  reviewMode,
  onNewReview,
  onLoadSample,
  latencyMs,
  rightContent,
}) => {
  return (
    <header className="h-[64px] flex-shrink-0 flex items-center justify-between px-6 border-b border-white/[0.06] bg-slate-950/60 backdrop-blur-xl select-none z-20">
      {/* Left: Page Title & Context */}
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-[17px] font-bold text-white tracking-tight leading-none">
            {pageTitle}
          </h1>
          {pageSubtitle && (
            <p className="text-[12.5px] text-slate-400 mt-1 font-medium leading-none">
              {pageSubtitle}
            </p>
          )}
        </div>

        {/* Mode Status Pill */}
        {reviewMode && (
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/25">
            {reviewMode === 'HYBRID' ? (
              <>
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Hybrid Intelligence</span>
              </>
            ) : (
              <>
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                <span>Static Analysis Only</span>
              </>
            )}
          </div>
        )}
      </div>

      {/* Right: Actions & Sample Selectors */}
      <div className="flex items-center gap-3">
        {latencyMs != null && (
          <span className="hidden md:inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11.5px] font-mono text-slate-400 bg-white/[0.04] border border-white/[0.06]">
            <span>Latency:</span>
            <span className="text-cyan-400 font-semibold">{(latencyMs / 1000).toFixed(2)}s</span>
          </span>
        )}

        {/* Quick Sample Selector */}
        {onLoadSample && (
          <div className="relative">
            <select
              onChange={e => {
                if (e.target.value) {
                  onLoadSample(e.target.value);
                  e.target.value = '';
                }
              }}
              defaultValue=""
              className="appearance-none px-3.5 py-1.5 pr-8 rounded-lg bg-white/[0.05] border border-white/[0.1] text-[12.5px] font-medium text-slate-200 hover:bg-white/[0.08] hover:border-cyan-500/40 focus:outline-none focus:border-cyan-400 transition-all cursor-pointer"
            >
              <option value="" disabled>Load Demo Sample...</option>
              {CODE_SAMPLES.map(s => (
                <option key={s.id} value={s.id} className="bg-slate-900 text-white">
                  {s.name} ({s.filename})
                </option>
              ))}
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        )}

        {/* Reset / New Review */}
        {onNewReview && (
          <button
            onClick={onNewReview}
            className="btn-secondary-modern"
            title="Reset workspace"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
            <span>Reset</span>
          </button>
        )}

        {rightContent}
      </div>
    </header>
  );
};
