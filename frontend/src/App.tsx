import React, { useState, useEffect } from 'react';
import { Language, ReviewFinding, ReviewResponse } from './types';
import { apiService } from './services/api';
import { CODE_SAMPLES } from './data/samples';
import { NavTab, Sidebar } from './components/layout/Sidebar';
import { WorkspacePage } from './pages/WorkspacePage';
import { HistoryPage } from './pages/HistoryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { DocsPage } from './pages/DocsPage';
import { SettingsPage } from './pages/SettingsPage';
import { ToastContainer, toast } from './components/common/ErrorBanner';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('workspace');
  const [code, setCode] = useState<string>(CODE_SAMPLES[0].code);
  const [filename, setFilename] = useState<string>(CODE_SAMPLES[0].filename);
  const [language, setLanguage] = useState<Language>('python');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeReview, setActiveReview] = useState<ReviewResponse | undefined>(undefined);
  const [selectedFinding, setSelectedFinding] = useState<ReviewFinding | undefined>(undefined);
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
  const [backendConnected, setBackendConnected] = useState(false);
  const [historyCount, setHistoryCount] = useState(0);

  const [highlightLine, setHighlightLine] = useState<number | undefined>(undefined);
  const [highlightEndLine, setHighlightEndLine] = useState<number | undefined>(undefined);

  // Connectivity & history count polling
  useEffect(() => {
    const checkConnectivity = async () => {
      try {
        await apiService.checkHealth();
        setBackendConnected(true);
        const historyResp = await apiService.listReviews(1, 10);
        setHistoryCount(historyResp.total);
      } catch {
        setBackendConnected(false);
      }
    };

    checkConnectivity();
    const interval = setInterval(checkConnectivity, 15000);
    return () => clearInterval(interval);
  }, []);

  // Submit Code Review
  const handleReviewSubmit = async () => {
    if (!code.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setErrorMessage(undefined);
    setSelectedFinding(undefined);
    setHighlightLine(undefined);

    try {
      const reviewResp = await apiService.submitReview({
        code,
        language,
        filename,
        enable_static_analysis: true,
        enable_llm: true,
      });

      setActiveReview(reviewResp);
      setHistoryCount(prev => prev + 1);

      const issueCount = reviewResp.findings.length;
      const mode = reviewResp.summary?.review_mode || 'HYBRID';
      toast.success(`Analysis complete (${mode}) — ${issueCount} finding${issueCount !== 1 ? 's' : ''} detected.`);
    } catch (err: any) {
      const msg = err.message || 'Review execution failed. Please verify the backend service is reachable.';
      setErrorMessage(msg);
      toast.error('Code analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Load Benchmark Scenario Sample
  const handleLoadSample = (sampleId: string) => {
    const sample = CODE_SAMPLES.find(s => s.id === sampleId);
    if (sample) {
      setCode(sample.code);
      setFilename(sample.filename);
      setActiveReview(undefined);
      setSelectedFinding(undefined);
      setErrorMessage(undefined);
      setHighlightLine(undefined);
      setActiveTab('workspace');
      toast.info(`Loaded demo sample: ${sample.name}`);
    }
  };

  // Clear Editor Workspace
  const handleClear = () => {
    setCode('');
    setFilename('target.py');
    setActiveReview(undefined);
    setSelectedFinding(undefined);
    setErrorMessage(undefined);
    setHighlightLine(undefined);
    toast.info('Workspace reset');
  };

  // Synchronize Finding Selection with Editor Highlight
  const handleSelectFinding = (finding?: ReviewFinding) => {
    setSelectedFinding(finding);
    if (finding && finding.line_number) {
      setHighlightLine(finding.line_number);
      setHighlightEndLine(finding.end_line || finding.line_number);
    } else {
      setHighlightLine(undefined);
      setHighlightEndLine(undefined);
    }
  };

  // Load Historical Review
  const handleSelectHistoricalReview = (rev: ReviewResponse) => {
    setActiveReview(rev);
    setFilename(rev.filename);
    setSelectedFinding(undefined);
    setActiveTab('workspace');
    toast.info(`Loaded historical review for ${rev.filename}`);
  };

  return (
    <div className="flex h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans select-none">
      <ToastContainer />

      {/* Left Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        reviewCount={historyCount}
        backendConnected={backendConnected}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-950">
        {activeTab === 'workspace' && (
          <WorkspacePage
            code={code}
            onCodeChange={setCode}
            language={language}
            onLanguageChange={setLanguage}
            filename={filename}
            onFilenameChange={setFilename}
            onReviewSubmit={handleReviewSubmit}
            onClear={handleClear}
            isAnalyzing={isAnalyzing}
            activeReview={activeReview}
            selectedFinding={selectedFinding}
            onSelectFinding={handleSelectFinding}
            errorMessage={errorMessage}
            onDismissError={() => setErrorMessage(undefined)}
            onSelectSample={handleLoadSample}
            highlightLine={highlightLine}
            highlightEndLine={highlightEndLine}
            onJumpToLine={(line, endLine) => {
              setHighlightLine(line);
              setHighlightEndLine(endLine);
            }}
            onNewReview={() => {
              handleClear();
              setActiveTab('workspace');
            }}
          />
        )}

        {activeTab === 'history' && (
          <HistoryPage onSelectReview={handleSelectHistoricalReview} />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsPage />
        )}

        {activeTab === 'docs' && <DocsPage />}

        {activeTab === 'settings' && (
          <SettingsPage backendConnected={backendConnected} />
        )}
      </main>
    </div>
  );
};

export default App;
