import React, { useState, useEffect } from 'react';
import { ShieldCheck, Check, Brain } from 'lucide-react';

interface LoadingProgressProps {
  filename: string;
}

export const LoadingProgress: React.FC<LoadingProgressProps> = ({ filename }) => {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setSeconds(s => s + 0.2), 200);
    return () => clearInterval(timer);
  }, []);

  const stages = [
    {
      label: 'Parsing code & building AST structure',
      sub: 'Tokenizing source and analyzing decision branches',
      done: seconds > 0.8,
      active: seconds <= 0.8,
    },
    {
      label: 'Running deterministic static analysis',
      sub: 'Executing 15 AST rules, Ruff linter, and Bandit security scans',
      done: seconds > 2.0,
      active: seconds > 0.8 && seconds <= 2.0,
    },
    {
      label: 'Consulting local AI reasoning engine',
      sub: 'Evaluating semantic context with Qwen2.5-Coder via Ollama',
      done: seconds > 5.5,
      active: seconds > 2.0 && seconds <= 5.5,
    },
    {
      label: 'Fusing findings & scoring code quality',
      sub: 'Corroborating multi-tool evidence and generating actionable fixes',
      done: false,
      active: seconds > 5.5,
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center select-none animate-fade-in relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute w-72 h-72 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none -top-10" />

      {/* Modern Gradient Animated Loader */}
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-[2px] shadow-glow-brand animate-pulse-slow">
          <div className="w-full h-full rounded-[14px] bg-slate-950 flex items-center justify-center">
            <Brain className="w-7 h-7 text-cyan-400 animate-pulse" />
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="mb-8 space-y-1.5">
        <h3 className="text-xl font-bold text-white tracking-tight">
          Reviewing {filename}
        </h3>
        <p className="text-[13.5px] text-slate-400">
          Running hybrid static analysis and local AI code intelligence
        </p>
      </div>

      {/* Modern Stage Progression Cards */}
      <div className="w-full max-w-md space-y-2.5 text-left">
        {stages.map((stage, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-xl border transition-all duration-300 ${
              stage.active
                ? 'bg-slate-850 border-cyan-500/40 shadow-glow-subtle'
                : stage.done
                ? 'bg-slate-900/40 border-white/[0.04]'
                : 'bg-transparent border-transparent opacity-40'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex-shrink-0">
                {stage.done ? (
                  <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                ) : stage.active ? (
                  <div className="w-5 h-5 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  </div>
                ) : (
                  <div className="w-5 h-5 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-semibold text-slate-400">
                    {idx + 1}
                  </div>
                )}
              </div>

              <div className="min-w-0 flex-1">
                <p className={`text-[13px] font-semibold leading-snug ${
                  stage.done ? 'text-slate-400 line-through' :
                  stage.active ? 'text-white' : 'text-slate-400'
                }`}>
                  {stage.label}
                </p>
                <p className="text-[11.5px] text-slate-400 mt-0.5 truncate">
                  {stage.sub}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Safety & Privacy Notice */}
      <div className="mt-8 flex items-center gap-2 text-[12px] font-medium text-slate-400">
        <ShieldCheck className="w-4 h-4 text-emerald-400" />
        <span>100% on-device privacy — code is never transmitted to external cloud APIs</span>
      </div>
    </div>
  );
};
