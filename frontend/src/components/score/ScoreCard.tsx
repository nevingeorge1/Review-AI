import React, { useState } from 'react';
import { QualityScore, ReviewSummary, Category } from '../../types';
import { GradeBadge } from '../common/Badge';
import {
  ShieldAlert,
  Bug,
  Zap,
  Wrench,
  Palette,
  AlertTriangle,
  Clock,
  HelpCircle,
  Activity,
} from 'lucide-react';

interface ScoreCardProps {
  score: QualityScore;
  summary: ReviewSummary;
  durationMs?: number;
  onSelectCategory?: (category: Category) => void;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ score, summary, durationMs, onSelectCategory }) => {
  const [showFormula, setShowFormula] = useState(false);

  const overall = score.overall_score;
  const grade = score.grade;

  // Arc calculation for radial gauge
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (overall / 100) * circumference;

  const scoreColor =
    overall >= 80 ? 'text-emerald-400 stroke-emerald-400' :
    overall >= 60 ? 'text-cyan-400 stroke-cyan-400' :
    overall >= 40 ? 'text-yellow-400 stroke-yellow-400' : 'text-rose-400 stroke-rose-400';

  return (
    <div className="space-y-4 select-none animate-fade-in">
      {/* Radial Health Card */}
      <div className="glass-card p-5 relative overflow-hidden">
        <div className="flex flex-col sm:flex-row items-center gap-5">
          {/* Radial Arc */}
          <div className="relative w-28 h-28 flex items-center justify-center flex-shrink-0">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="50"
                cy="50"
                r={radius}
                className={`${scoreColor} transition-all duration-1000 ease-out`}
                strokeWidth="8"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="none"
              />
            </svg>

            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className={`text-3xl font-bold tracking-tight leading-none ${scoreColor}`}>
                {overall.toFixed(0)}
              </span>
              <span className="text-[11px] font-medium text-slate-400 mt-1">/ 100</span>
            </div>
          </div>

          {/* Health Verdict & Overview */}
          <div className="min-w-0 flex-1 space-y-2 text-center sm:text-left">
            <div className="flex items-center justify-center sm:justify-start gap-2.5">
              <GradeBadge grade={grade} size="sm" />
              <h3 className="text-lg font-bold text-white tracking-tight">
                Code Health
              </h3>
            </div>

            <p className="text-[13px] text-slate-300 leading-relaxed font-normal">
              {overall >= 80
                ? 'High quality codebase. Low vulnerability footprint and clean design.'
                : overall >= 60
                ? 'Moderate issues detected. Recommended refactor of high severity items.'
                : 'Action required. Critical security or reliability issues found.'}
            </p>

            {durationMs != null && (
              <div className="flex items-center justify-center sm:justify-start gap-1.5 text-[12px] font-medium text-slate-400">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>Analyzed in {(durationMs / 1000).toFixed(2)}s</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Metric Tiles Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className={`p-3 rounded-xl border ${summary.critical_count > 0 ? 'bg-rose-500/10 border-rose-500/30' : 'bg-slate-900/60 border-white/[0.06]'}`}>
          <div className="flex items-center justify-between text-[11.5px] font-medium text-slate-400 mb-1">
            <span>Critical</span>
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <p className={`text-2xl font-bold ${summary.critical_count > 0 ? 'text-rose-400' : 'text-slate-200'}`}>
            {summary.critical_count}
          </p>
        </div>

        <div className={`p-3 rounded-xl border ${summary.high_count > 0 ? 'bg-amber-500/10 border-amber-500/30' : 'bg-slate-900/60 border-white/[0.06]'}`}>
          <div className="flex items-center justify-between text-[11.5px] font-medium text-slate-400 mb-1">
            <span>High Risk</span>
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <p className={`text-2xl font-bold ${summary.high_count > 0 ? 'text-amber-400' : 'text-slate-200'}`}>
            {summary.high_count}
          </p>
        </div>

        <div className="p-3 rounded-xl border bg-slate-900/60 border-white/[0.06]">
          <div className="flex items-center justify-between text-[11.5px] font-medium text-slate-400 mb-1">
            <span>Medium</span>
            <Bug className="w-3.5 h-3.5 text-yellow-400" />
          </div>
          <p className="text-2xl font-bold text-slate-200">
            {summary.medium_count}
          </p>
        </div>

        <div className="p-3 rounded-xl border bg-slate-900/60 border-white/[0.06]">
          <div className="flex items-center justify-between text-[11.5px] font-medium text-slate-400 mb-1">
            <span>Total Issues</span>
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-cyan-300">
            {summary.total_findings}
          </p>
        </div>
      </div>

      {/* Category Sub-Scores Breakdown */}
      <div className="glass-card p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-[13px] font-semibold text-slate-200">Category Breakdown</span>
          <button
            onClick={() => setShowFormula(f => !f)}
            className="text-[11.5px] font-medium text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
          >
            <HelpCircle className="w-3 h-3" />
            <span>{showFormula ? 'Hide Formula' : 'Calculation Info'}</span>
          </button>
        </div>

        <div className="space-y-2.5 text-[12.5px]">
          {/* Security (30%) */}
          <div
            onClick={() => onSelectCategory && onSelectCategory('security')}
            className="space-y-1 cursor-pointer group"
          >
            <div className="flex justify-between font-medium">
              <span className="text-slate-300 flex items-center gap-2 group-hover:text-cyan-400 transition-colors">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-400" /> Security
              </span>
              <span className="text-slate-400 font-semibold">{score.security_score.toFixed(0)} <span className="text-slate-400 font-normal">/ 100 (30% wt)</span></span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div className="h-full bg-rose-500 rounded-full transition-all duration-700" style={{ width: `${score.security_score}%` }} />
            </div>
          </div>

          {/* Reliability (30%) */}
          <div
            onClick={() => onSelectCategory && onSelectCategory('bug')}
            className="space-y-1 cursor-pointer group"
          >
            <div className="flex justify-between font-medium">
              <span className="text-slate-300 flex items-center gap-2 group-hover:text-cyan-400 transition-colors">
                <Bug className="w-3.5 h-3.5 text-amber-400" /> Reliability
              </span>
              <span className="text-slate-400 font-semibold">{score.reliability_score.toFixed(0)} <span className="text-slate-400 font-normal">/ 100 (30% wt)</span></span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full transition-all duration-700" style={{ width: `${score.reliability_score}%` }} />
            </div>
          </div>

          {/* Maintainability (20%) */}
          <div
            onClick={() => onSelectCategory && onSelectCategory('maintainability')}
            className="space-y-1 cursor-pointer group"
          >
            <div className="flex justify-between font-medium">
              <span className="text-slate-300 flex items-center gap-2 group-hover:text-cyan-400 transition-colors">
                <Wrench className="w-3.5 h-3.5 text-sky-400" /> Maintainability
              </span>
              <span className="text-slate-400 font-semibold">{score.maintainability_score.toFixed(0)} <span className="text-slate-400 font-normal">/ 100 (20% wt)</span></span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div className="h-full bg-sky-500 rounded-full transition-all duration-700" style={{ width: `${score.maintainability_score}%` }} />
            </div>
          </div>

          {/* Performance (10%) */}
          <div
            onClick={() => onSelectCategory && onSelectCategory('performance')}
            className="space-y-1 cursor-pointer group"
          >
            <div className="flex justify-between font-medium">
              <span className="text-slate-300 flex items-center gap-2 group-hover:text-cyan-400 transition-colors">
                <Zap className="w-3.5 h-3.5 text-yellow-400" /> Performance
              </span>
              <span className="text-slate-400 font-semibold">{score.performance_score.toFixed(0)} <span className="text-slate-400 font-normal">/ 100 (10% wt)</span></span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div className="h-full bg-yellow-500 rounded-full transition-all duration-700" style={{ width: `${score.performance_score}%` }} />
            </div>
          </div>

          {/* Style (10%) */}
          <div
            onClick={() => onSelectCategory && onSelectCategory('style')}
            className="space-y-1 cursor-pointer group"
          >
            <div className="flex justify-between font-medium">
              <span className="text-slate-300 flex items-center gap-2 group-hover:text-cyan-400 transition-colors">
                <Palette className="w-3.5 h-3.5 text-purple-400" /> Style
              </span>
              <span className="text-slate-400 font-semibold">{score.style_score.toFixed(0)} <span className="text-slate-400 font-normal">/ 100 (10% wt)</span></span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div className="h-full bg-purple-500 rounded-full transition-all duration-700" style={{ width: `${score.style_score}%` }} />
            </div>
          </div>
        </div>

        {/* Expandable Mathematical Formula Info */}
        {showFormula && (
          <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.08] text-[12px] text-slate-300 space-y-2 animate-fade-in">
            <p className="font-semibold text-cyan-300">
              Deterministic Quality Scoring Model
            </p>
            <p className="text-slate-400 leading-relaxed font-normal">
              Scores start at 100 with deduction penalties: Critical (-25), High (-15), Medium (-8), Low (-3).
            </p>
            <p className="text-[11px] text-slate-400 font-mono bg-white/[0.03] p-2 rounded border border-white/[0.06]">
              Overall = 0.30×Security + 0.30×Reliability + 0.20×Maintainability + 0.10×Performance + 0.10×Style
            </p>
          </div>
        )}
      </div>

      {/* Executive Summary Banner */}
      {summary.executive_summary && (
        <div className="glass-card p-4 space-y-1.5">
          <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider">Executive Summary</span>
          <p className="text-[13px] text-slate-200 leading-relaxed font-normal">
            {summary.executive_summary}
          </p>
        </div>
      )}
    </div>
  );
};
