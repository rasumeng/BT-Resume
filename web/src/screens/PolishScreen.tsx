import { useState, useCallback, useEffect, useRef } from 'react';
import { Sparkles, Download, RefreshCw, Check } from 'lucide-react';
import { useApp } from '../app/AppContext';
import * as resumeApi from '../services/resumeApi';
import * as aiApi from '../services/aiApi';
import { track } from '../services/tracking';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import SegmentedControl from '../components/ui/SegmentedControl';
import SplitPanel from '../components/layout/SplitPanel';
import StepWizard from '../components/ai/StepWizard';
import IntensitySelector from '../components/ai/IntensitySelector';
import ChangesList from '../components/ai/ChangesList';
import ResumeSelect from '../components/resume/ResumeSelect';
import ResumePreview from '../components/resume/ResumePreview';
import Overlay from '../components/shared/Overlay';
import NotificationToast from '../components/shared/NotificationToast';

const INTENSITY_OPTIONS = [
  { label: 'Light', value: 'light' },
  { label: 'Medium', value: 'medium' },
  { label: 'Aggressive', value: 'aggressive' },
];

const STEPS = [
  { label: 'Select', icon: <Sparkles size={14} /> },
  { label: 'Polish', icon: <Sparkles size={14} /> },
  { label: 'Review', icon: <Check size={14} /> },
  { label: 'Export', icon: <Download size={14} /> },
];

function getStep(hasResume: boolean, polished: boolean): number {
  if (polished) return 3;
  if (hasResume) return 2;
  return 1;
}

