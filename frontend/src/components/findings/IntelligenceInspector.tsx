import React, { useState } from 'react';
import { ReviewFinding } from '../../types';
import { SeverityBadge, SourceBadge, CategoryBadge } from '../common/Badge';
import { toast } from '../common/ErrorBanner';
import {
  MapPin,
  Copy,
  Check,
  ExternalLink,
  Code2,
  CheckCircle2,
  X,
  Brain,
  Lightbulb,
} from 'lucide-react';

interface IntelligenceInspectorProps {
  finding?: ReviewFinding;
  onClose?: () => void;
  onJumpToLine?: (line: number, endLine?: number) => void;
}

export const IntelligenceInspector: React.FC<IntelligenceInspectorProps> = ({
  finding,
  onClose,
  onJumpToLine,
}) => {
  const [copied, setCopied] = useState(false);
  const [diffMode, setDiffMode] = useState<'unified' | 'clean'>('unified');

  if (!finding) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center select-none text-slate-400">
        <Code2 className="w-10 h-10 text-slate-400 mb-3" />
        <h4 className="text-[14px] font-semibold text-slate-300">No issue selected</h4>
        <p className="text-[12.5px] text-slate-400 max-w-xs mt-1">
          Select any issue from the list or click a marked line in the code editor to inspect insights and suggested fixes.
        </p>
      </div>
    );
  }

  const handleCopyFix = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Replacement code copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  const detectedBy = finding.detected_by || [finding.detection_source];
  const isHybrid = finding.detection_source === 'hybrid';
  const confidencePct = Math.round((finding.confidence || 0.9) * 100);

  return (
    <div className="h-full flex flex-col bg-slate-950 overflow-y-auto select-none">
      {/* Header */}
      <div className="p-4 border-b border-white/[0.08] flex items-start justify-between gap-4 bg-slate-900/60 sticky top-0 backdrop-blur-md z-10">
        <div className="space-y-2 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <SeverityBadge severity={finding.severity} size="md" />
            <SourceBadge source={finding.detection_source} />
            <CategoryBadge category={finding.category} />
            {finding.rule_id && (
              <span className="text-[11px] font-mono text-cyan-300 bg-white/[0.04] px-2 py-0.5 rounded-md border border-white/[0.08] font-semibold">
                {finding.rule_id}
              </span>
            )}
          </div>

          <h2 className="text-[16px] font-bold text-white leading-snug">
            {finding.title.replace(/^\[RULE-\d+\]\s*/, '')}
          </h2>

          {/* Line Location & Action */}
          {finding.line_number != null && (
            <div className="flex items-center gap-2 pt-0.5">
              <button
                onClick={() => onJumpToLine && onJumpToLine(finding.line_number!, finding.end_line)}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-[12px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/20 transition-colors cursor-pointer"
              >
                <MapPin className="w-3.5 h-3.5" />
                <span>Jump to Line {finding.line_number} in Editor</span>
                <ExternalLink className="w-3 h-3 ml-0.5" />
              </button>
            </div>
          )}
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-white/[0.06] cursor-pointer"
            title="Close Inspector"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="p-5 space-y-5 flex-1">
        {/* MULTI-TOOL PROVENANCE */}
        <div className="space-y-2">
          <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider">Multi-Source Verification</span>
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/[0.06] space-y-2.5">
            <div className="flex flex-wrap items-center gap-2">
              {detectedBy.map(tool => (
                <span
                  key={tool}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11.5px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/25"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  {tool.toUpperCase()}
                </span>
              ))}
            </div>

            <div className="flex items-center justify-between text-[12px] pt-2 border-t border-white/[0.04] text-slate-300">
              <span>
                {isHybrid ? '✦ Corroborated: Static analysis & AI reasoning agree' : 'Single analyzer detection'}
              </span>
              <span className="text-cyan-300 font-semibold">
                Confidence: {finding.confidence_level || 'HIGH'} ({confidencePct}%)
              </span>
            </div>
          </div>
        </div>

        {/* ISSUE DESCRIPTION */}
        <div className="space-y-2">
          <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider">Issue Description</span>
          <p className="text-[13.5px] text-slate-200 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-white/[0.06]">
            {finding.description}
          </p>
        </div>

        {/* CODE EVIDENCE */}
        {finding.code_evidence && (
          <div className="space-y-2">
            <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider">Affected Source Evidence</span>
            <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/25 font-mono text-[12.5px] text-rose-300 overflow-x-auto">
              <code>{finding.code_evidence}</code>
            </div>
          </div>
        )}

        {/* AI INSIGHTS & REASONING (QWEN2.5) */}
        {finding.explanation && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Brain className="w-3.5 h-3.5 text-indigo-400" />
                <span>AI Root Cause & Analysis</span>
              </span>
              <span className="text-[11px] font-medium text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                Qwen2.5-Coder
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-gradient-to-b from-indigo-500/5 to-transparent border border-indigo-500/20 text-[13px] text-slate-200 leading-relaxed">
              <p>{finding.explanation}</p>
            </div>
          </div>
        )}

        {/* RECOMMENDATION */}
        {finding.recommendation && (
          <div className="space-y-2">
            <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
              <span>Recommended Approach</span>
            </span>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/[0.06] text-[13px] text-slate-200 leading-relaxed">
              <p>{finding.recommendation}</p>
            </div>
          </div>
        )}

        {/* SUGGESTED FIX DIFF & COPY */}
        {finding.suggested_fix && (
          <div className="space-y-3 pb-4">
            <div className="flex items-center justify-between">
              <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider">Suggested Refactoring</span>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1 bg-slate-900 p-0.5 rounded-lg border border-white/[0.08] text-[11px]">
                  <button
                    onClick={() => setDiffMode('unified')}
                    className={`px-2 py-0.5 rounded-md font-medium cursor-pointer transition-colors ${
                      diffMode === 'unified' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Diff View
                  </button>
                  <button
                    onClick={() => setDiffMode('clean')}
                    className={`px-2 py-0.5 rounded-md font-medium cursor-pointer transition-colors ${
                      diffMode === 'clean' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Clean Code
                  </button>
                </div>

                <button
                  onClick={() => handleCopyFix(finding.suggested_fix!.replacement_snippet)}
                  className="btn-primary-gradient text-[12px] py-1.5 px-3"
                  title="Copy replacement snippet"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-white" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>Copy Fix</span>
                </button>
              </div>
            </div>

            {finding.suggested_fix.explanation && (
              <p className="text-[12.5px] text-slate-400 italic">
                {finding.suggested_fix.explanation}
              </p>
            )}

            {/* Diff Viewer */}
            {diffMode === 'unified' ? (
              <div className="rounded-xl bg-slate-950 border border-white/[0.08] font-mono text-[12.5px] overflow-hidden">
                {finding.code_evidence && (
                  <div className="flex items-start bg-rose-500/10 border-b border-white/[0.04] text-rose-300 px-3 py-2">
                    <span className="w-6 text-rose-500 font-bold select-none">-</span>
                    <pre className="flex-1 whitespace-pre-wrap leading-relaxed">
                      <code>{finding.code_evidence.trim()}</code>
                    </pre>
                  </div>
                )}

                <div className="flex items-start bg-emerald-500/10 text-emerald-300 px-3 py-2">
                  <span className="w-6 text-emerald-500 font-bold select-none">+</span>
                  <pre className="flex-1 whitespace-pre-wrap leading-relaxed">
                    <code>{finding.suggested_fix.replacement_snippet}</code>
                  </pre>
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30 text-[12.5px] font-mono text-emerald-300 overflow-x-auto">
                <pre className="whitespace-pre-wrap leading-relaxed">
                  <code>{finding.suggested_fix.replacement_snippet}</code>
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
