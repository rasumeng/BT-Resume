import { ArrowRight } from 'lucide-react';
import type { AnalysisData } from '../../types';
import CircularGauge from './CircularGauge';
import ProgressBar from './ProgressBar';

function getConfidenceLabel(score: number): string {
  if (score >= 85) return 'Excellent fit!';
  if (score >= 70) return 'Good match';
  if (score >= 60) return 'Fair match';
  return 'Needs work';
}

function getStatusBadgeClass(status: string): string {
  switch (status) {
    case 'matched': return 'badge-green';
    case 'partial': return 'badge-orange';
    default: return 'badge-red';
  }
}

interface TailorAnalysisProps {
  analysis: AnalysisData;
}

export default function TailorAnalysis({ analysis }: TailorAnalysisProps) {
  return (
    <div className="flex flex-col gap-3 animate-fade-in">
      {/* Confidence Gauge */}
      <div className="flex flex-col items-center gap-2">
        <CircularGauge
          score={analysis.overall_confidence}
          size={110}
          label={getConfidenceLabel(analysis.overall_confidence)}
        />
      </div>

      {/* Category Scores */}
      {analysis.category_scores.length > 0 && (
        <div className="flex flex-col gap-2">
          <span className="field-label">Match Breakdown</span>
          {analysis.category_scores.map((cat, idx) => (
            <div key={cat.name} className="flex flex-col gap-0.5 animate-fade-in" style={{ animationDelay: `${idx * 50}ms` }}>
              <div className="flex justify-between">
                <span className="text-xs text-text-secondary">{cat.icon} {cat.name}</span>
                <span className="text-xs font-semibold text-cream">{cat.score}/{cat.max_score}</span>
              </div>
              <ProgressBar value={cat.score} maxValue={cat.max_score} />
            </div>
          ))}
        </div>
      )}

      {/* Keyword Matches */}
      {analysis.matches.length > 0 && (
        <div>
          <span className="field-label mb-1.5 block">Top Matches</span>
          <div className="flex flex-wrap gap-1" role="list" aria-label="Keyword matches">
            {analysis.matches.slice(0, 10).map((m, i) => (
              <span
                key={i}
                role="listitem"
                className={`badge ${getStatusBadgeClass(m.status)}`}
              >
                {m.keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {analysis.gaps.missing_skills.length > 0 && (
        <div>
          <span className="field-label mb-1.5 block text-warning">Missing Skills</span>
          <div className="flex flex-wrap gap-1" role="list" aria-label="Missing skills">
            {analysis.gaps.missing_skills.slice(0, 8).map((s, i) => (
              <span key={i} role="listitem" className="badge badge-orange">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      {analysis.gaps.suggestions.length > 0 && (
        <div>
          <span className="field-label mb-1.5 block text-warning">Suggestions</span>
          {analysis.gaps.suggestions.slice(0, 4).map((s, i) => (
            <div key={i} className="flex items-start gap-1.5 mb-1">
              <ArrowRight size={10} className="text-warning shrink-0 mt-0.5" />
              <span className="text-xs text-cream">{s}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
