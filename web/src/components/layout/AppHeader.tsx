import { useRef } from 'react';
import { FileText, Sparkles, Target, MessageSquare } from 'lucide-react';
import type { Tab } from '../../types';
import { track } from '../../services/tracking';

const TABS: { id: Tab; label: string; icon: typeof FileText }[] = [
  { id: 0, label: 'My Resumes', icon: FileText },
  { id: 1, label: 'Polish', icon: Sparkles },
  { id: 2, label: 'Tailor', icon: Target },
  { id: 3, label: 'Feedback', icon: MessageSquare },
];

interface AppHeaderProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
  backendStatus: string;
  backendMessage: string;
}

export default function AppHeader({
  activeTab,
  onTabChange,
  backendStatus,
  backendMessage,
}: AppHeaderProps) {
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const focusTab = (index: number) => {
    const nextTab = TABS[index];
    if (!nextTab) return;
    track('tab_changed', nextTab.label);
    onTabChange(nextTab.id);
    tabRefs.current[index]?.focus();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
      event.preventDefault();
      focusTab((index + 1) % TABS.length);
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
      event.preventDefault();
      focusTab((index - 1 + TABS.length) % TABS.length);
    }
  };

  const statusDot = (
    <span
      className={`w-2 h-2 rounded-full shrink-0 ${
        backendStatus === 'ready'
          ? 'bg-success'
          : backendStatus === 'connecting'
            ? 'bg-warning'
            : 'bg-error'
      }`}
    />
  );

  return (
    <header className="flex w-full flex-col border-b border-surface-active bg-surface/90 shadow-card backdrop-blur-sm">
      <div className="flex items-center gap-3 px-3 py-2">
        <img src="/BTR-Logo.svg" alt="Beyond The Resume" className="h-16 w-auto" />
        <span className="text-sm font-bold text-cream truncate">Beyond The Resume</span>
        {backendMessage && (
          <span className="hidden sm:inline text-xs text-text-tertiary truncate">{backendMessage}</span>
        )}

        <nav role="tablist" aria-label="Main navigation" className="flex flex-1 justify-center gap-1 flex-wrap">
          {TABS.map(({ id, label, icon: Icon }) => {
            const isActive = activeTab === id;
            const tabIndex = TABS.findIndex((tab) => tab.id === id);
            return (
              <button
                key={id}
                role="tab"
                aria-selected={isActive}
                aria-controls={`tabpanel-${id}`}
                className={`tab whitespace-nowrap ${isActive ? 'tab-active' : ''}`}
                ref={(node) => {
                  tabRefs.current[tabIndex] = node;
                }}
                onKeyDown={(event) => handleKeyDown(event, tabIndex)}
                onClick={() => { track('tab_changed', label); onTabChange(id); }}
              >
                <Icon size={14} />
                <span>{label}</span>
              </button>
            );
          })}
        </nav>

        <div>{statusDot}</div>
      </div>
    </header>
  );
}
