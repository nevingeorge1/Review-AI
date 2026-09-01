import React, { useState, useEffect } from 'react';
import { ReviewResponse } from '../types';
import { apiService } from '../services/api';
import { Header } from '../components/layout/Navbar';
import { GradeBadge } from '../components/common/Badge';
import { toast } from '../components/common/ErrorBanner';
import {
  Search, Trash2, Eye, FileCode,
  ChevronLeft, ChevronRight, AlertTriangle, Loader2, RefreshCw,
  Activity, Layers
} from 'lucide-react';

interface HistoryPageProps {
  onSelectReview: (review: ReviewResponse) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onSelectReview }) => {
  const [reviews, setReviews] = useState<ReviewResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();
  const [search, setSearch] = useState('');
  const [deletingId, setDeletingId] = useState<string | undefined>();

  const PAGE_SIZE = 15;

  const loadHistory = async (p: number) => {
    setLoading(true);
    setError(undefined);
    try {
      const resp = await apiService.listReviews(p, PAGE_SIZE);
      setReviews(resp.items);
      setTotal(resp.total);
    } catch (e: any) {
      setError(e.message || 'Failed to retrieve review history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(page);
  }, [page]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this review record? This cannot be undone.')) return;
    setDeletingId(id);
    try {
      await apiService.deleteReview(id);
      setReviews(prev => prev.filter(r => r.review_id !== id));
      setTotal(prev => Math.max(0, prev - 1));
      toast.info('Review record deleted');
    } catch {
      toast.error('Failed to delete review');
    } finally {
      setDeletingId(undefined);
    }
  };

  const filtered = search
    ? reviews.filter(r =>
        r.filename.toLowerCase().includes(search.toLowerCase()) ||
        r.language.toLowerCase().includes(search.toLowerCase()) ||
        r.review_id.toLowerCase().includes(search.toLowerCase())
      )
    : reviews;

  const totalFindings = reviews.reduce((sum, r) => sum + (r.summary?.total_findings ?? r.findings?.length ?? 0), 0);
  const totalCritical = reviews.reduce((sum, r) => sum + (r.summary?.critical_count ?? 0), 0);
  const scoresWithVal = reviews.filter(r => r.quality_score?.overall_score != null);
  const avgScore = scoresWithVal.length > 0
    ? Math.round(scoresWithVal.reduce((sum, r) => sum + r.quality_score!.overall_score, 0) / scoresWithVal.length)
    : null;

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;

  const formatDate = (iso: string) => {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('en-US', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    } catch {
      return iso;
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-ambient-glow select-none">
      <Header
        pageTitle="Review History"
        pageSubtitle="Past code intelligence analysis reports and benchmarks"
        rightContent={
          <button
            onClick={() => loadHistory(page)}
            className="btn-secondary-modern"
            title="Sync History"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span>Refresh</span>
          </button>
        }
      />

      <div className="flex-1 overflow-hidden flex flex-col p-6 gap-5 max-w-7xl mx-auto w-full">
        {/* SUMMARY METRICS STRIP */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
          <div className="glass-card p-4 flex items-center justify-between">
            <div>
              <p className="text-[12px] font-semibold uppercase tracking-wider text-slate-400">Total Reviews</p>
              <p className="text-2xl font-bold text-white mt-0.5">{total}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <FileCode className="w-5 h-5" />
            </div>
          </div>

          <div className="glass-card p-4 flex items-center justify-between">
            <div>
              <p className="text-[12px] font-semibold uppercase tracking-wider text-slate-400">Average Health</p>
              <p className="text-2xl font-bold text-emerald-400 mt-0.5">{avgScore != null ? `${avgScore} / 100` : '—'}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Activity className="w-5 h-5" />
            </div>
          </div>

          <div className="glass-card p-4 flex items-center justify-between">
            <div>
              <p className="text-[12px] font-semibold uppercase tracking-wider text-slate-400">Total Findings</p>
              <p className="text-2xl font-bold text-slate-100 mt-0.5">{totalFindings}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
          </div>

          <div className="glass-card p-4 flex items-center justify-between">
            <div>
              <p className="text-[12px] font-semibold uppercase tracking-wider text-slate-400">Critical Flaws</p>
              <p className={`text-2xl font-bold mt-0.5 ${totalCritical > 0 ? 'text-rose-400' : 'text-slate-100'}`}>{totalCritical}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* SEARCH BAR */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search reports by filename or ID..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900/60 border border-white/[0.08] text-[13px] text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cyan-400 transition-colors"
            />
          </div>

          {search && (
            <button
              onClick={() => setSearch('')}
              className="text-cyan-400 hover:underline text-[12.5px] cursor-pointer"
            >
              Clear
            </button>
          )}
        </div>

        {/* TIMELINE TABLE */}
        <div className="glass-card flex-1 overflow-hidden flex flex-col">
          {/* Column Headers */}
          <div className="grid grid-cols-12 gap-3 px-5 py-3 border-b border-white/[0.06] bg-slate-900/80 text-[12px] font-semibold uppercase tracking-wider text-slate-400 flex-shrink-0">
            <div className="col-span-4">Target File</div>
            <div className="col-span-2">Health Score</div>
            <div className="col-span-2">Issues Found</div>
            <div className="col-span-1">Mode</div>
            <div className="col-span-1">Latency</div>
            <div className="col-span-1">Date</div>
            <div className="col-span-1 text-right">Action</div>
          </div>

          {/* Data Rows */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-400">
                <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
                <span className="text-[13px]">Loading review history...</span>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-20 gap-3 text-rose-400">
                <AlertTriangle className="w-8 h-8" />
                <span className="text-[13px]">{error}</span>
                <button onClick={() => loadHistory(page)} className="btn-secondary-modern text-[12px] mt-2">
                  Retry Query
                </button>
              </div>
            ) : filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-400 text-center">
                <FileCode className="w-12 h-12 text-slate-400" />
                <p className="font-semibold text-base text-slate-200">
                  {search ? 'No matching reports' : 'No review history yet'}
                </p>
                <p className="text-[13px] text-slate-400 max-w-xs leading-relaxed">
                  {search ? 'Try adjusting your search keywords.' : 'Run your first code review from the Code Review tab.'}
                </p>
              </div>
            ) : (
              filtered.map(review => {
                const score = review.quality_score?.overall_score;
                const grade = review.quality_score?.grade;
                const issueCount = review.summary?.total_findings ?? review.findings?.length ?? 0;
                const criticalCount = review.summary?.critical_count ?? 0;
                const duration = review.metadata?.total_duration_ms;
                const mode = review.summary?.review_mode || 'HYBRID';

                return (
                  <div
                    key={review.review_id}
                    onClick={() => onSelectReview(review)}
                    className="grid grid-cols-12 gap-3 px-5 py-3.5 border-b border-white/[0.04] hover:bg-white/[0.03] cursor-pointer transition-colors duration-150 items-center group"
                  >
                    {/* Filename & UUID */}
                    <div className="col-span-4 min-w-0">
                      <div className="flex items-center gap-2">
                        <FileCode className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                        <span className="font-semibold text-[13.5px] text-slate-100 truncate group-hover:text-cyan-300 transition-colors">
                          {review.filename}
                        </span>
                        <span className="text-[11px] font-medium text-slate-400 uppercase bg-white/[0.04] px-1.5 py-0.5 rounded">
                          {review.language}
                        </span>
                      </div>
                      <span className="text-[11px] font-mono text-slate-400 truncate block mt-0.5 max-w-[200px]">
                        {review.review_id}
                      </span>
                    </div>

                    {/* Health Score & Grade */}
                    <div className="col-span-2 flex items-center gap-2">
                      {score != null ? (
                        <>
                          <span className="font-bold text-[14px] text-slate-100">{score.toFixed(0)}</span>
                          {grade && <GradeBadge grade={grade} size="sm" />}
                        </>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </div>

                    {/* Total Issues & Critical */}
                    <div className="col-span-2 flex items-center gap-2">
                      <span className={`font-semibold text-[13px] ${issueCount > 0 ? 'text-slate-200' : 'text-emerald-400'}`}>
                        {issueCount} issue{issueCount !== 1 ? 's' : ''}
                      </span>
                      {criticalCount > 0 && (
                        <span className="px-1.5 py-0.5 rounded text-[10.5px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30">
                          {criticalCount} Critical
                        </span>
                      )}
                    </div>

                    {/* Mode */}
                    <div className="col-span-1">
                      <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                        mode === 'HYBRID'
                          ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                          : 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                      }`}>
                        {mode}
                      </span>
                    </div>

                    {/* Latency */}
                    <div className="col-span-1 text-slate-400 text-[12px] font-mono">
                      {duration ? `${(duration / 1000).toFixed(1)}s` : '—'}
                    </div>

                    {/* Date */}
                    <div className="col-span-1 text-slate-400 text-[12px]">
                      {formatDate(review.created_at)}
                    </div>

                    {/* Actions */}
                    <div className="col-span-1 flex items-center justify-end gap-1.5">
                      <button
                        onClick={e => { e.stopPropagation(); onSelectReview(review); }}
                        className="btn-secondary-modern p-1.5 text-slate-400 hover:text-cyan-400"
                        title="Load review in workspace"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={e => handleDelete(review.review_id, e)}
                        disabled={deletingId === review.review_id}
                        className="btn-secondary-modern p-1.5 text-slate-400 hover:text-rose-400"
                        title="Delete report"
                      >
                        {deletingId === review.review_id
                          ? <Loader2 className="w-4 h-4 animate-spin" />
                          : <Trash2 className="w-4 h-4" />
                        }
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="p-3.5 border-t border-white/[0.06] flex items-center justify-between bg-slate-900/80 text-[12.5px] text-slate-400 flex-shrink-0">
              <span>Page {page} of {totalPages} ({total} Reports)</span>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-secondary-modern p-1.5 disabled:opacity-30"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="btn-secondary-modern p-1.5 disabled:opacity-30"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
