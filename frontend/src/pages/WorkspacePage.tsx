import React, { useState } from 'react';
import { Language, ReviewFinding, ReviewResponse, Category } from '../types';
import { CodeEditor } from '../components/editor/CodeEditor';
import { ScoreCard } from '../components/score/ScoreCard';
import { FindingsList } from '../components/findings/FindingsList';
import { IntelligenceInspector } from '../components/findings/IntelligenceInspector';
import { LoadingProgress } from '../components/common/LoadingProgress';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { Header } from '../components/layout/Navbar';
import { ShieldCheck, ArrowLeft, X } from 'lucide-react';

interface WorkspacePageProps {
  code: string;
  onCodeChange: (code: string) => void;
  language: Language;
  onLanguageChange: (lang: Language) => void;
  filename: string;
  onFilenameChange: (name: string) => void;
  onReviewSubmit: () => void;
  onClear: () => void;
  isAnalyzing: boolean;
  activeReview?: ReviewResponse;
  selectedFinding: ReviewFinding | undefined;
  onSelectFinding: (finding: ReviewFinding | undefined) => void;
  errorMessage?: string;
  onDismissError: () => void;
  onSelectSample: (sampleId: string) => void;
  highlightLine?: number;
  highlightEndLine?: number;
  onJumpToLine: (line: number, endLine?: number) => void;
  onNewReview: () => void;
}

export const WorkspacePage: React.FC<WorkspacePageProps> = ({
  code,
  onCodeChange,
  language,
  onLanguageChange,
  filename,
  onFilenameChange,
  onReviewSubmit,
  onClear,
  isAnalyzing,
  activeReview,
  selectedFinding,
  onSelectFinding,
  errorMessage,
  onDismissError,
  onSelectSample,
  highlightLine,
  highlightEndLine,
  onJumpToLine,
  onNewReview,
}) => {
  const [catFilter, setCatFilter] = useState<Category | undefined>(undefined);

  const reviewMode = activeReview?.summary?.review_mode;
  const hasResults = Boolean(activeReview);
  const isCleanCode = hasResults && activeReview!.findings.length === 0;

  const displayedFindings = (hasResults && activeReview?.findings)
    ? (catFilter ? activeReview.findings.filter(f => f.category === catFilter) : activeReview.findings)
    : [];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-ambient-glow">
      {/* Top Header */}
      <Header
        pageTitle="Code Review"
        pageSubtitle="Deterministic Static Analysis + Local AI Reasoning"
        reviewMode={reviewMode}
        onNewReview={onNewReview}
        onLoadSample={onSelectSample}
        latencyMs={activeReview?.metadata?.total_duration_ms}
      />

      {/* Error Alert */}
      {errorMessage && (
        <div className="px-6 pt-3 flex-shrink-0">
          <ErrorBanner
            message={errorMessage}
            onDismiss={onDismissError}
            onRetry={onReviewSubmit}
          />
        </div>
      )}

      {/* Workspace Fluid Canvas */}
      <div className="flex-1 flex overflow-hidden p-4 gap-4">
        {/* LEFT / CENTER: Dominant Code Editor Card */}
        <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
          <CodeEditor
            code={code}
            onChange={onCodeChange}
            language={language}
            onLanguageChange={onLanguageChange}
            filename={filename}
            onFilenameChange={onFilenameChange}
            onReviewSubmit={onReviewSubmit}
            onClear={onClear}
            isAnalyzing={isAnalyzing}
            highlightLine={highlightLine}
            highlightEndLine={highlightEndLine}
            findings={activeReview?.findings || []}
          />
        </div>

        {/* RIGHT: Results / Inspector / Empty State Panel */}
        <div className="w-full lg:w-[460px] xl:w-[500px] flex-shrink-0 h-full flex flex-col min-w-0 overflow-hidden glass-card">
          {isAnalyzing ? (
            <div className="h-full overflow-hidden">
              <LoadingProgress filename={filename} />
            </div>

          ) : selectedFinding ? (
            /* Finding Inspector View */
            <div className="h-full flex flex-col overflow-hidden animate-fade-in">
              <div className="px-4 py-2.5 border-b border-white/[0.08] bg-slate-900/60 flex items-center justify-between text-[12.5px] font-medium">
                <button
                  onClick={() => onSelectFinding(undefined)}
                  className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 transition-colors cursor-pointer"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back to Issues</span>
                </button>
                <span className="text-slate-400">Issue Details</span>
              </div>
              <div className="flex-1 overflow-hidden">
                <IntelligenceInspector
                  finding={selectedFinding}
                  onClose={() => onSelectFinding(undefined)}
                  onJumpToLine={onJumpToLine}
                />
              </div>
            </div>

          ) : hasResults ? (
            /* Full Results: Health Score + Findings Stream */
            <div className="h-full flex flex-col overflow-hidden animate-fade-in">
              {/* Radial Health Card */}
              <div className="p-4 border-b border-white/[0.06] flex-shrink-0 overflow-y-auto max-h-[340px]">
                <ScoreCard
                  score={activeReview!.quality_score!}
                  summary={activeReview!.summary!}
                  durationMs={activeReview!.metadata?.total_duration_ms}
                  onSelectCategory={(cat) => setCatFilter(prev => prev === cat ? undefined : cat)}
                />
              </div>

              {/* Category Filter Indicator */}
              {catFilter && (
                <div className="px-4 py-2 bg-cyan-500/10 border-b border-cyan-500/20 flex items-center justify-between text-[12px] font-semibold text-cyan-400">
                  <span>Filtered by: {catFilter.toUpperCase()}</span>
                  <button
                    onClick={() => setCatFilter(undefined)}
                    className="hover:underline flex items-center gap-1 cursor-pointer"
                  >
                    <span>Clear</span>
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {/* Issues Stream */}
              <div className="flex-1 overflow-hidden flex flex-col bg-slate-950/60">
                {isCleanCode ? (
                  <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
                    <ShieldCheck className="w-12 h-12 text-emerald-400 mb-3" />
                    <h3 className="text-base font-bold text-white tracking-tight">
                      Code is Clean
                    </h3>
                    <p className="text-[13px] text-slate-400 max-w-xs mt-1 leading-relaxed">
                      Zero security vulnerabilities, bugs, or performance issues were detected in this review pass.
                    </p>
                  </div>
                ) : (
                  <FindingsList
                    findings={displayedFindings}
                    selectedFindingId={undefined}
                    onSelectFinding={onSelectFinding}
                  />
                )}
              </div>
            </div>

          ) : (
            /* Empty State */
            <div className="h-full overflow-y-auto">
              <EmptyState onSelectSample={onSelectSample} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
