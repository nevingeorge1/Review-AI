import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, AlertTriangle, Info, AlertOctagon } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

let toastListeners: ((t: Toast) => void)[] = [];

export const toast = {
  success: (message: string) => toastListeners.forEach(fn => fn({ id: Math.random().toString(36), type: 'success', message })),
  error:   (message: string) => toastListeners.forEach(fn => fn({ id: Math.random().toString(36), type: 'error', message })),
  info:    (message: string) => toastListeners.forEach(fn => fn({ id: Math.random().toString(36), type: 'info', message })),
};

export const ToastContainer: React.FC = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handler = (t: Toast) => {
      setToasts(prev => [...prev, t]);
      setTimeout(() => {
        setToasts(prev => prev.filter(item => item.id !== t.id));
      }, 4000);
    };
    toastListeners.push(handler);
    return () => {
      toastListeners = toastListeners.filter(fn => fn !== handler);
    };
  }, []);

  const getStyle = (type: ToastType) => {
    switch (type) {
      case 'success':
        return 'border-emerald-500/40 bg-slate-950/95 text-emerald-300 shadow-[0_4px_25px_-5px_rgba(16,185,129,0.3)]';
      case 'error':
        return 'border-rose-500/40 bg-slate-950/95 text-rose-300 shadow-[0_4px_25px_-5px_rgba(244,63,94,0.3)]';
      case 'info':
      default:
        return 'border-cyan-500/40 bg-slate-950/95 text-cyan-300 shadow-[0_4px_25px_-5px_rgba(6,182,212,0.3)]';
    }
  };

  const getIcon = (type: ToastType) => {
    switch (type) {
      case 'success': return <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />;
      case 'error':   return <AlertOctagon className="w-4 h-4 text-rose-400 flex-shrink-0" />;
      case 'info':    return <Info className="w-4 h-4 text-cyan-400 flex-shrink-0" />;
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 pointer-events-none text-[13px] font-medium">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`animate-slide-up pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-xl ${getStyle(t.type)}`}
        >
          {getIcon(t.type)}
          <span className="leading-tight text-white">{t.message}</span>
          <button
            onClick={() => setToasts(prev => prev.filter(x => x.id !== t.id))}
            className="ml-2 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};

// ─── Error Alert Banner ───────────────────────────────────────────────────────

interface ErrorBannerProps {
  message: string;
  onDismiss?: () => void;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss, onRetry }) => {
  if (!message) return null;

  const isSyntaxError = message.toLowerCase().includes('syntax');

  return (
    <div className="animate-fade-in flex items-center justify-between gap-3 px-4 py-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-200 text-[13px] font-medium">
      <div className="flex items-center gap-2.5 min-w-0">
        <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
        <span className="font-bold text-white uppercase tracking-wider text-[11.5px]">
          {isSyntaxError ? 'Syntax Error' : 'Analysis Interrupted'}:
        </span>
        <span className="text-rose-200/90 truncate">{message}</span>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-2.5 py-1 rounded-md text-[11.5px] font-semibold bg-rose-500/20 hover:bg-rose-500/30 text-white border border-rose-500/40 transition-colors cursor-pointer"
          >
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-rose-400 hover:text-white transition-colors cursor-pointer p-0.5"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
