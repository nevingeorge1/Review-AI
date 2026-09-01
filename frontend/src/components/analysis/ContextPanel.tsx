import React from 'react';
import { Language, ReviewResponse } from '../../types';
import {
  FileCode2,
  Cpu,
  Layers,
  Activity,
  Terminal,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

interface ContextPanelProps {
  filename: string;
  language: Language;
  code: string;
  activeReview?: ReviewResponse;
}

export const ContextPanel: React.FC<ContextPanelProps> = ({
  filename,
  language,
  code,
  activeReview,
}) => {
  const lineCount = code ? code.split('\n').length : 0;
  const byteSize = new Blob([code]).size;

  // Real or deterministic AST approximation metrics based on actual code
  const functionCount = (code.match(/def\s+[a-zA-Z_]/g) || []).length;
  const classCount = (code.match(/class\s+[a-zA-Z_]/g) || []).length;
  const importCount = (code.match(/import\s+[a-zA-Z_]|from\s+[a-zA-Z_]/g) || []).length;
  
  // Calculate max indentation depth
  const lines = code.split('\n');
  let maxNesting = 0;
  lines.forEach(l => {
    const match = l.match(/^(\s+)/);
    if (match) {
      const depth = Math.floor(match[1].length / 4);
      if (depth > maxNesting) maxNesting = depth;
    }
  });

  const reviewMode = activeReview?.summary?.review_mode || (activeReview?.metadata?.review_mode) || 'HYBRID';
  const durationMs = activeReview?.metadata?.total_duration_ms;
  const analysisId = activeReview?.analysis_id || activeReview?.review_id;

  return (
    <div className="h-full flex flex-col font-mono text-[11px] bg-dark-950 border-r border-dark-600 select-none overflow-y-auto">
      {/* Panel Header */}
      <div className="p-3 border-b border-dark-600 flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-cyan-electric">
          <Terminal className="w-3.5 h-3.5" />
          <span className="font-bold uppercase tracking-wider text-[10.5px]">CODE CONTEXT</span>
        </div>
        <span className="px-1.5 py-0.2 rounded text-[8.5px] font-bold uppercase bg-dark-800 text-slate-400 border border-dark-700">
          AST v3
        </span>
      </div>

      <div className="p-3 space-y-4">
        {/* SECTION 1: TARGET FILE */}
        <div className="space-y-1.5">
          <span className="telemetry-label flex items-center justify-between text-slate-400">
            <span>TARGET FILE</span>
            <FileCode2 className="w-3 h-3 text-slate-400" />
          </span>
          <div className="p-2 rounded bg-dark-900 border border-dark-700 space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">NAME</span>
              <span className="text-slate-200 font-semibold truncate max-w-[100px]">{filename}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">LANG</span>
              <span className="text-cyan-300 font-semibold uppercase">{language}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">LINES</span>
              <span className="text-slate-200">{lineCount}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">SIZE</span>
              <span className="text-slate-200">{(byteSize / 1024).toFixed(1)} KB</span>
            </div>
          </div>
        </div>

        {/* SECTION 2: AST STRUCTURE METRICS */}
        <div className="space-y-1.5">
          <span className="telemetry-label flex items-center justify-between text-slate-400">
            <span>AST TOPOLOGY</span>
            <Layers className="w-3 h-3 text-slate-400" />
          </span>
          <div className="p-2 rounded bg-dark-900 border border-dark-700 space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">FUNCTIONS</span>
              <span className="text-emerald-400 font-semibold">{functionCount}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">CLASSES</span>
              <span className="text-cyan-300 font-semibold">{classCount}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">IMPORTS</span>
              <span className="text-slate-200">{importCount}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">MAX NESTING</span>
              <span className={maxNesting > 4 ? 'text-orange-400 font-bold' : 'text-slate-200'}>
                {maxNesting} {maxNesting > 4 ? '⚠' : ''}
              </span>
            </div>
          </div>
        </div>

        {/* SECTION 3: ENGINES EXECUTED */}
        <div className="space-y-1.5">
          <span className="telemetry-label flex items-center justify-between text-slate-400">
            <span>ENGINES ENGAGED</span>
            <Cpu className="w-3 h-3 text-slate-400" />
          </span>
          <div className="p-2 rounded bg-dark-900 border border-dark-700 space-y-1 text-[10px]">
            <div className="flex items-center gap-1.5 text-emerald-400">
              <CheckCircle2 className="w-3 h-3 flex-shrink-0" />
              <span>15 AST Rules Engine</span>
            </div>
            <div className="flex items-center gap-1.5 text-emerald-400">
              <CheckCircle2 className="w-3 h-3 flex-shrink-0" />
              <span>Ruff Subprocess Linter</span>
            </div>
            <div className="flex items-center gap-1.5 text-emerald-400">
              <CheckCircle2 className="w-3 h-3 flex-shrink-0" />
              <span>Bandit Security Engine</span>
            </div>
            <div className="flex items-center gap-1.5 text-cyan-300">
              <Sparkles className="w-3 h-3 flex-shrink-0" />
              <span>Qwen2.5-Coder (Ollama)</span>
            </div>
          </div>
        </div>

        {/* SECTION 4: REVIEW RUN TELEMETRY */}
        {activeReview && (
          <div className="space-y-1.5 animate-fade-in">
            <span className="telemetry-label flex items-center justify-between text-slate-400">
              <span>RUN TELEMETRY</span>
              <Activity className="w-3 h-3 text-slate-400" />
            </span>
            <div className="p-2 rounded bg-dark-900 border border-dark-700 space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">MODE</span>
                <span className="text-cyan-electric font-semibold">{reviewMode}</span>
              </div>
              {durationMs != null && (
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">LATENCY</span>
                  <span className="text-slate-200">{(durationMs / 1000).toFixed(2)}s</span>
                </div>
              )}
              {analysisId && (
                <div className="flex justify-between items-center pt-0.5 border-t border-dark-800">
                  <span className="text-slate-400">REQ ID</span>
                  <span className="text-slate-400 text-[9px] truncate max-w-[85px]">
                    {analysisId}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
