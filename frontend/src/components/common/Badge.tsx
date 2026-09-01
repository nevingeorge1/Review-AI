import React from 'react';
import { Sparkles, Shield, Cpu, Bug, Zap, Wrench, Palette, Info, AlertTriangle, AlertOctagon } from 'lucide-react';
import { Severity, Category, DetectionSource } from '../../types';

// ─── Severity Badge ─────────────────────────────────────────────────────────

interface SeverityBadgeProps {
  severity: Severity;
  showIcon?: boolean;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, showIcon = true, size = 'sm' }) => {
  const isSm = size === 'sm';
  switch (severity) {
    case 'critical':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md ${
          isSm ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-[12px]'
        } bg-rose-500/15 text-rose-400 border border-rose-500/30`}>
          {showIcon && <AlertOctagon className="w-3 h-3 text-rose-400" />}
          Critical
        </span>
      );
    case 'high':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md ${
          isSm ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-[12px]'
        } bg-amber-500/15 text-amber-400 border border-amber-500/30`}>
          {showIcon && <AlertTriangle className="w-3 h-3 text-amber-400" />}
          High
        </span>
      );
    case 'medium':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md ${
          isSm ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-[12px]'
        } bg-yellow-500/15 text-yellow-400 border border-yellow-500/30`}>
          {showIcon && <Info className="w-3 h-3 text-yellow-400" />}
          Medium
        </span>
      );
    case 'low':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md ${
          isSm ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-[12px]'
        } bg-sky-500/15 text-sky-400 border border-sky-500/30`}>
          Low
        </span>
      );
    case 'info':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md ${
          isSm ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-[12px]'
        } bg-purple-500/15 text-purple-400 border border-purple-500/30`}>
          Info
        </span>
      );
  }
};

// ─── Source & Provenance Badge ───────────────────────────────────────────────

interface SourceBadgeProps {
  source: DetectionSource;
  showIcon?: boolean;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({ source, showIcon = true }) => {
  if (source === 'hybrid') {
    return (
      <span
        title="Corroborated by Deterministic Static Analysis + Local AI Reasoning"
        className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
      >
        {showIcon && <Sparkles className="w-3 h-3 text-cyan-400" />}
        Hybrid (AST + AI)
      </span>
    );
  }

  if (source === 'static_analysis') {
    return (
      <span
        title="Deterministic Static Analysis Evidence (AST / Ruff / Bandit)"
        className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700/60"
      >
        {showIcon && <Shield className="w-3 h-3 text-slate-400" />}
        Static Analysis
      </span>
    );
  }

  return (
    <span
      title="Local LLM Reasoning (Qwen2.5-Coder)"
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium bg-indigo-500/15 text-indigo-300 border border-indigo-500/30"
    >
      {showIcon && <Cpu className="w-3 h-3 text-indigo-400" />}
      Local AI
    </span>
  );
};

// ─── Category Badge ──────────────────────────────────────────────────────────

const CATEGORY_META: Record<Category, { label: string; icon: React.ElementType; color: string }> = {
  security:        { label: 'Security',       icon: Shield, color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
  bug:             { label: 'Reliability',    icon: Bug,    color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  performance:     { label: 'Performance',    icon: Zap,    color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' },
  maintainability: { label: 'Maintainability',icon: Wrench, color: 'text-sky-400 bg-sky-500/10 border-sky-500/20' },
  style:           { label: 'Style',          icon: Palette,color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
};

export const CategoryBadge: React.FC<{ category: Category }> = ({ category }) => {
  const meta = CATEGORY_META[category] || { label: category, icon: Info, color: 'text-slate-400 bg-slate-800 border-slate-700' };
  const Icon = meta.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11.5px] font-medium border ${meta.color}`}>
      <Icon className="w-3 h-3" />
      {meta.label}
    </span>
  );
};

// ─── Letter Grade Badge ──────────────────────────────────────────────────────

export const GradeBadge: React.FC<{ grade: string; size?: 'sm' | 'lg' }> = ({ grade, size = 'sm' }) => {
  const isA = grade.startsWith('A');
  const isB = grade === 'B';
  const isC = grade === 'C';
  const isD = grade === 'D';

  const colorClass = isA
    ? 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30 shadow-[0_0_15px_-3px_rgba(16,185,129,0.3)]'
    : isB
    ? 'text-cyan-400 bg-cyan-500/15 border-cyan-500/30'
    : isC
    ? 'text-yellow-400 bg-yellow-500/15 border-yellow-500/30'
    : isD
    ? 'text-amber-400 bg-amber-500/15 border-amber-500/30'
    : 'text-rose-400 bg-rose-500/15 border-rose-500/30';

  if (size === 'lg') {
    return (
      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center font-bold text-3xl border ${colorClass}`}>
        {grade}
      </div>
    );
  }

  return (
    <span className={`px-2 py-0.5 rounded-md font-bold text-[12px] border ${colorClass}`}>
      {grade}
    </span>
  );
};

// ─── Severity Dot Indicator ──────────────────────────────────────────────────

export const SeverityDot: React.FC<{ severity: Severity; className?: string }> = ({ severity, className = '' }) => {
  const dotColor =
    severity === 'critical' ? 'bg-rose-500 shadow-[0_0_8px_#f43f5e]' :
    severity === 'high'     ? 'bg-amber-500 shadow-[0_0_8px_#f59e0b]' :
    severity === 'medium'   ? 'bg-yellow-500' :
    severity === 'low'      ? 'bg-sky-400' : 'bg-purple-400';

  return <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor} ${className}`} />;
};
