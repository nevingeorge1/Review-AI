import React, { useRef, useEffect, useState } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import {
  Play, RotateCcw, Copy, Check, FileCode, AlertTriangle, Loader2
} from 'lucide-react';
import { Language, ReviewFinding } from '../../types';

interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  language: Language;
  onLanguageChange: (lang: Language) => void;
  filename: string;
  onFilenameChange: (name: string) => void;
  onReviewSubmit: () => void;
  onClear: () => void;
  isAnalyzing: boolean;
  highlightLine?: number;
  highlightEndLine?: number;
  findings?: ReviewFinding[];
}

const LANGUAGE_OPTIONS: { value: Language; label: string; monacoLang: string }[] = [
  { value: 'python',     label: 'Python',     monacoLang: 'python' },
  { value: 'javascript', label: 'JavaScript', monacoLang: 'javascript' },
  { value: 'typescript', label: 'TypeScript', monacoLang: 'typescript' },
  { value: 'go',         label: 'Go',         monacoLang: 'go' },
  { value: 'rust',       label: 'Rust',       monacoLang: 'rust' },
  { value: 'java',       label: 'Java',       monacoLang: 'java' },
  { value: 'cpp',        label: 'C++',        monacoLang: 'cpp' },
];

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  language,
  onLanguageChange,
  filename,
  onFilenameChange,
  onReviewSubmit,
  onClear,
  isAnalyzing,
  highlightLine,
  highlightEndLine,
  findings = [],
}) => {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const decorationsRef = useRef<string[]>([]);
  const [copied, setCopied] = useState(false);
  const [cursorPos, setCursorPos] = useState({ ln: 1, col: 1 });

  const lineCount = code ? code.split('\n').length : 0;
  const byteSize = new Blob([code]).size;
  const isTooLarge = lineCount > 500 || byteSize > 65536;
  const isEmpty = !code.trim();

  const monacoLang = LANGUAGE_OPTIONS.find(o => o.value === language)?.monacoLang || 'python';

  const handleMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Define custom clean editor theme
    monaco.editor.defineTheme('reviewai-saas', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '64748b', fontStyle: 'italic' },
        { token: 'keyword', foreground: '38bdf8', fontStyle: 'bold' },
        { token: 'string', foreground: '34d399' },
        { token: 'number', foreground: 'fbbf24' },
        { token: 'type', foreground: '818cf8' },
        { token: 'function', foreground: '60a5fa' },
      ],
      colors: {
        'editor.background': '#090e1a',
        'editor.foreground': '#e2e8f0',
        'editorLineNumber.foreground': '#334155',
        'editorLineNumber.activeForeground': '#38bdf8',
        'editor.lineHighlightBackground': '#0f172a',
        'editor.selectionBackground': '#1e293b',
        'editorGutter.background': '#090e1a',
        'editorCursor.foreground': '#38bdf8',
      },
    });

    monaco.editor.setTheme('reviewai-saas');

    editor.onDidChangeCursorPosition((e: any) => {
      setCursorPos({ ln: e.position.lineNumber, col: e.position.column });
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (!isAnalyzing && !isEmpty && !isTooLarge) {
        onReviewSubmit();
      }
    });
  };

  useEffect(() => {
    if (!editorRef.current) return;
    const editor = editorRef.current;

    const newDecorations: any[] = [];

    findings.forEach(f => {
      if (f.line_number) {
        const isSelected = f.line_number === highlightLine;
        const colorClass = isSelected
          ? 'monaco-finding-active'
          : f.severity === 'critical'
          ? 'monaco-finding-critical'
          : f.severity === 'high'
          ? 'monaco-finding-high'
          : 'monaco-finding-medium';

        newDecorations.push({
          range: {
            startLineNumber: f.line_number,
            startColumn: 1,
            endLineNumber: f.end_line || f.line_number,
            endColumn: 9999,
          },
          options: {
            isWholeLine: true,
            className: colorClass,
            overviewRuler: {
              color: isSelected ? '#06b6d4' : f.severity === 'critical' ? '#ef4444' : '#f97316',
              position: 1,
            },
          },
        });
      }
    });

    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, newDecorations);

    if (highlightLine) {
      editor.revealLineInCenter(highlightLine);
    }
  }, [highlightLine, highlightEndLine, findings]);

  const handleCopy = () => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-slate-950/80 border border-white/[0.08] rounded-2xl shadow-card overflow-hidden select-none">
      {/* Editor Header Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/[0.06] bg-slate-900/60 backdrop-blur-md flex-shrink-0">
        {/* File & Language Selector */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08]">
            <FileCode className="w-4 h-4 text-cyan-400 flex-shrink-0" />
            <input
              type="text"
              value={filename}
              onChange={e => onFilenameChange(e.target.value)}
              className="text-[13px] font-medium text-slate-200 bg-transparent border-none focus:outline-none w-36 font-mono"
              placeholder="filename.py"
              aria-label="Target filename"
            />
          </div>

          <select
            value={language}
            onChange={e => onLanguageChange(e.target.value as Language)}
            className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-[12.5px] font-medium text-slate-300 focus:outline-none focus:border-cyan-400 cursor-pointer"
            aria-label="Programming Language"
          >
            {LANGUAGE_OPTIONS.map(o => (
              <option key={o.value} value={o.value} className="bg-slate-900">{o.label}</option>
            ))}
          </select>
        </div>

        {/* Right: Actions & Primary CTA */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            disabled={isEmpty}
            className="btn-secondary-modern text-[12px] p-2 disabled:opacity-30"
            title="Copy Code"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={onClear}
            disabled={isEmpty || isAnalyzing}
            className="btn-secondary-modern text-[12px] p-2 disabled:opacity-30"
            title="Clear Code"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {/* Primary Action Button */}
          <button
            onClick={onReviewSubmit}
            disabled={isEmpty || isAnalyzing || isTooLarge}
            className="btn-primary-gradient min-w-[155px]"
            title="Press Ctrl+Enter or click to analyze"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze Code →</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Exceeded Limit Banner */}
      {isTooLarge && (
        <div className="flex items-center gap-2 px-4 py-2 bg-rose-500/10 border-b border-rose-500/20 text-rose-300 text-[12.5px] flex-shrink-0">
          <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>Code exceeds the maximum limit of 500 lines or 64 KB.</span>
        </div>
      )}

      {/* Monaco Canvas */}
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          language={monacoLang}
          value={code}
          theme="reviewai-saas"
          onChange={val => onChange(val || '')}
          onMount={handleMount}
          options={{
            minimap: { enabled: false },
            fontSize: 13.5,
            fontFamily: '"JetBrains Mono", "Fira Code", Consolas, monospace',
            fontLigatures: true,
            lineNumbers: 'on',
            glyphMargin: true,
            scrollBeyondLastLine: false,
            readOnly: isAnalyzing,
            automaticLayout: true,
            tabSize: 4,
            renderLineHighlight: 'all',
            overviewRulerBorder: false,
            padding: { top: 12, bottom: 12 },
            scrollbar: {
              verticalScrollbarSize: 6,
              horizontalScrollbarSize: 6,
            },
          }}
        />
      </div>

      {/* Bottom Status Bar */}
      <div className="px-4 py-1.5 border-t border-white/[0.06] bg-slate-900/60 flex items-center justify-between text-[12px] text-slate-400 flex-shrink-0">
        <div className="flex items-center gap-3">
          <span>Ln {cursorPos.ln}, Col {cursorPos.col}</span>
          <span>·</span>
          <span>{lineCount} lines</span>
          <span>·</span>
          <span>{(byteSize / 1024).toFixed(1)} KB</span>
        </div>

        <div className="flex items-center gap-3 font-medium">
          <span className="text-slate-300">{language.toUpperCase()}</span>
          <span>·</span>
          <span className="hidden sm:inline text-cyan-400">
            <kbd className="px-1.5 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] text-[11px] font-mono">Ctrl+Enter</kbd> to analyze
          </span>
        </div>
      </div>
    </div>
  );
};
