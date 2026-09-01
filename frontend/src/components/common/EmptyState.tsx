import React from 'react';
import { CODE_SAMPLES } from '../../data/samples';
import { ShieldAlert, Bug, Zap, CheckCircle2, ArrowRight, Sparkles } from 'lucide-react';

interface EmptyStateProps {
  onSelectSample: (sampleId: string) => void;
}

const SAMPLE_ICONS = [ShieldAlert, Bug, Zap, CheckCircle2];
const SAMPLE_COLORS = ['text-rose-400 bg-rose-500/10 border-rose-500/20', 'text-amber-400 bg-amber-500/10 border-amber-500/20', 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20', 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'];

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectSample }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center select-none animate-fade-in overflow-y-auto">
      {/* Abstract Animated AST Tree Illustration */}
      <div className="relative mb-6 w-36 h-20 flex items-center justify-center">
        <svg viewBox="0 0 140 80" className="w-full h-full stroke-cyan-500/30 fill-none" strokeWidth="1.5">
          <line x1="70" y1="12" x2="35" y2="45" strokeDasharray="3 3" />
          <line x1="70" y1="12" x2="105" y2="45" strokeDasharray="3 3" />
          <line x1="35" y1="45" x2="18" y2="68" />
          <line x1="35" y1="45" x2="52" y2="68" />
          <line x1="105" y1="45" x2="122" y2="68" />

          {/* Root node */}
          <circle cx="70" cy="12" r="5" className="fill-cyan-400 stroke-cyan-200" />
          {/* Branch nodes */}
          <circle cx="35" cy="45" r="4" className="fill-blue-500 stroke-blue-300" />
          <circle cx="105" cy="45" r="4" className="fill-indigo-500 stroke-indigo-300" />
          {/* Leaf nodes */}
          <circle cx="18" cy="68" r="3" className="fill-emerald-400" />
          <circle cx="52" cy="68" r="3" className="fill-yellow-400" />
          <circle cx="122" cy="68" r="3" className="fill-rose-400" />
        </svg>
      </div>

      {/* Hero Content */}
      <div className="space-y-2 mb-8 max-w-md">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/25">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI Code Intelligence</span>
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Inspect code before production.
        </h2>
        <p className="text-[14px] text-slate-400 leading-relaxed">
          Paste your code or select a demo sample to detect security vulnerabilities, bugs, and performance bottlenecks.
        </p>
      </div>

      {/* Quick Launch Demo Cards */}
      <div className="w-full max-w-md space-y-2.5 text-left">
        <p className="text-[12px] font-semibold uppercase tracking-wider text-slate-400 px-1">
          Try a Benchmark Scenario
        </p>

        {CODE_SAMPLES.map((sample, idx) => {
          const Icon = SAMPLE_ICONS[idx] || ShieldAlert;
          const colorClass = SAMPLE_COLORS[idx] || 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20';

          return (
            <button
              key={sample.id}
              onClick={() => onSelectSample(sample.id)}
              className="w-full flex items-center gap-3.5 p-3 rounded-xl border border-white/[0.08] bg-slate-900/60 hover:bg-slate-850 hover:border-cyan-500/40 transition-all duration-200 group text-left cursor-pointer shadow-sm"
            >
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center border flex-shrink-0 ${colorClass}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-[13.5px] font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors">
                    {sample.name}
                  </span>
                  <span className="text-[11.5px] font-mono text-slate-400">
                    {sample.filename}
                  </span>
                </div>
                <p className="text-[12px] text-slate-400 truncate mt-0.5 font-normal">
                  {sample.description}
                </p>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all flex-shrink-0" />
            </button>
          );
        })}
      </div>
    </div>
  );
};
