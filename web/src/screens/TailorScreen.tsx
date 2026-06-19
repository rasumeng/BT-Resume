import { useState, useCallback, useEffect, useRef } from 'react';
import { FileText, BarChart3, Edit, Download, RefreshCw, Target } from 'lucide-react';
import { useApp } from '../app/AppContext';
import * as resumeApi from '../services/resumeApi';
import * as aiApi from '../services/aiApi';
import { track } from '../services/tracking';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Textarea from '../components/ui/Textarea';
import SegmentedControl from '../components/ui/SegmentedControl';
import SplitPanel from '../components/layout/SplitPanel';
import StepWizard from '../components/ai/StepWizard';
import IntensitySelector from '../components/ai/IntensitySelector';
import TailorAnalysis from '../components/ai/TailorAnalysis';
import ResumeSelect from '../components/resume/ResumeSelect';
import ResumePreview from '../components/resume/ResumePreview';
import Overlay from '../components/shared/Overlay';
import NotificationToast from '../components/shared/NotificationToast';
import Input from '../components/ui/Input';

const INTENSITY_OPTIONS = [
  { label: 'Light', value: 'light' },
  { label: 'Medium', value: 'medium' },
  { label: 'Heavy', value: 'heavy' },
];

const STEPS = [
  { label: 'Details', icon: <FileText size={14} /> },
  { label: 'Analysis', icon: <BarChart3 size={14} /> },
  { label: 'Tailor', icon: <Edit size={14} /> },
  { label: 'Result', icon: <Target size={14} /> },
];

const CHAR_LIMIT_JD = 10000;

