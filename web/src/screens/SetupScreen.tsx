import { ArrowRight, CheckCircle2, RefreshCw, Shield, Sparkles } from 'lucide-react';
import { useApp } from '../app/AppContext';
import Button from '../components/ui/Button';
import { track } from '../services/tracking';

export default function SetupScreen() {
  const { state, checkHealth, dispatch } = useApp();

  const isReady = state.backendStatus === 'ready';
  const isConnecting = state.backendStatus === 'connecting' || state.backendStatus === 'disconnected';

  const statusLabel = isReady
    ? 'Workspace ready'
    : isConnecting
      ? 'Checking local services'
      : 'Backend needs attention';

  const statusDescription = isReady
    ? 'The local backend is online and the web workspace can continue.'
    : 'The app is waiting for the local backend to respond before opening the main workspace.';

  const handleOpenWorkspace = () => {
    track('workspace_opened');
    dispatch({ type: 'SET_PHASE', phase: 'home' });
  };

  return (
    <div className="h-full overflow-auto bg-[radial-gradient(circle_at_top,_rgba(201,168,76,0.12),_transparent_36%),linear-gradient(180deg,_#11110e_0%,_#0d0d0b_100%)] px-6 py-10">
      <div className="mx-auto flex min-h-full w-full max-w-5xl flex-col justify-center gap-8 lg:flex-row lg:items-center">
        <div className="max-w-xl space-y-5">
          <div className="inline-flex items-center gap-2 rounded-full border border-gold/20 bg-surface/80 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-gold">
            <Sparkles size={14} />
            Local web workspace
          </div>

          <div className="space-y-3">
            <h1 className="text-3xl font-bold tracking-tight text-cream sm:text-4xl">
              Beyond The Resume
            </h1>
            <p className="max-w-prose text-sm leading-6 text-text-secondary sm:text-base">
              A private, local-first resume workspace inspired by OpenWebUI. The browser app keeps
              the interface simple while the backend handles resume storage, AI workflows, and PDF
              generation.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            {[
              'Single reducer-owned state tree',
              'Normalized service responses only',
              'Shared AI wizard infrastructure',
            ].map((item) => (
              <div key={item} className="rounded-xl border border-surface-active bg-surface/80 p-4 text-sm text-text-secondary shadow-card">
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="w-full max-w-md rounded-2xl border border-gold/15 bg-surface/90 p-6 shadow-card backdrop-blur-sm sm:p-8">
          <div className="flex items-center gap-3">
            <div className={`flex h-12 w-12 items-center justify-center rounded-full ${isReady ? 'bg-success/15' : 'bg-gold/15'}`}>
              {isReady ? <CheckCircle2 className="text-success" size={24} /> : <Shield className="text-gold" size={24} />}
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gold">Setup status</p>
              <h2 className="text-xl font-bold text-cream">{statusLabel}</h2>
            </div>
          </div>

          <p className="mt-4 text-sm leading-6 text-text-secondary">{statusDescription}</p>

          <div className="mt-6 space-y-3 rounded-xl border border-surface-active bg-background/50 p-4">
            <div className="flex items-center justify-between gap-4 text-sm">
              <span className="text-text-secondary">Backend</span>
              <span className={isReady ? 'text-success' : 'text-warning'}>{state.backendStatus}</span>
            </div>
            <div className="flex items-center justify-between gap-4 text-sm">
              <span className="text-text-secondary">Phase</span>
              <span className="text-cream">{state.phase}</span>
            </div>
            <div className="flex items-center justify-between gap-4 text-sm">
              <span className="text-text-secondary">Workflow</span>
              <span className="text-cream">Resume workspace</span>
            </div>
          </div>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Button
              variant="secondary"
              icon={<RefreshCw size={14} />}
              onClick={checkHealth}
              full
            >
              Recheck
            </Button>
            <Button
              variant="primary"
              icon={<ArrowRight size={14} />}
              onClick={handleOpenWorkspace}
              disabled={!isReady}
              full
            >
              Open Workspace
            </Button>
          </div>

          <p className="mt-4 text-xs leading-5 text-text-tertiary">
            If the backend is still starting, keep this page open and retry after a moment.
          </p>
        </div>
      </div>
    </div>
  );
}
