import { Check, ChevronLeft, ChevronRight } from 'lucide-react';
import { useMemo, type ReactNode } from 'react';

interface Step {
  label: string;
  icon: ReactNode;
}

interface StepWizardProps {
  steps: Step[];
  currentStep: number;
  children: ReactNode;
  ariaLabel?: string;
  onBack?: () => void;
  onNext?: () => void;
  canGoBack?: boolean;
  canGoNext?: boolean;
  backLabel?: string;
  nextLabel?: string;
  footer?: ReactNode;
}

export default function StepWizard({
  steps,
  currentStep,
  children,
  ariaLabel,
  onBack,
  onNext,
  canGoBack = true,
  canGoNext = true,
  backLabel = 'Back',
  nextLabel = 'Next',
  footer,
}: StepWizardProps) {
  const activeStep = useMemo(() => Math.min(Math.max(currentStep, 1), steps.length), [currentStep, steps.length]);

  return (
    <section aria-label={ariaLabel} className="space-y-4">
      <ol className="flex items-start justify-center gap-0 py-2" aria-label={ariaLabel ? `${ariaLabel} steps` : 'Steps'}>
        {steps.map((step, idx) => {
          const stepNum = idx + 1;
          const isActive = stepNum === activeStep;
          const isCompleted = stepNum < activeStep;

          return (
            <li key={step.label} className="flex items-center">
              <div className="flex flex-col items-center gap-1">
                <button
                  type="button"
                  className={`step-dot ${
                    isActive
                      ? 'step-dot-active'
                      : isCompleted
                        ? 'step-dot-completed'
                        : 'step-dot-upcoming'
                  }`}
                  aria-current={isActive ? 'step' : undefined}
                  aria-label={`${step.label}${isCompleted ? ', completed' : isActive ? ', current step' : ''}`}
                  tabIndex={-1}
                >
                  {isCompleted ? <Check size={14} /> : step.icon}
                </button>
                <span
                  className={`step-label ${
                    isActive
                      ? 'step-label-active'
                      : isCompleted
                        ? 'step-label-completed'
                        : ''
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {idx < steps.length - 1 && (
                <div className={`step-line mx-1 ${isCompleted ? 'step-line-completed' : ''}`} />
              )}
            </li>
          );
        })}

      </ol>

      <div className="animate-fade-in">{children}</div>

      {(onBack || onNext || footer) && (
        <div className="flex flex-col gap-3 border-t border-surface-active pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex gap-2">
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                disabled={!canGoBack}
                className="btn btn-secondary"
              >
                <ChevronLeft size={14} />
                <span>{backLabel}</span>
              </button>
            )}
            {onNext && (
              <button
                type="button"
                onClick={onNext}
                disabled={!canGoNext}
                className="btn btn-primary"
              >
                <span>{nextLabel}</span>
                <ChevronRight size={14} />
              </button>
            )}
          </div>
          {footer ? <div className="flex items-center gap-2">{footer}</div> : null}
        </div>
      )}
    </section>
  );
}
