import { useEffect, useState } from 'react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';

interface DownloadDialogProps {
  open: boolean;
  originalFileName: string;
  onDownload: (fileName: string, replaceOriginal: boolean) => Promise<void> | void;
  onCancel: () => void;
}

function stripExtension(fileName: string): string {
  return fileName.replace(/\.(pdf|txt)$/i, '');
}

export default function DownloadDialog({
  open,
  originalFileName,
  onDownload,
  onCancel,
}: DownloadDialogProps) {
  const [fileName, setFileName] = useState(stripExtension(originalFileName));
  const [replaceOriginal, setReplaceOriginal] = useState(false);

  useEffect(() => {
    if (open) {
      setFileName(stripExtension(originalFileName));
      setReplaceOriginal(false);
    }
  }, [open, originalFileName]);

  const handleConfirm = async () => {
    const normalized = fileName.trim();
    if (!normalized && !replaceOriginal) return;
    await onDownload(normalized || stripExtension(originalFileName), replaceOriginal);
  };

  return (
    <Modal open={open} onClose={onCancel} title="Download Resume">
      <div className="flex flex-col gap-4">
        <div className="text-xs text-text-secondary">
          Default location: Documents {'>'} BT-Resume {'>'} resumes
        </div>

        <button
          type="button"
          onClick={() => setReplaceOriginal(false)}
          className={`text-left rounded-lg border p-3 transition-colors ${replaceOriginal ? 'border-surface-active bg-surface' : 'border-gold/40 bg-gold/5'}`}
        >
          <p className="text-sm font-semibold text-cream">Save with custom name</p>
          <p className="text-xs text-text-secondary">Choose a new filename</p>
        </button>

        {!replaceOriginal && (
          <div className="field">
            <label className="field-label">Filename</label>
            <div className="flex items-center gap-2">
              <input
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                placeholder="Enter filename"
                className="field-input flex-1"
              />
              <span className="text-xs text-text-secondary shrink-0">.pdf</span>
            </div>
          </div>
        )}

        <button
          type="button"
          onClick={() => setReplaceOriginal(true)}
          className={`text-left rounded-lg border p-3 transition-colors ${replaceOriginal ? 'border-gold/40 bg-gold/5' : 'border-surface-active bg-surface'}`}
        >
          <p className="text-sm font-semibold text-cream">Replace original file</p>
          <p className="text-xs text-text-secondary">Overwrite {originalFileName}</p>
        </button>

        <div className="flex gap-2 justify-end pt-2">
          <Button variant="ghost" onClick={onCancel}>Cancel</Button>
          <Button variant="primary" onClick={handleConfirm}>Download</Button>
        </div>
      </div>
    </Modal>
  );
}