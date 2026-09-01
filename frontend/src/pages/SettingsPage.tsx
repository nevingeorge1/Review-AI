import React from 'react';
import { Header } from '../components/layout/Navbar';
import {
  Server,
  Cpu,
  Shield,
  Lock,
} from 'lucide-react';

interface SettingsPageProps {
  backendConnected: boolean;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ backendConnected }) => {
  return (
    <div className="flex flex-col h-full overflow-hidden bg-ambient-glow select-none">
      <Header
        pageTitle="Settings & Subsystems"
        pageSubtitle="Hardware configuration, model endpoints, and privacy parameters"
      />

      <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-5xl mx-auto w-full">
        {/* SECTION 1: BACKEND API GATEWAY */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
            <div className="flex items-center gap-2.5 text-cyan-400">
              <Server className="w-5 h-5" />
              <h3 className="text-base font-bold text-white tracking-tight">
                Backend API Gateway
              </h3>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] font-semibold bg-white/[0.04] border border-white/[0.08]">
              <span className={`w-2 h-2 rounded-full ${backendConnected ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-rose-500'}`} />
              <span className={backendConnected ? 'text-emerald-400' : 'text-rose-400'}>
                {backendConnected ? 'Port 8000 Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Framework</span>
              <p className="text-white font-semibold text-[13.5px]">FastAPI / Uvicorn</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">API Prefix</span>
              <p className="text-white font-semibold text-[13.5px]">/api/v1</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Max Input Lines</span>
              <p className="text-cyan-300 font-semibold text-[13.5px]">500 Lines</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Max Payload</span>
              <p className="text-cyan-300 font-semibold text-[13.5px]">64 KB</p>
            </div>
          </div>
        </div>

        {/* SECTION 2: LOCAL LLM REASONING LAYER */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
            <div className="flex items-center gap-2.5 text-indigo-400">
              <Cpu className="w-5 h-5" />
              <h3 className="text-base font-bold text-white tracking-tight">
                Local AI Reasoning Subsystem
              </h3>
            </div>
            <span className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-indigo-300 bg-indigo-500/10 px-3 py-1 rounded-full border border-indigo-500/25">
              <Lock className="w-3.5 h-3.5" />
              <span>On-Device Privacy</span>
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Inference Engine</span>
              <p className="text-white font-semibold text-[13.5px]">Ollama Local Daemon</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Target Model</span>
              <p className="text-indigo-300 font-semibold text-[13.5px]">qwen2.5-coder:7b</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Base URL</span>
              <p className="text-white font-semibold text-[13.5px]">localhost:11434</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Timeout Limit</span>
              <p className="text-white font-semibold text-[13.5px]">60.0s</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Offline Resilience</span>
              <p className="text-emerald-400 font-semibold text-[13.5px]">Automatic Fallback</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Output Grammar</span>
              <p className="text-white font-semibold text-[13.5px]">Strict JSON Schema</p>
            </div>
          </div>
        </div>

        {/* SECTION 3: DETERMINISTIC STATIC ANALYSIS SUBSYSTEM */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
            <div className="flex items-center gap-2.5 text-emerald-400">
              <Shield className="w-5 h-5" />
              <h3 className="text-base font-bold text-white tracking-tight">
                Deterministic Static Analyzers
              </h3>
            </div>
            <span className="text-[12px] text-emerald-400 font-semibold">
              Zero Code Execution
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Custom AST Rules</span>
              <p className="text-emerald-400 font-semibold text-[13.5px]">15 Checkers</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">AST Visitor</span>
              <p className="text-white font-semibold text-[13.5px]">Single-Pass Node</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Ruff Linter</span>
              <p className="text-white font-semibold text-[13.5px]">Isolated JSON CLI</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] space-y-1">
              <span className="text-[11.5px] text-slate-400">Bandit Security</span>
              <p className="text-white font-semibold text-[13.5px]">Isolated Security CLI</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
