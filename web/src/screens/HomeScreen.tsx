import { useCallback } from 'react';
import { useApp } from '../app/AppContext';
import type { Tab } from '../types';
import AppHeader from '../components/layout/AppHeader';
import StatusBanner from '../components/layout/StatusBanner';
import MyResumesScreen from './MyResumesScreen';
import PolishScreen from './PolishScreen';
import TailorScreen from './TailorScreen';
import FeedbackScreen from './FeedbackScreen';

export default function HomeScreen() {
  const { state, dispatch } = useApp();

  const handleTabChange = useCallback((tab: Tab) => {
    dispatch({ type: 'SET_TAB', tab });
  }, [dispatch]);

  return (
    <div className="flex h-full flex-col overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(201,168,76,0.08),_transparent_30%),linear-gradient(180deg,_#10100d_0%,_#0d0d0b_100%)]">
      <AppHeader
        activeTab={state.activeTab}
        onTabChange={handleTabChange}
        backendStatus={state.backendStatus}
        backendMessage={state.backendMessage}
        ollamaReady={state.ollamaReady}
        ollamaModel={state.ollamaModel}
      />

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <StatusBanner status={state.backendStatus} message={state.backendMessage} />

        <main className="min-w-0 flex-1 overflow-hidden p-3 sm:p-4 lg:p-5">
          <div className="h-full overflow-hidden rounded-2xl border border-surface-active bg-surface/70 shadow-card">
        {state.activeTab === 0 && (
          <div id="tabpanel-0" role="tabpanel" aria-labelledby="tab-0" className="h-full">
            <MyResumesScreen />
          </div>
        )}
        {state.activeTab === 1 && (
          <div id="tabpanel-1" role="tabpanel" aria-labelledby="tab-1" className="h-full">
            <PolishScreen />
          </div>
        )}
        {state.activeTab === 2 && (
          <div id="tabpanel-2" role="tabpanel" aria-labelledby="tab-2" className="h-full">
            <TailorScreen />
          </div>
        )}
        {state.activeTab === 3 && (
          <div id="tabpanel-3" role="tabpanel" aria-labelledby="tab-3" className="h-full">
            <FeedbackScreen />
          </div>
        )}
          </div>
        </main>
      </div>
    </div>
  );
}
