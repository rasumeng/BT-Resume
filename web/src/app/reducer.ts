import type { AnalysisData, AppPhase, AsyncState, BackendStatus, GradeResult, PolishResult, ResumeFile, Tab } from '../types';

export interface AppState {
  phase: AppPhase;
  backendStatus: BackendStatus;
  backendMessage: string;
  ollamaReady: boolean;
  ollamaModel: string;
  resumes: ResumeFile[];
  selectedResume: ResumeFile | null;
  selectedResumeContent: string | null;
  activeTab: Tab;
  grade: AsyncState<GradeResult>;
  polish: AsyncState<PolishResult>;
  tailor: AsyncState<AnalysisData>;
  errorMessage: string | null;
}

export type Action =
  | { type: 'SET_PHASE'; phase: AppPhase }
  | { type: 'SET_BACKEND_STATUS'; status: BackendStatus; message?: string }
  | { type: 'SET_RESUMES'; resumes: ResumeFile[] }
  | { type: 'SET_SELECTED_RESUME'; resume: ResumeFile | null; content?: string | null }
  | { type: 'SET_TAB'; tab: Tab }
  | { type: 'SET_GRADE_STATE'; state: AsyncState<GradeResult> }
  | { type: 'SET_POLISH_STATE'; state: AsyncState<PolishResult> }
  | { type: 'SET_TAILOR_STATE'; state: AsyncState<AnalysisData> }
  | { type: 'SET_OLLAMA_STATUS'; ready: boolean; model?: string }
  | { type: 'ADD_RESUME'; resume: ResumeFile }
  | { type: 'REMOVE_RESUME'; filename: string }
  | { type: 'SET_ERROR'; error: string };

export const initialState: AppState = {
  phase: 'setup',
  backendStatus: 'disconnected',
  backendMessage: '',
  ollamaReady: false,
  ollamaModel: 'mistral:7b',
  resumes: [],
  selectedResume: null,
  selectedResumeContent: null,
  activeTab: 0,
  grade: { loading: false, data: null, error: null },
  polish: { loading: false, data: null, error: null },
  tailor: { loading: false, data: null, error: null },
  errorMessage: null,
};

export function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_PHASE':
      return { ...state, phase: action.phase };

    case 'SET_BACKEND_STATUS':
      return {
        ...state,
        backendStatus: action.status,
        backendMessage: action.message ?? state.backendMessage,
      };

    case 'SET_RESUMES':
      return { ...state, resumes: action.resumes };

    case 'SET_SELECTED_RESUME':
      return {
        ...state,
        selectedResume: action.resume,
        selectedResumeContent:
          action.content !== undefined ? action.content : state.selectedResumeContent,
      };

    case 'SET_TAB':
      return { ...state, activeTab: action.tab };

    case 'SET_GRADE_STATE':
      return { ...state, grade: action.state };

    case 'SET_POLISH_STATE':
      return { ...state, polish: action.state };

    case 'SET_TAILOR_STATE':
      return { ...state, tailor: action.state };

    case 'SET_OLLAMA_STATUS':
      return {
        ...state,
        ollamaReady: action.ready,
        ollamaModel: action.model ?? state.ollamaModel,
      };

    case 'ADD_RESUME':
      return { ...state, resumes: [...state.resumes, action.resume] };

    case 'REMOVE_RESUME':
      return {
        ...state,
        resumes: state.resumes.filter((r) => r.filename !== action.filename),
        selectedResume:
          state.selectedResume?.filename === action.filename ? null : state.selectedResume,
        selectedResumeContent:
          state.selectedResume?.filename === action.filename
            ? null
            : state.selectedResumeContent,
      };

    case 'SET_ERROR':
      return { ...state, errorMessage: action.error, phase: 'error' };

    default:
      return state;
  }
}
