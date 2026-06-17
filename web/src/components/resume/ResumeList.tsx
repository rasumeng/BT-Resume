import { FileText, Trash2 } from 'lucide-react';
import type { ResumeFile } from '../../types';

interface ResumeListProps {
  resumes: ResumeFile[];
  selectedFilename?: string;
  onSelect: (resume: ResumeFile) => void;
  onDelete: (filename: string) => void;
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function displayName(filename: string): string {
  return filename.replace(/\.(pdf|txt)$/i, '');
}

export default function ResumeList({ resumes, selectedFilename, onSelect, onDelete }: ResumeListProps) {
  return (
    <div role="listbox" aria-label="Resume list" className="flex flex-col gap-1">
      {resumes.map((resume) => {
        const isSelected = resume.filename === selectedFilename;
        return (
          <div
            key={resume.filename}
            role="option"
            aria-selected={isSelected}
            className={`flex items-center gap-2 p-3 rounded-md cursor-pointer transition-all ${
              isSelected
                ? 'bg-surface-active border border-gold/40'
                : 'border border-transparent hover:bg-surface-hover'
            }`}
            onClick={() => onSelect(resume)}
          >
            <div
              className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
                isSelected ? 'bg-gold/15' : 'bg-surface-active'
              }`}
            >
              <FileText
                size={18}
                className={isSelected ? 'text-gold' : 'text-text-secondary'}
              />
            </div>

            <div className="flex-1 min-w-0">
              <p
                className={`text-sm font-semibold truncate transition-colors ${
                  isSelected ? 'text-gold' : 'text-cream'
                }`}
              >
                {displayName(resume.filename)}
              </p>
              <div className="flex gap-2 mt-0.5">
                <span className="text-xs text-text-secondary">{formatDate(resume.last_modified)}</span>
                <span className="text-xs text-text-secondary">{resume.file_size}</span>
              </div>
            </div>

            <button
              className="text-text-tertiary hover:text-error transition-colors p-1 rounded"
              onClick={(e) => { e.stopPropagation(); onDelete(resume.filename); }}
              aria-label={`Delete ${resume.filename}`}
            >
              <Trash2 size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
