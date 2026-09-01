import React, { useState } from 'react';
import { Header } from '../components/layout/Navbar';
import {
  Shield,
  Sparkles,
  CheckCircle2,
  Search,
  BookOpen,
} from 'lucide-react';
import { SeverityBadge } from '../components/common/Badge';

interface RuleDef {
  id: string;
  name: string;
  cat: string;
  sev: 'critical' | 'high' | 'medium' | 'low' | 'info';
  desc: string;
  astPattern: string;
}

const AST_RULES: RuleDef[] = [
  { id: 'RULE-001', name: 'Dangerous eval()', cat: 'Security', sev: 'high', desc: 'Direct execution of dynamic Python expressions', astPattern: 'ast.Call(func.id == "eval")' },
  { id: 'RULE-002', name: 'Dangerous exec()', cat: 'Security', sev: 'high', desc: 'Execution of dynamic arbitrary Python statements', astPattern: 'ast.Call(func.id == "exec")' },
  { id: 'RULE-003', name: 'Dynamic __import__()', cat: 'Security', sev: 'medium', desc: 'Dynamic module loading vulnerability risk', astPattern: 'ast.Call(func.id == "__import__")' },
  { id: 'RULE-004', name: 'os.system() Shell Call', cat: 'Security', sev: 'high', desc: 'Unsanitized shell invocation risk (CWE-78)', astPattern: 'ast.Attribute(value.id == "os", attr == "system")' },
  { id: 'RULE-005', name: 'subprocess(shell=True)', cat: 'Security', sev: 'high', desc: 'Process execution with shell expansion enabled', astPattern: 'ast.Call(keywords contains shell=True)' },
  { id: 'RULE-006', name: 'pickle.loads() Deserialization', cat: 'Security', sev: 'high', desc: 'Arbitrary remote code execution on untrusted payload', astPattern: 'ast.Attribute(value.id == "pickle", attr == "loads")' },
  { id: 'RULE-007', name: 'Broad except Exception:', cat: 'Maintainability', sev: 'low', desc: 'Catches broad Exception base class and masks bugs', astPattern: 'ast.ExceptHandler(type.id == "Exception")' },
  { id: 'RULE-008', name: 'Mutable Default Argument', cat: 'Bug', sev: 'high', desc: 'List/Dict/Set default retained across function calls', astPattern: 'ast.FunctionDef(defaults contains List/Dict/Set)' },
  { id: 'RULE-009', name: 'Bare except:', cat: 'Maintainability', sev: 'medium', desc: 'Catches BaseException including KeyboardInterrupt', astPattern: 'ast.ExceptHandler(type is None)' },
  { id: 'RULE-010', name: 'High Cyclomatic Complexity', cat: 'Maintainability', sev: 'medium', desc: 'Decision branch complexity exceeds threshold (>10)', astPattern: 'Count(If + While + For + Except + BoolOp) > 10' },
  { id: 'RULE-011', name: 'Deep Nesting Depth', cat: 'Maintainability', sev: 'low', desc: 'Control-flow nesting exceeds threshold (>4)', astPattern: 'MaxIndentLevel(block) > 4' },
  { id: 'RULE-012', name: 'Too Many Parameters', cat: 'Maintainability', sev: 'low', desc: 'Function parameter count exceeds threshold (>6)', astPattern: 'len(FunctionDef.args.args) > 6' },
  { id: 'RULE-013', name: 'Hardcoded Secret / API Key', cat: 'Security', sev: 'high', desc: 'Static secret or token string literal detected', astPattern: 'Regex(Constant.value matches secret_patterns)' },
  { id: 'RULE-014', name: 'Dynamic SQL Formatting', cat: 'Security', sev: 'high', desc: 'String interpolation in database execute method', astPattern: 'ast.Call(func.attr == "execute", args contains BinOp/Format)' },
  { id: 'RULE-015', name: 'Quadratic Loop O(N^2)', cat: 'Performance', sev: 'medium', desc: 'Nested loop linear scan membership check', astPattern: 'Nested(For/While, Compare(In, List))' },
];

