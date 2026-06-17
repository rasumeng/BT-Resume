import { useState, useRef, useEffect } from 'react';
import { ChevronDown, FileText } from 'lucide-react';
import type { ResumeFile } from '../../types';

interface ResumeSelectProps {
  resumes: ResumeFile[];
  selectedFilename?: string;
  onSelect: (resume: ResumeFile) => void;
  placeholder?: string;
}

function displayName(filename: string): string {
  return filename.replace(/\.(pdf|txt)$/i, '');
}

export default function ResumeSelect({
  resumes,
  selectedFilename,
  onSelect,
  placeholder = 'Select a resume...',
}: ResumeSelectProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selected = resumes.find((r) => r.filename === selectedFilename);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        className={`dropdown-trigger w-full text-left ${open ? 'dropdown-trigger-open' : ''}`}
        onClick={() => setOpen(!open)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') setOpen(false);
        }}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <FileText size={16} className="shrink-0 text-text-tertiary" />
        <span className={selected ? 'text-cream flex-1 truncate' : 'text-text-tertiary flex-1 truncate'}>
          {selected ? displayName(selected.filename) : placeholder}
        </span>
        <ChevronDown
          size={14}
          className={`shrink-0 text-text-tertiary transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open && (
        <div className="dropdown-menu" role="listbox" aria-label="Resume list">
          {resumes.length === 0 ? (
            <div className="dropdown-item text-text-tertiary text-sm">No resumes found</div>
          ) : (
            resumes.map((resume) => {
              const isSelected = resume.filename === selectedFilename;
              return (
                <div
                  key={resume.filename}
                  role="option"
                  aria-selected={isSelected}
                  className={`dropdown-item ${isSelected ? 'bg-surface-active text-gold' : 'text-text-secondary'}`}
                  onClick={() => {
                    onSelect(resume);
                    setOpen(false);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelect(resume);
                      setOpen(false);
                    }
                  }}
                  tabIndex={0}
                >
                  <FileText
                    size={14}
                    className={`shrink-0 ${isSelected ? 'text-gold' : 'text-text-tertiary'}`}
                  />
                  <span className="flex-1 truncate">{displayName(resume.filename)}</span>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