export default function TailorScreen() {
  const { state, selectResume, dispatch } = useApp();
  const [intensity, setIntensity] = useState('medium');
  const [jobPosition, setJobPosition] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [phase, setPhase] = useState<'input' | 'analysis' | 'result'>('input');
  const [notif, setNotif] = useState<{ type: 'success' | 'error'; title: string; message: string } | null>(null);
  const [showTailored, setShowTailored] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);

  const prevResumeRef = useRef(state.selectedResume?.filename);

  useEffect(() => {
    const current = state.selectedResume?.filename;
    if (prevResumeRef.current && prevResumeRef.current !== current) {
      setPhase('input');
      setShowTailored(false);
      setGeneratingPdf(false);
    }
    prevResumeRef.current = current;
  }, [state.selectedResume?.filename]);

  const phaseToStep: Record<string, number> = { input: 1, analysis: 2, result: 4 };
  const currentStep = phaseToStep[phase] || 1;
  const analysis = state.tailor.data;
  const tailoredPdfName = state.tailor.data?.tailoredPdfName ?? null;
  const canAnalyze = !!state.selectedResume && !!jobDescription.trim() && phase === 'input' && state.ollamaReady;
  const canTailor = !!analysis && phase === 'analysis' && state.ollamaReady;
  const isShowingTailored = phase === 'result' && showTailored;
  const previewFilename = tailoredPdfName
    ? tailoredPdfName
    : (state.selectedResume?.filename?.toLowerCase().endsWith('.pdf')
        ? state.selectedResume.filename
        : null
      );
  const previewSource = tailoredPdfName ? 'temp' : 'resumes';
  const previewPdfUrl = previewFilename
    ? `/api/get-resume-pdf?filename=${encodeURIComponent(previewFilename)}&source=${previewSource}`
    : undefined;

  const handleAnalyze = useCallback(async () => {
    const selected = state.selectedResume;
    if (!selected || !jobDescription.trim()) return;

    dispatch({ type: 'SET_TAILOR_STATE', state: { loading: true, data: null, error: null } });

    let resumeText = state.selectedResumeContent;
    if (!resumeText) {
      try {
        resumeText = await resumeApi.getResume(selected.filename);
      } catch {
        dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: null, error: 'Failed to load resume content.' } });
        setNotif({ type: 'error', title: 'Error', message: 'Failed to load resume content.' });
        return;
      }
    }

    track('fit_analysis', jobPosition || 'unknown');

    try {
      const finalResult = await aiApi.analyzeFit(resumeText, jobDescription, {
        jobPosition,
        companyName,
      });
      dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: finalResult, error: null } });
      setPhase('analysis');
    } catch {
      dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: null, error: 'Failed to analyze fit.' } });
      setNotif({ type: 'error', title: 'Error', message: 'Failed to analyze fit.' });
    }
  }, [dispatch, state.selectedResume, state.selectedResumeContent, jobDescription, jobPosition, companyName]);

  const handleTailor = useCallback(async () => {
    const selected = state.selectedResume;
    if (!selected || !jobDescription.trim()) return;

    dispatch({ type: 'SET_TAILOR_STATE', state: { loading: true, data: analysis ?? null, error: null } });

    let resumeText = state.selectedResumeContent;
    if (!resumeText) {
      try {
        resumeText = await resumeApi.getResume(selected.filename);
      } catch {
        dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: analysis ?? null, error: 'Failed to load resume content.' } });
        setNotif({ type: 'error', title: 'Error', message: 'Failed to load resume content.' });
        return;
      }
    }

    track('tailor', intensity);

    try {
      const result = await aiApi.tailorResume(resumeText, jobDescription, intensity, {
        jobPosition,
        companyName,
      });
      dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: result, error: null } });
      setPhase('result');

      // Auto-generate PDF preview (like Flutter does) — keep overlay during generation
      if (result.tailored_resume) {
        setGeneratingPdf(true);
        try {
          const pdfResult = await resumeApi.saveTextPdf(selected.filename, result.tailored_resume);
          dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: { ...result, tailoredPdfName: pdfResult.filename }, error: null } });
          setShowTailored(true);
        } catch {
          dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: { ...result, tailoredPdfName: undefined }, error: null } });
          setNotif({ type: 'error', title: 'Preview Unavailable', message: 'Could not generate PDF preview. You can still download the text version.' });
        }
        setGeneratingPdf(false);
      } else {
        setShowTailored(true);
      }

      setNotif({ type: 'success', title: 'Tailoring Complete', message: 'Your resume has been tailored!' });
    } catch {
      dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: analysis ?? null, error: 'Failed to tailor resume.' } });
      setNotif({ type: 'error', title: 'Error', message: 'Failed to tailor resume.' });
    }
  }, [analysis, dispatch, state.selectedResume, state.selectedResumeContent, jobDescription, intensity, jobPosition, companyName]);

  const handleDownload = useCallback(() => {
    const pdfName = tailoredPdfName;
    if (!pdfName) return;
    track('tailor_downloaded', pdfName);
    const a = document.createElement('a');
    a.href = `/api/get-resume-pdf?filename=${encodeURIComponent(pdfName)}&download=1&source=temp`;
    a.download = pdfName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [tailoredPdfName]);

  const handleReset = () => {
    setPhase('input');
    dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: null, error: null } });
    setShowTailored(false);
    setGeneratingPdf(false);
  };

  const handleBack = () => {
    if (phase === 'result') {
      setPhase('analysis');
      setShowTailored(false);
      setGeneratingPdf(false);
      return;
    }

    if (phase === 'analysis') {
      setPhase('input');
      dispatch({ type: 'SET_TAILOR_STATE', state: { loading: false, data: null, error: null } });
      setShowTailored(false);
      setGeneratingPdf(false);
    }
  };

  const handleNext = () => {
    if (phase === 'input') {
      void handleAnalyze();
      return;
    }

    if (phase === 'analysis') {
      void handleTailor();
      return;
    }

    handleDownload();
  };

  const displayText = state.selectedResumeContent || '';

  return (
    <>
      <SplitPanel
        left={
          <div className="p-3 flex flex-col gap-3 h-full overflow-auto">
            <StepWizard
              steps={STEPS}
              currentStep={currentStep}
              ariaLabel="Tailor progress"
              onBack={handleBack}
              onNext={handleNext}
              canGoBack={phase !== 'input'}
              canGoNext={phase === 'input' ? canAnalyze : phase === 'analysis' ? canTailor : !!analysis?.tailored_resume}
              backLabel={phase === 'result' ? 'Back to analysis' : 'Back'}
              nextLabel={phase === 'input' ? 'See How I Fit' : phase === 'analysis' ? 'Generate Tailored Resume' : 'Download PDF'}
            >
              <Card>
                <div className="flex items-center mb-3">
                  <span className="text-[11px] font-bold text-gold uppercase tracking-wide">
                    {phase === 'input' ? 'Job Details' : phase === 'analysis' ? 'Fit Analysis' : 'Tailored Result'}
                  </span>
                </div>

                <div className="flex flex-col gap-3">
                  {/* Resume Selector (input phase) */}
                  {phase === 'input' && (
                    <div className="field">
                      <label className="field-label">Select Resume *</label>
                      <ResumeSelect
                        resumes={state.resumes}
                        selectedFilename={state.selectedResume?.filename}
                        onSelect={selectResume}
                      />
                    </div>
                  )}

                  {/* Input Phase */}
                  {phase === 'input' && (
                    <div className="flex flex-col gap-3 animate-fade-in">
                      <Textarea
                        label="Job Description *"
                        placeholder="Paste the job description here..."
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value.slice(0, CHAR_LIMIT_JD))}
                        rows={6}
                      />
                      <Input
                        label="Job Position"
                        placeholder="e.g. Senior Frontend Engineer"
                        value={jobPosition}
                        onChange={(e) => setJobPosition(e.target.value)}
                      />
                      <Input
                        label="Company Name"
                        placeholder="e.g. Acme Corp"
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                      />
                      {jobDescription.length >= CHAR_LIMIT_JD && (
                        <p className="text-xs text-warning">
                          Character limit reached ({CHAR_LIMIT_JD.toLocaleString()})
                        </p>
                      )}
                      <div className="info-box" role="status">
                        <span className="text-sm" aria-hidden="true">ℹ</span>
                        <span>Fill in the job details and analyze to see your fit.</span>
                      </div>
                      <Button
                        variant="primary"
                        icon={<BarChart3 size={14} />}
                        full
                        onClick={handleAnalyze}
                        loading={state.tailor.loading && phase === 'input'}
                        disabled={!state.selectedResume || !jobDescription.trim() || !state.ollamaReady}
                      >
                        See How I Fit
                      </Button>
                    </div>
                  )}

                  {/* Analysis Phase */}
                  {phase === 'analysis' && analysis && (
                    <div className="flex flex-col gap-3 animate-fade-in">
                      <TailorAnalysis analysis={analysis} />

                      <div className="divider" />

                      <IntensitySelector
                        value={intensity}
                        onChange={setIntensity}
                        options={INTENSITY_OPTIONS}
                        label="Tailor Intensity"
                      />

                      <Button
                        variant="primary"
                        icon={<Edit size={14} />}
                        full
                        onClick={handleTailor}
                        loading={state.tailor.loading && phase === 'analysis'}
                        disabled={!state.ollamaReady}
                      >
                        Generate Tailored Resume
                      </Button>

                      <Button variant="ghost" icon={<RefreshCw size={14} />} full onClick={handleReset}>
                        Try Different Job
                      </Button>
                    </div>
                  )}

                  {/* Result Phase */}
                  {phase === 'result' && (
                    <div className="flex flex-col gap-3 animate-fade-in">
                      {analysis && <TailorAnalysis analysis={analysis} />}

                      <div className="divider" />

                      {analysis?.tailored_resume && (
                        <Button
                          variant="success"
                          icon={<Download size={14} />}
                          full
                          onClick={handleDownload}
                        >
                          Download Tailored Resume
                        </Button>
                      )}

                      <Button variant="ghost" icon={<RefreshCw size={14} />} full onClick={handleReset}>
                        Try Different Job
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            </StepWizard>
          </div>
        }

        right={
          <ResumePreview
            text={displayText}
            filename={isShowingTailored ? (tailoredPdfName || state.selectedResume?.filename) : state.selectedResume?.filename}
            pdfUrl={previewPdfUrl}
            title="Resume Preview"
            emptyTitle="No Resume Selected"
            emptyDescription="Select a resume and enter job details to begin"
            headerRight={
              phase === 'result' && analysis?.tailored_resume ? (
                <SegmentedControl
                  options={[
                    { label: 'Original', value: 'original' },
                    { label: 'Tailored', value: 'tailored' },
                  ]}
                  value={showTailored ? 'tailored' : 'original'}
                  onChange={(v) => setShowTailored(v === 'tailored')}
                  ariaLabel="View mode"
                />
              ) : null
            }
            onDownload={phase === 'result' && analysis?.tailored_resume ? handleDownload : undefined}
            loading={generatingPdf}
          />
        }
      />

      {notif && <NotificationToast {...notif} onClose={() => setNotif(null)} />}
      <Overlay
        visible={state.tailor.loading || generatingPdf}
        message={generatingPdf ? 'Generating PDF preview...' : phase === 'input' ? 'Analyzing fit...' : 'Tailoring resume...'}
      />
    </>
  );
}
