type TrackEvent =
  | 'resumes_added'
  | 'grade_resume'
  | 'polish'
  | 'fit_analysis'
  | 'tailor'
  | 'resume_uploaded'
  | 'feedback_submitted'
  | 'workspace_opened'
  | 'tab_changed'
  | 'resume_deleted'
  | 'polish_downloaded'
  | 'tailor_downloaded';

const TRACK_URL = 'https://beyondtheframe.vercel.app/api/track';

export function track(
  event: TrackEvent,
  label?: string,
  meta?: Record<string, unknown>,
): void {
  try {
    fetch(TRACK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event, label, meta }),
    }).catch(() => {});
  } catch {
    // silently fail — tracking should never disrupt the app
  }
}