export const DocsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [filterCat, setFilterCat] = useState('all');

  const filteredRules = AST_RULES.filter(r => {
    if (filterCat !== 'all' && r.cat.toLowerCase() !== filterCat.toLowerCase()) return false;
    if (search) {
      const q = search.toLowerCase();
      return r.id.toLowerCase().includes(q) || r.name.toLowerCase().includes(q) || r.desc.toLowerCase().includes(q);
    }
    return true;
  });

  return (
    <div className="flex flex-col h-full overflow-hidden bg-ambient-glow select-none">
      <Header
        pageTitle="Rules Engine"
        pageSubtitle="15 Deterministic AST Intelligence Rules & Invariants"
      />

      <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* ARCHITECTURE SUMMARY */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="glass-card p-6 space-y-2.5">
            <div className="flex items-center gap-2 text-cyan-400">
              <Sparkles className="w-5 h-5" />
              <h3 className="text-base font-bold text-white tracking-tight">Hybrid Intelligence Architecture</h3>
            </div>
            <p className="text-[13px] text-slate-300 leading-relaxed">
              Traditional linters lack semantic context, while pure LLMs frequently hallucinate incorrect line numbers.
            </p>
            <p className="text-[13px] text-slate-300 leading-relaxed">
              <strong className="text-cyan-300 font-semibold">ReviewAI combines both:</strong> 15 AST rules, Ruff, and Bandit establish ground-truth facts. Local Qwen2.5-Coder then evaluates root causes, contextual severity, and suggests verified fixes.
            </p>
          </div>

          <div className="glass-card p-6 space-y-2.5">
            <div className="flex items-center gap-2 text-emerald-400">
              <Shield className="w-5 h-5" />
              <h3 className="text-base font-bold text-white tracking-tight">Security Invariants</h3>
            </div>
            <ul className="space-y-2 text-[13px] text-slate-300">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                <span><strong className="text-white">Zero Code Execution:</strong> Source code is strictly parsed as data and never executed.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                <span><strong className="text-white">Prompt Injection Defense:</strong> String literals & comments are sanitized before prompt formatting.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                <span><strong className="text-white">Local-First Privacy:</strong> Runs 100% on-device via Ollama without third-party cloud data transmission.</span>
              </li>
            </ul>
          </div>
        </div>

        {/* 15 BUILT-IN RULES CATALOG */}
        <div className="glass-card overflow-hidden flex flex-col space-y-3">
          <div className="p-5 border-b border-white/[0.06] flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-900/60">
            <div className="flex items-center gap-2.5 text-white">
              <BookOpen className="w-5 h-5 text-cyan-400" />
              <h3 className="text-base font-bold tracking-tight">
                Built-in AST Rules Catalog
              </h3>
            </div>

            <div className="flex items-center gap-2.5">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Filter rules..."
                  className="pl-9 pr-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-[12.5px] text-slate-200 focus:outline-none focus:border-cyan-400 w-44 transition-colors"
                />
              </div>

              <select
                value={filterCat}
                onChange={e => setFilterCat(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-[12.5px] font-medium text-slate-300 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="all" className="bg-slate-900">All Categories</option>
                <option value="security" className="bg-slate-900">Security</option>
                <option value="bug" className="bg-slate-900">Reliability</option>
                <option value="maintainability" className="bg-slate-900">Maintainability</option>
                <option value="performance" className="bg-slate-900">Performance</option>
              </select>
            </div>
          </div>

          <div className="p-4 space-y-2.5">
            {filteredRules.map(rule => (
              <div
                key={rule.id}
                className="p-4 rounded-xl bg-slate-900/40 border border-white/[0.04] hover:border-white/[0.1] transition-colors flex flex-col md:flex-row md:items-center justify-between gap-3"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-cyan-400 font-bold font-mono text-[13px]">{rule.id}</span>
                  <SeverityBadge severity={rule.sev} />
                  <span className="font-semibold text-[14px] text-white truncate">{rule.name}</span>
                  <span className="text-[13px] text-slate-400 hidden lg:inline">
                    — {rule.desc}
                  </span>
                </div>

                <div className="flex items-center gap-2.5 flex-shrink-0">
                  <span className="text-[11.5px] font-medium text-slate-400 uppercase bg-white/[0.04] px-2 py-0.5 rounded-md">
                    {rule.cat}
                  </span>
                  <code className="text-[12px] font-mono text-emerald-400 bg-slate-950 px-2.5 py-1 rounded-md border border-emerald-500/20 truncate max-w-[280px]">
                    {rule.astPattern}
                  </code>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
