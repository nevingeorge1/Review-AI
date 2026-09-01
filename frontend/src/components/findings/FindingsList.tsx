import React, { useState, useMemo } from 'react';
import { ReviewFinding, Severity } from '../../types';
import { SeverityBadge, SourceBadge, CategoryBadge, SeverityDot } from '../common/Badge';
import {
  Search,
  MapPin,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';

interface FindingsListProps {
  findings: ReviewFinding[];
  selectedFindingId?: string;
  onSelectFinding: (finding: ReviewFinding) => void;
}

type SortKey = 'priority' | 'severity' | 'line';

const SEVERITY_WEIGHT: Record<Severity, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
  info: 4,
};

export const FindingsList: React.FC<FindingsListProps> = ({
  findings,
  selectedFindingId,
  onSelectFinding,
}) => {
  const [search, setSearch] = useState('');
  const [sevFilter, setSevFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortKey>('priority');

  const filtered = useMemo(() => {
    return findings
      .filter(f => {
        if (search) {
          const q = search.toLowerCase();
          const matchTitle = f.title.toLowerCase().includes(q);
          const matchDesc = f.description.toLowerCase().includes(q);
          const matchRule = (f.rule_id || '').toLowerCase().includes(q);
          if (!matchTitle && !matchDesc && !matchRule) return false;
        }
        if (sevFilter !== 'all' && f.severity !== sevFilter) return false;
        return true;
      })
      .sort((a, b) => {
        if (sortBy === 'line') return (a.line_number ?? 9999) - (b.line_number ?? 9999);
        if (sortBy === 'severity') return (SEVERITY_WEIGHT[a.severity] ?? 99) - (SEVERITY_WEIGHT[b.severity] ?? 99);
        // Priority default
        if (SEVERITY_WEIGHT[a.severity] !== SEVERITY_WEIGHT[b.severity]) {
          return SEVERITY_WEIGHT[a.severity] - SEVERITY_WEIGHT[b.severity];
        }
        if (a.detection_source === 'hybrid' && b.detection_source !== 'hybrid') return -1;
        if (b.detection_source === 'hybrid' && a.detection_source !== 'hybrid') return 1;
        return (a.line_number ?? 0) - (b.line_number ?? 0);
      });
  }, [findings, search, sevFilter, sortBy]);

  return (
    <div className="flex flex-col h-full select-none">
      {/* Search & Filter Header */}
      <div className="p-3.5 border-b border-white/[0.06] space-y-3 bg-slate-950/60">
        <div className="flex items-center gap-2">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search findings or rule ID..."
              className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-[13px] text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cyan-400 transition-colors"
            />
          </div>

          {/* Sort Selector */}
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value as SortKey)}
            className="px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-[12px] font-medium text-slate-300 focus:outline-none focus:border-cyan-400 cursor-pointer"
          >
            <option value="priority" className="bg-slate-900">Priority</option>
            <option value="severity" className="bg-slate-900">Severity</option>
            <option value="line" className="bg-slate-900">Line #</option>
          </select>
        </div>

        {/* Severity Filter Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5">
          {['all', 'critical', 'high', 'medium', 'low'].map(s => {
            const isActive = sevFilter === s;
            const count = s === 'all' ? findings.length : findings.filter(f => f.severity === s).length;
            if (count === 0 && s !== 'all') return null;

            return (
              <button
                key={s}
                onClick={() => setSevFilter(s)}
                className={`px-2.5 py-1 rounded-md text-[11.5px] font-semibold uppercase tracking-wider transition-all cursor-pointer flex-shrink-0 ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'bg-white/[0.03] text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] border border-transparent'
                }`}
              >
                {s} ({count})
              </button>
            );
          })}
        </div>
      </div>

      {/* Issues Count Bar */}
      <div className="px-4 py-2 border-b border-white/[0.04] flex items-center justify-between text-[12px] font-medium text-slate-400 bg-slate-900/40">
        <span>{filtered.length} of {findings.length} Issues Found</span>
        {(search || sevFilter !== 'all') && (
          <button
            onClick={() => { setSearch(''); setSevFilter('all'); }}
            className="text-cyan-400 hover:underline cursor-pointer"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Findings List Items */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center text-slate-400">
            <CheckCircle2 className="w-8 h-8 text-slate-400 mb-2" />
            <p className="font-semibold text-[13.5px] text-slate-300">No matching issues</p>
            <p className="text-[12px] text-slate-400 mt-0.5">Try clearing your filters or search keywords</p>
          </div>
        ) : (
          filtered.map(finding => {
            const isSelected = selectedFindingId === finding.id;

            return (
              <div
                key={finding.id}
                onClick={() => onSelectFinding(finding)}
                className={`p-3.5 rounded-xl border transition-all duration-150 cursor-pointer ${
                  isSelected
                    ? 'bg-slate-850 border-cyan-500/50 shadow-glow-subtle'
                    : 'bg-slate-900/60 border-white/[0.06] hover:bg-slate-850 hover:border-white/[0.12]'
                }`}
              >
                <div className="flex items-start gap-3">
                  <SeverityDot severity={finding.severity} className="mt-1.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0 space-y-1.5">
                    {/* Header Badges */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <SeverityBadge severity={finding.severity} />
                      <SourceBadge source={finding.detection_source} />
                      <CategoryBadge category={finding.category} />
                      {finding.rule_id && (
                        <span className="text-[10.5px] font-mono text-slate-400 bg-white/[0.04] px-1.5 py-0.5 rounded border border-white/[0.06]">
                          {finding.rule_id}
                        </span>
                      )}
                    </div>

                    {/* Title */}
                    <p className="text-[13.5px] font-semibold text-slate-100 leading-snug">
                      {finding.title.replace(/^\[RULE-\d+\]\s*/, '')}
                    </p>

                    {/* Line Number & Evidence */}
                    {finding.line_number != null && (
                      <div className="flex items-center gap-1.5 text-[12px] font-medium text-cyan-400">
                        <MapPin className="w-3.5 h-3.5" />
                        <span>Line {finding.line_number}{finding.end_line && finding.end_line !== finding.line_number ? `–${finding.end_line}` : ''}</span>
                        {finding.code_evidence && (
                          <span className="text-slate-400 font-mono font-normal truncate max-w-[200px] ml-1">
                            · {finding.code_evidence.trim()}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center text-slate-400 flex-shrink-0 self-center">
                    <ChevronRight className={`w-4 h-4 transition-transform ${isSelected ? 'text-cyan-400 translate-x-0.5' : ''}`} />
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
