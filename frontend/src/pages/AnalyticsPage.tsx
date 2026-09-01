import React, { useState, useEffect } from 'react';
import { ReviewResponse } from '../types';
import { apiService } from '../services/api';
import { Header } from '../components/layout/Navbar';
import {
  Shield, Bug, Clock,
  AlertTriangle, Loader2, Activity, Layers, Terminal
} from 'lucide-react';

interface MetricTileProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ElementType;
  iconColor: string;
}

const MetricTile: React.FC<MetricTileProps> = ({
  label,
  value,
  sub,
  icon: Icon,
  iconColor,
}) => (
  <div className="glass-card p-5 flex items-center justify-between">
    <div className="min-w-0">
      <span className="text-[12px] font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
      <p className="text-2xl font-bold text-white leading-tight mt-1">{value}</p>
      {sub && <p className="text-[12px] text-slate-400 mt-1 truncate">{sub}</p>}
    </div>
    <div className={`w-12 h-12 rounded-2xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-center flex-shrink-0 ${iconColor}`}>
      <Icon className="w-6 h-6" />
    </div>
  </div>
);

interface DistributionBarProps {
  label: string;
  count: number;
  max: number;
  color: string;
}

const DistributionBar: React.FC<DistributionBarProps> = ({ label, count, max, color }) => {
  const pct = max > 0 ? (count / max) * 100 : 0;
  return (
    <div className="space-y-1.5 text-[13px]">
      <div className="flex justify-between items-center font-medium">
        <span className="text-slate-200">{label}</span>
        <span className="text-slate-400 font-semibold">{count}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
};

export const AnalyticsPage: React.FC = () => {
  const [reviews, setReviews] = useState<ReviewResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const resp = await apiService.listReviews(1, 100);
        setReviews(resp.items);
      } catch (err: any) {
        setError(err.message || 'Failed to retrieve analytics data');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col h-full overflow-hidden bg-ambient-glow">
        <Header pageTitle="Engineering Analytics" pageSubtitle="Aggregate quality metrics and security diagnostics" />
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-slate-400">
          <Loader2 className="w-7 h-7 animate-spin text-cyan-400" />
          <span className="text-[13px]">Calculating analytics metrics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full overflow-hidden bg-ambient-glow">
        <Header pageTitle="Engineering Analytics" pageSubtitle="Aggregate quality metrics and security diagnostics" />
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-rose-400 p-8">
          <AlertTriangle className="w-8 h-8" />
          <span className="text-[13px]">{error}</span>
        </div>
      </div>
    );
  }

  if (reviews.length === 0) {
    return (
      <div className="flex flex-col h-full overflow-hidden bg-ambient-glow select-none">
        <Header pageTitle="Engineering Analytics" pageSubtitle="Aggregate quality metrics and security diagnostics" />
        <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center text-slate-400">
          <Layers className="w-14 h-14 text-slate-400" />
          <h3 className="text-base font-bold text-slate-200">No Analytics Recorded</h3>
          <p className="text-[13px] text-slate-400 max-w-xs leading-relaxed">
            Run code reviews from the Code Review tab to populate aggregate analytics and trends.
          </p>
        </div>
      </div>
    );
  }

  const totalReviews = reviews.length;
  const allFindings = reviews.flatMap(r => r.findings || []);
  const totalFindings = allFindings.length;
  const criticalCount = reviews.reduce((sum, r) => sum + (r.summary?.critical_count || 0), 0);
  const highCount = reviews.reduce((sum, r) => sum + (r.summary?.high_count || 0), 0);
  const securityCount = allFindings.filter(f => f.category === 'security').length;

  const validScores = reviews.filter(r => r.quality_score?.overall_score != null);
  const avgScore = validScores.length > 0
    ? Math.round(validScores.reduce((sum, r) => sum + r.quality_score!.overall_score, 0) / validScores.length)
    : null;

  const validDurations = reviews.filter(r => r.metadata?.total_duration_ms != null);
  const avgDuration = validDurations.length > 0
    ? (validDurations.reduce((sum, r) => sum + r.metadata!.total_duration_ms, 0) / validDurations.length)
    : null;

  const hybridCount = reviews.filter(r => r.summary?.review_mode === 'HYBRID').length;

  // Severity Distribution
  const sevMap: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
  allFindings.forEach(f => {
    sevMap[f.severity] = (sevMap[f.severity] || 0) + 1;
  });
  const maxSev = Math.max(...Object.values(sevMap), 1);

  // Category Breakdown
  const catMap: Record<string, number> = {};
  allFindings.forEach(f => {
    catMap[f.category] = (catMap[f.category] || 0) + 1;
  });
  const maxCat = Math.max(...Object.values(catMap), 1);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-ambient-glow select-none">
      <Header
        pageTitle="Engineering Analytics"
        pageSubtitle={`Aggregated across ${totalReviews} code reviews`}
      />

      <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* ROW 1: PRIMARY METRICS TILES */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricTile
            label="Total Reviews"
            value={totalReviews}
            sub={`${hybridCount} hybrid / ${totalReviews - hybridCount} static`}
            icon={Terminal}
            iconColor="text-cyan-400"
          />
          <MetricTile
            label="Average Health"
            value={avgScore != null ? `${avgScore} / 100` : '—'}
            sub="Across all submissions"
            icon={Activity}
            iconColor="text-emerald-400"
          />
          <MetricTile
            label="Total Findings"
            value={totalFindings}
            sub={`${criticalCount} critical issues`}
            icon={Layers}
            iconColor="text-indigo-400"
          />
          <MetricTile
            label="Average Duration"
            value={avgDuration != null ? `${(avgDuration / 1000).toFixed(2)}s` : '—'}
            sub="End-to-end review latency"
            icon={Clock}
            iconColor="text-amber-400"
          />
        </div>

        {/* ROW 2: DISTRIBUTIONS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* SEVERITY SPECTRUM */}
          <div className="glass-card p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
              <h3 className="text-base font-bold text-white tracking-tight">Severity Spectrum</h3>
              <AlertTriangle className="w-4 h-4 text-rose-400" />
            </div>
            <div className="space-y-3.5">
              <DistributionBar label="Critical Flaws" count={sevMap.critical} max={maxSev} color="bg-rose-500 shadow-[0_0_10px_#f43f5e]" />
              <DistributionBar label="High Severity" count={sevMap.high} max={maxSev} color="bg-amber-500" />
              <DistributionBar label="Medium Issues" count={sevMap.medium} max={maxSev} color="bg-yellow-500" />
              <DistributionBar label="Low Severity" count={sevMap.low} max={maxSev} color="bg-sky-400" />
              <DistributionBar label="Informational" count={sevMap.info} max={maxSev} color="bg-purple-400" />
            </div>
          </div>

          {/* CATEGORY BREAKDOWN */}
          <div className="glass-card p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
              <h3 className="text-base font-bold text-white tracking-tight">Issue Categories</h3>
              <Bug className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="space-y-3.5">
              <DistributionBar label="Security Vulnerabilities" count={catMap.security || 0} max={maxCat} color="bg-rose-500" />
              <DistributionBar label="Reliability & Bugs" count={catMap.bug || 0} max={maxCat} color="bg-amber-500" />
              <DistributionBar label="Maintainability & Structure" count={catMap.maintainability || 0} max={maxCat} color="bg-sky-400" />
              <DistributionBar label="Performance Bottlenecks" count={catMap.performance || 0} max={maxCat} color="bg-yellow-500" />
              <DistributionBar label="Style & Consistency" count={catMap.style || 0} max={maxCat} color="bg-purple-400" />
            </div>
          </div>
        </div>

        {/* ROW 3: SECURITY THREAT SUMMARY */}
        {securityCount > 0 && (
          <div className="glass-card p-6 border-rose-500/30 bg-rose-500/5 space-y-3">
            <div className="flex items-center gap-2 text-rose-400 font-bold text-[14px]">
              <Shield className="w-5 h-5" />
              <span>Security Threat Index</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center pt-2">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-white/[0.06]">
                <p className="text-3xl font-bold text-rose-400">{securityCount}</p>
                <p className="text-[12px] font-medium text-slate-400 mt-1 uppercase">Security Issues</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/80 border border-white/[0.06]">
                <p className="text-3xl font-bold text-amber-400">{criticalCount}</p>
                <p className="text-[12px] font-medium text-slate-400 mt-1 uppercase">Critical Exploits</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/80 border border-white/[0.06]">
                <p className="text-3xl font-bold text-yellow-400">{highCount}</p>
                <p className="text-[12px] font-medium text-slate-400 mt-1 uppercase">High Severity Risks</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
