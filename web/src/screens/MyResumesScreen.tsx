import { useState, useCallback, useEffect } from 'react';
import { BarChart3, Check, AlertTriangle, ArrowRight } from 'lucide-react';
import { useApp } from '../app/AppContext';
import * as aiApi from '../services/aiApi';
import * as resumeApi from '../services/resumeApi';
import { track } from '../services/tracking';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import SplitPanel from '../components/layout/SplitPanel';
import ResumeList from '../components/resume/ResumeList';
import ResumePreview from '../components/resume/ResumePreview';
import UploadButton from '../components/resume/UploadButton';
import CircularGauge, { getScoreLabel } from '../components/ai/CircularGauge';
import ProgressBar from '../components/ai/ProgressBar';
import WorkflowCard from '../components/ai/WorkflowCard';
import EmptyState from '../components/shared/EmptyState';
import Overlay from '../components/shared/Overlay';
import NotificationToast from '../components/shared/NotificationToast';
import ConfirmDialog from '../components/shared/ConfirmDialog';

export default function MyResumesScreen() {
  const { state, selectResume, deleteResume, uploadResume, loadResumes, dispatch } = useApp();
  const [uploadLoading, setUploadLoading] = useState(false);
  const [grading, setGrading] = useState(false);
  const [notif, setNotif] = useState<{ type: 'success' | 'error'; title: string; message: string } | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const gradeResult = state.grade.data;

  const handleUpload = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setNotif({ type: 'error', title: 'Invalid File', message: 'Only PDF files are allowed.' });
      return;
    }
    try {
      setUploadLoading(true);
      await uploadResume(file);
      track('resume_uploaded', file.name);
    } catch {
      setNotif({ type: 'error', title: 'Upload Failed', message: 'Failed to upload resume. Please try again.' });
    } finally {
      setUploadLoading(false);
    }
  }, [uploadResume]);

  const handleGrade = useCallback(async () => {
    const selected = state.selectedResume;
    if (!selected) return;
    track('grade_resume');
    try {
      setGrading(true);
      dispatch({ type: 'SET_GRADE_STATE', state: { loading: true, data: null, error: null } });
      const text = state.selectedResumeContent;
      const isPdf = selected.filename.toLowerCase().endsWith('.pdf');
      if (isPdf) {
        const result = await aiApi.gradeResume('', selected.filename);
        dispatch({ type: 'SET_GRADE_STATE', state: { loading: false, data: result, error: null } });
      } else if (!text) {
        const content = await resumeApi.getResume(selected.filename);
        const result = await aiApi.gradeResume(content);
        dispatch({ type: 'SET_GRADE_STATE', state: { loading: false, data: result, error: null } });
      } else {
        const result = await aiApi.gradeResume(text);
        dispatch({ type: 'SET_GRADE_STATE', state: { loading: false, data: result, error: null } });
      }
    } catch {
      dispatch({ type: 'SET_GRADE_STATE', state: { loading: false, data: null, error: 'Failed to grade resume.' } });
      setNotif({ type: 'error', title: 'Grade Failed', message: 'Failed to grade resume.' });
    } finally {
      setGrading(false);
    }
  }, [dispatch, state.selectedResume, state.selectedResumeContent]);

  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return;
    track('resume_deleted', deleteTarget);
    await deleteResume(deleteTarget);
    setDeleteTarget(null);
  }, [deleteTarget, deleteResume]);

  // Poll for processing state changes so Grade button re-enables once parsing completes
  useEffect(() => {
    const hasProcessing = state.resumes.some((r) => r.processing);
    if (!hasProcessing) return;
    const interval = setInterval(() => {
      loadResumes();
    }, 3000);
    return () => clearInterval(interval);
  }, [state.resumes, loadResumes]);

  return (
    <>
      <SplitPanel
        left={
          <div className="p-3 flex flex-col gap-3 h-full overflow-auto">
            {/* Resume List Card */}
            <Card className="flex-1 flex flex-col overflow-hidden" padding="0">
              <div className="flex items-center justify-between px-4 py-3 border-b border-surface-active">
                <span className="text-[11px] font-bold text-gold uppercase tracking-wide">My Resumes</span>
                <span className="badge badge-gold" role="status" aria-label={`${state.resumes.length} resumes`}>
                  {state.resumes.length} Resume{state.resumes.length !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="flex-1 overflow-auto px-3 py-2">
                {state.resumes.length === 0 ? (
                  <EmptyState
                    title="No resumes yet"
                    description="Add your first resume to get started"
                  />
                ) : (
                  <ResumeList
                    resumes={state.resumes}
                    selectedFilename={state.selectedResume?.filename}
                    onSelect={selectResume}
                    onDelete={setDeleteTarget}
                  />
                )}
              </div>

              <div className="flex gap-2 px-4 py-3 border-t border-surface-active">
                <UploadButton
                  onUpload={handleUpload}
                  loading={uploadLoading}
                  disabled={state.backendStatus !== 'ready'}
                />
                <Button
                  variant="secondary"
                  icon={<BarChart3 size={14} />}
                  full
                  onClick={handleGrade}
                  loading={grading}
                  disabled={!state.selectedResume || state.selectedResume.processing || uploadLoading || !state.ollamaReady}
                >
                  {state.selectedResume?.processing ? 'Processing...' : 'Grade'}
                </Button>
              </div>
            </Card>

            {/* Grade Card */}
            <WorkflowCard
              eyebrow="Resume Grade"
              title={gradeResult ? getScoreLabel(gradeResult.score) : undefined}
              description={gradeResult ? 'Latest grading result from the local AI model' : 'Select a resume and tap Grade'}
            >
              {gradeResult ? (
                <div className="flex flex-col items-center gap-3 animate-fade-in">
                  <div className="flex items-center gap-4 w-full">
                    <CircularGauge score={gradeResult.score} size={90} label={getScoreLabel(gradeResult.score)} />
                    <div className="flex-1">
                      {gradeResult.strengths?.slice(0, 2).map((s, i) => (
                        <div key={i} className="flex items-start gap-1.5 mb-1">
                          <Check size={10} className="text-success shrink-0 mt-0.5" />
                          <span className="text-xs text-cream">{s}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {gradeResult.categories?.length > 0 && (
                    <div className="grid grid-cols-3 gap-2 w-full">
                      {gradeResult.categories.slice(0, 6).map((cat, idx) => (
                        <div key={cat.name} className="category-card animate-fade-in" style={{ animationDelay: `${idx * 50}ms` }}>
                          <span className="text-sm" aria-hidden="true">{cat.icon || '📊'}</span>
                          <span className="text-xs font-semibold text-cream text-center">
                            {cat.score}/{cat.max_score}
                          </span>
                          <ProgressBar value={cat.score} maxValue={cat.max_score} height="sm" />
                          <span className="text-[9px] text-text-tertiary text-center">{cat.name}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {gradeResult.ats_feedback && (
                    <div className="info-box w-full" role="status">
                      <AlertTriangle size={14} className="shrink-0 mt-0.5 text-warning" />
                      <span className="text-xs">{gradeResult.ats_feedback}</span>
                    </div>
                  )}

                  {gradeResult.improvements?.length > 0 && (
                    <div className="w-full">
                      <p className="text-[10px] font-bold text-warning uppercase tracking-wide mb-1.5">
                        Suggested Improvements
                      </p>
                      {gradeResult.improvements.slice(0, 3).map((s, i) => (
                        <div key={i} className="flex items-start gap-1.5 mb-0.5">
                          <ArrowRight size={10} className="text-warning shrink-0 mt-0.5" />
                          <span className="text-xs text-cream">{s}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <EmptyState
                  title="No Grade Yet"
                  description="Select a resume and tap 'Grade'"
                />
              )}
            </WorkflowCard>
          </div>
        }

        right={
          state.selectedResume ? (
            <ResumePreview
              text={state.selectedResumeContent ?? ''}
              filename={state.selectedResume.filename}
              pdfUrl={state.selectedResume.filename.toLowerCase().endsWith('.pdf')
                ? `/api/get-resume-pdf?filename=${encodeURIComponent(state.selectedResume.filename)}`
                : undefined}
            />
          ) : (
            <EmptyState
              title="No Resume Selected"
              description="Select a resume from the list to preview"
            />
          )
        }
      />

      {notif && <NotificationToast {...notif} onClose={() => setNotif(null)} />}
      <Overlay visible={grading} message="Grading resume..." />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Resume"
        message="Are you sure you want to delete this resume? This action cannot be undone."
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </>
  );
}