export default function PolishScreen() {
  const { state, selectResume, dispatch } = useApp();
  const [intensity, setIntensity] = useState('medium');
  const [showOriginal, setShowOriginal] = useState(true);
  const [notif, setNotif] = useState<{ type: 'success' | 'error'; title: string; message: string } | null>(null);
  const [generatingPdf, setGeneratingPdf] = useState(false);

  const prevResumeRef = useRef(state.selectedResume?.filename);

  useEffect(() => {
    const current = state.selectedResume?.filename;
    if (prevResumeRef.current && prevResumeRef.current !== current) {
      setShowOriginal(true);
      setGeneratingPdf(false);
    }
    prevResumeRef.current = current;
  }, [state.selectedResume?.filename]);

  const polishedText = state.polish.data?.polished_resume ?? null;
  const changes = state.polish.data?.changes ?? [];
  const polishedPdfName = state.polish.data?.polishedPdfName ?? null;
  const currentStep = getStep(!!state.selectedResume, !!polishedText);
  const canGenerate = !!state.selectedResume && !polishedText;
  const previewFilename = polishedPdfName
    ? polishedPdfName
    : (state.selectedResume?.filename?.toLowerCase().endsWith('.pdf')
        ? state.selectedResume.filename
        : null
      );
  const previewSource = polishedPdfName ? 'temp' : 'resumes';
  const previewPdfUrl = previewFilename
    ? `/api/get-resume-pdf?filename=${encodeURIComponent(previewFilename)}&source=${previewSource}`
    : undefined;

  const handlePolish = useCallback(async () => {
    const selected = state.selectedResume;
    if (!selected) return;

    dispatch({ type: 'SET_POLISH_STATE', state: { loading: true, data: null, error: null } });

    let resumeText = state.selectedResumeContent;
    if (!resumeText) {
      try {
        resumeText = await resumeApi.getResume(selected.filename);
      } catch {
        dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: null, error: 'Failed to load resume content.' } });
        setNotif({ type: 'error', title: 'Error', message: 'Failed to load resume content.' });
        return;
      }
    }

    track('polish', intensity);

    try {
      const result = await aiApi.polishResume(resumeText, intensity);
      if (result.polished_resume) {
        dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: result, error: null } });

        // Auto-generate PDF preview (like Flutter does) — keep overlay during generation
        setGeneratingPdf(true);
        try {
          const pdfResult = await resumeApi.saveTextPdf(selected.filename, result.polished_resume);
          dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: { ...result, polishedPdfName: pdfResult.filename }, error: null } });
          setShowOriginal(false);
        } catch {
          dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: { ...result, polishedPdfName: undefined }, error: null } });
          setNotif({ type: 'error', title: 'Preview Unavailable', message: 'Could not generate PDF preview. You can still download the text version.' });
        }
        setGeneratingPdf(false);

        setNotif({ type: 'success', title: 'Polish Complete', message: 'Your resume has been polished!' });
      } else {
        dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: null, error: 'Failed to polish resume.' } });
        setNotif({ type: 'error', title: 'Error', message: 'Failed to polish resume.' });
      }
    } catch {
      dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: null, error: 'An error occurred while polishing.' } });
      setNotif({ type: 'error', title: 'Error', message: 'An error occurred while polishing.' });
    }
  }, [dispatch, state.selectedResume, state.selectedResumeContent, intensity]);

  const handleDownload = useCallback(() => {
    const pdfName = polishedPdfName;
    if (!pdfName) return;
    track('polish_downloaded', pdfName);
    const a = document.createElement('a');
    a.href = `/api/get-resume-pdf?filename=${encodeURIComponent(pdfName)}&download=1&source=temp`;
    a.download = pdfName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [polishedPdfName]);

  const handleReset = () => {
    dispatch({ type: 'SET_POLISH_STATE', state: { loading: false, data: null, error: null } });
    setShowOriginal(true);
    setGeneratingPdf(false);
  };

  const handleBack = () => {
    if (polishedText) {
      handleReset();
      return;
    }

    if (state.selectedResume) {
      setNotif(null);
    }
  };

  const handleNext = () => {
    if (!polishedText) {
      void handlePolish();
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
              ariaLabel="Polish progress"
              onBack={handleBack}
              onNext={handleNext}
              canGoBack={true}
              canGoNext={canGenerate || !!polishedText}
              backLabel={polishedText ? 'Start over' : 'Back'}
              nextLabel={polishedText ? 'Download PDF' : 'Polish Resume'}
            >
              <Card>
                <div className="flex items-center mb-3">
                  <span className="text-[11px] font-bold text-gold uppercase tracking-wide">Polish Resume</span>
                  <p className="text-[11px] text-text-secondary ml-2">Improve clarity, impact, and ATS performance</p>
                </div>

                <div className="flex flex-col gap-3">
                  {/* Resume Selector */}
                  <div className="field">
                    <label className="field-label">Select Resume *</label>
                    <ResumeSelect
                      resumes={state.resumes}
                      selectedFilename={state.selectedResume?.filename}
                      onSelect={selectResume}
                    />
                  </div>

                  {/* Intensity */}
                  <IntensitySelector
                    value={intensity}
                    onChange={setIntensity}
                    options={INTENSITY_OPTIONS}
                    label="Polish Intensity"
                  />

                  {/* Info / Polish Button */}
                  {!polishedText && (
                    <>
                      <div className="info-box" role="status">
                        <Sparkles size={14} className="shrink-0 text-gold" />
                        <span>Select a resume, choose an intensity, then polish when ready.</span>
                      </div>
                      <Button
                        variant="primary"
                        icon={<Sparkles size={14} />}
                        full
                        onClick={handlePolish}
                        loading={state.polish.loading}
                        disabled={!state.selectedResume}
                      >
                        Polish Resume
                      </Button>
                    </>
                  )}

                  {/* Results */}
                  {polishedText && (
                    <div className="flex flex-col gap-3 animate-fade-in">
                      <ChangesList changes={changes} />

                      <div className="divider" />

                      <div className="flex gap-2">
                        <Button variant="secondary" icon={<RefreshCw size={14} />} onClick={handleReset} className="flex-1">
                          Start Over
                        </Button>
                        <Button variant="success" icon={<Download size={14} />} onClick={handleDownload} className="flex-1">
                          Download PDF
                        </Button>
                      </div>
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
            filename={polishedText && !showOriginal ? (polishedPdfName || state.selectedResume?.filename) : state.selectedResume?.filename}
            pdfUrl={previewPdfUrl}
            title="Resume Preview"
            emptyTitle="No Resume Selected"
            emptyDescription="Select a resume from the left panel to preview"
            headerRight={
              polishedText ? (
                <SegmentedControl
                  options={[
                    { label: 'Original', value: 'original' },
                    { label: 'Polished', value: 'polished' },
                  ]}
                  value={showOriginal ? 'original' : 'polished'}
                  onChange={(v) => setShowOriginal(v === 'original')}
                  ariaLabel="View mode"
                />
              ) : null
            }
            onDownload={polishedText ? handleDownload : undefined}
            loading={generatingPdf}
          />
        }
      />

      {notif && <NotificationToast {...notif} onClose={() => setNotif(null)} />}
      <Overlay visible={state.polish.loading || generatingPdf} message={generatingPdf ? 'Generating PDF preview...' : 'Polishing resume...'} />
    </>
  );
}
