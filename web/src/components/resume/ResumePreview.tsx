import { FileText, Download, Loader2 } from 'lucide-react';
import type { ReactNode } from 'react';
import EmptyState from '../shared/EmptyState';

interface ResumePreviewProps {
  text: string;
  filename?: string;
  pdfUrl?: string;
  title?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  headerRight?: ReactNode;
  onDownload?: () => void;
  loading?: boolean;
}

export default function ResumePreview({
  text,
  filename,
  pdfUrl,
  title = 'Resume Preview',
  emptyTitle = 'No Resume Selected',
  emptyDescription = 'Select a resume from the list to preview',
  headerRight,
  onDownload,
  loading,
}: ResumePreviewProps) {
  const isPdf = Boolean(pdfUrl);

  if (loading) {
    return (
      <div className="p-4 flex-1 overflow-auto h-full">
        <div className="bg-surface border border-gold/10 rounded-xl animate-fade-in overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-surface-active">
            <div>
              <span className="text-xs font-bold text-gold uppercase tracking-wide">{title}</span>
            </div>
          </div>
          <div className="flex items-center justify-center min-h-[70vh]">
            <Loader2 size={32} className="animate-spin text-gold" />
          </div>
        </div>
      </div>
    );
  }

  if (!isPdf && !text) {
    return (
      <EmptyState
        icon={<FileText size={28} />}
        title={emptyTitle}
        description={emptyDescription}
      />
    );
  }

  const readTime = Math.ceil((text.length || 0) / 2000);

  return (
    <div className="p-4 flex-1 overflow-auto h-full">
      <div className="bg-surface border border-gold/10 rounded-xl animate-fade-in overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-surface-active">
          <div>
            <span className="text-xs font-bold text-gold uppercase tracking-wide">{title}</span>
            {filename && (
              <p className="text-xs text-text-secondary mt-0.5">{filename}</p>
            )}
          </div>
          <div className="flex items-center gap-3">
            {headerRight}
            {onDownload && (
              <button
                onClick={onDownload}
                className="text-text-secondary hover:text-gold transition-colors p-1 rounded"
                aria-label="Download resume"
                title="Download"
              >
                <Download size={14} />
              </button>
            )}
            <span className="text-[10px] font-semibold text-text-tertiary uppercase tracking-wider">
              {isPdf ? 'PDF preview' : `${readTime} min read`}
            </span>
          </div>
        </div>
        {isPdf ? (
          <div className="bg-black/20">
            <iframe
              title={filename ? `${filename} preview` : 'Resume PDF preview'}
              src={pdfUrl}
              className="w-full min-h-[70vh] border-0 bg-surface"
            />
          </div>
        ) : (
          <div
            className="p-4 font-mono text-xs md:text-sm leading-relaxed text-cream whitespace-pre-wrap max-w-[80ch]"
          >
            {text}
          </div>
        )}
      </div>
    </div>
  );
}
