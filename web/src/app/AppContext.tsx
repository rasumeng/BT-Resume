import { createContext, useContext, useReducer, useCallback, useEffect, useRef, type ReactNode } from 'react';
import type { ResumeFile } from '../types';
import { reducer, initialState, type AppState, type Action } from './reducer';
import * as api from '../services/api';
import * as resumeApi from '../services/resumeApi';

interface AppContextValue {
  state: AppState;
  dispatch: React.Dispatch<Action>;
  checkHealth: () => Promise<boolean>;
  loadResumes: () => Promise<void>;
  selectResume: (resume: ResumeFile) => Promise<void>;
  deleteResume: (filename: string) => Promise<void>;
  uploadResume: (file: File) => Promise<void>;
}

const AppContext = createContext<AppContextValue | null>(null);

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}

const HEALTH_POLL_INTERVAL = 3000;
const MAX_FAILS_BEFORE_ERROR = 4;
const BACKEND_READY_TIMEOUT_MS = 15000;
const BACKEND_READY_POLL_MS = 500;

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const healthIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const hasCompletedRef = useRef(false);
  const failCountRef = useRef(0);

  const checkHealth = useCallback(async () => {
    try {
      dispatch({ type: 'SET_BACKEND_STATUS', status: 'connecting', message: 'Connecting to backend...' });
      const health = await api.health();
      if (health.status === 'healthy') {
        failCountRef.current = 0;
        dispatch({ type: 'SET_BACKEND_STATUS', status: 'ready', message: '' });
        return true;
      }
      return false;
    } catch {
      failCountRef.current += 1;
      if (failCountRef.current >= MAX_FAILS_BEFORE_ERROR) {
        dispatch({ type: 'SET_BACKEND_STATUS', status: 'error', message: 'Backend not available' });
      }
      return false;
    }
  }, []);

  const loadResumes = useCallback(async () => {
    try {
      const resumes = await resumeApi.listResumes();
      dispatch({ type: 'SET_RESUMES', resumes });
    } catch (err) {
      console.error('Failed to load resumes:', err);
    }
  }, []);

  const selectResume = useCallback(async (resume: ResumeFile) => {
    try {
      const content = await resumeApi.getResume(resume.filename);
      dispatch({ type: 'SET_SELECTED_RESUME', resume, content });
      dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: null, error: null } });
      dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: null, error: null } });
    } catch (err) {
      console.error('Failed to load resume:', err);
      dispatch({ type: 'SET_SELECTED_RESUME', resume, content: null });
    }
  }, []);

  const deleteResume = useCallback(async (filename: string) => {
    try {
      await resumeApi.deleteResume(filename);
      dispatch({ type: 'REMOVE_RESUME', filename });
    } catch (err) {
      console.error('Failed to delete resume:', err);
    }
  }, []);

  const waitForBackendReady = useCallback(async () => {
    const deadline = Date.now() + BACKEND_READY_TIMEOUT_MS;

    while (Date.now() < deadline) {
      const healthy = await checkHealth();
      if (healthy) {
        return true;
      }

      await new Promise((resolve) => {
        window.setTimeout(resolve, BACKEND_READY_POLL_MS);
      });
    }

    return false;
  }, [checkHealth]);

  const uploadResume = useCallback(async (file: File) => {
    if (state.backendStatus !== 'ready') {
      const ready = await waitForBackendReady();
      if (!ready) {
        throw new Error('Backend is still starting up. Please try again in a moment.');
      }
    }

    await resumeApi.uploadResume(file);
    await loadResumes();
  }, [loadResumes, state.backendStatus, waitForBackendReady]);

  useEffect(() => {
    let mounted = true;

    async function init() {
      const healthy = await checkHealth();
      if (!mounted) return;

      if (healthy) {
        await loadResumes();
        if (!mounted) return;
        dispatch({ type: 'SET_PHASE', phase: 'home' });
        hasCompletedRef.current = true;
        if (healthIntervalRef.current) clearInterval(healthIntervalRef.current);
      } else {
        healthIntervalRef.current = setInterval(async () => {
          const healthyNow = await checkHealth();
          if (healthyNow && mounted && !hasCompletedRef.current) {
            hasCompletedRef.current = true;
            if (healthIntervalRef.current) clearInterval(healthIntervalRef.current);
            await loadResumes();
            if (mounted) dispatch({ type: 'SET_PHASE', phase: 'home' });
          }
        }, HEALTH_POLL_INTERVAL);
      }
    }

    init();

    return () => {
      mounted = false;
      if (healthIntervalRef.current) clearInterval(healthIntervalRef.current);
    };
  }, [checkHealth, loadResumes]);

  const value: AppContextValue = {
    state,
    dispatch,
    checkHealth,
    loadResumes,
    selectResume,
    deleteResume,
    uploadResume,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
