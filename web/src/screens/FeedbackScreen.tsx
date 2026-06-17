import { useState } from 'react';
import { Lightbulb, Check } from 'lucide-react';
import { submitFeedback } from '../services/feedbackApi';
import { track } from '../services/tracking';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Textarea from '../components/ui/Textarea';
import SegmentedControl from '../components/ui/SegmentedControl';
import NotificationToast from '../components/shared/NotificationToast';
import StarRating from '../components/shared/StarRating';

const FEEDBACK_TYPES = [
  { label: 'General', value: 'general' },
  { label: 'Feature Request', value: 'feature_request' },
  { label: 'Bug Report', value: 'bug_report' },
];

export default function FeedbackScreen() {
  const [type, setType] = useState('general');
  const [rating, setRating] = useState(3);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [notif, setNotif] = useState<{ type: 'success' | 'error'; title: string; message: string } | null>(null);
  const [emailError, setEmailError] = useState('');

  const validateEmail = (value: string) => {
    if (!value) { setEmailError(''); return; }
    const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    setEmailError(isValid ? '' : 'Please enter a valid email address');
  };

  const handleSubmit = async () => {
    if (!message.trim()) {
      setNotif({ type: 'error', title: 'Error', message: 'Please enter a feedback message.' });
      return;
    }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setNotif({ type: 'error', title: 'Invalid Email', message: 'Please enter a valid email address or leave it blank.' });
      return;
    }
    try {
      setSubmitting(true);
      await submitFeedback({ type, rating, message, name, email, isAnonymous });
      track('feedback_submitted', type);
      setSubmitted(true);
      setNotif({ type: 'success', title: 'Thank You!', message: 'Your feedback helps us improve!' });
    } catch {
      setNotif({ type: 'error', title: 'Error', message: 'Failed to submit feedback.' });
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <Card className="text-center max-w-[420px] animate-scale-in">
          <div className="w-16 h-16 rounded-full bg-success/15 flex items-center justify-center mx-auto mb-4">
            <Check size={28} className="text-success" />
          </div>
          <h2 className="text-lg font-bold text-cream mb-2">Feedback Submitted!</h2>
          <p className="text-sm text-text-secondary mb-6">
            Thank you for your feedback! We'll use it to improve the app.
          </p>
          <Button
            variant="primary"
            onClick={() => { setSubmitted(false); setMessage(''); setRating(3); setName(''); setEmail(''); setIsAnonymous(false); }}
          >
            Send Another
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-6 flex justify-center">
      <div className="max-w-[620px] w-full">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-cream mb-1">App Feedback</h1>
          <p className="text-sm text-text-secondary">Help us improve Beyond The Resume with your feedback.</p>
        </div>

        <Card className="flex flex-col gap-4 animate-fade-in">
          {/* Feedback Type */}
          <div className="field">
            <label className="field-label" id="feedback-type-label">Feedback Type</label>
            <SegmentedControl
              options={FEEDBACK_TYPES}
              value={type}
              onChange={setType}
              ariaLabel="Feedback type"
            />
          </div>

          {/* Star Rating */}
          <div className="field">
            <label className="field-label">Rating</label>
            <StarRating value={rating} onChange={setRating} />
          </div>

          {/* Name */}
          {!isAnonymous && (
            <Input
              label="Your Name"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          )}

          {/* Anonymous Checkbox */}
          <div
            role="checkbox"
            aria-checked={isAnonymous}
            tabIndex={0}
            className="flex items-center gap-2.5 py-2 px-3 bg-surface-active rounded-md cursor-pointer select-none"
            onClick={() => setIsAnonymous(!isAnonymous)}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setIsAnonymous(!isAnonymous); } }}
          >
            <div
              className={`w-[18px] h-[18px] rounded border-2 flex items-center justify-center shrink-0 transition-all ${
                isAnonymous ? 'bg-gold border-gold' : 'border-text-tertiary'
              }`}
              aria-hidden="true"
            >
              {isAnonymous && <Check size={12} className="text-background" />}
            </div>
            <span className="text-xs text-cream">Submit Anonymously</span>
          </div>

          {/* Feedback Message */}
          <Textarea
            label="Your Feedback *"
            placeholder="Tell us what you think..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
          />

          {/* Email */}
          <Input
            label="Email (optional)"
            type="email"
            placeholder="For follow-up on your feedback"
            value={email}
            onChange={(e) => { setEmail(e.target.value); if (emailError) validateEmail(e.target.value); }}
            onBlur={() => validateEmail(email)}
            error={emailError}
          />

          {/* Info box */}
          <div className="info-box" role="status">
            <Lightbulb size={14} className="shrink-0 text-gold" />
            <span>Your feedback helps us improve! We read every submission.</span>
          </div>

          {/* Submit */}
          <Button variant="primary" full onClick={handleSubmit} loading={submitting} disabled={!message.trim()}>
            Submit Feedback
          </Button>
        </Card>
      </div>

      {notif && <NotificationToast {...notif} onClose={() => setNotif(null)} />}
    </div>
  );
}
