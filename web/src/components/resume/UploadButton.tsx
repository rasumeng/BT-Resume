import { useRef } from 'react';
import { Plus } from 'lucide-react';
import Button from '../ui/Button';

interface UploadButtonProps {
  onUpload: (file: File) => Promise<void>;
  loading?: boolean;
  disabled?: boolean;
}

export default function UploadButton({ onUpload, loading, disabled }: UploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) return;
    await onUpload(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        disabled={disabled || loading}
        onChange={handleChange}
        aria-hidden="true"
      />
      <Button
        variant="primary"
        icon={<Plus size={14} />}
        full
        onClick={() => fileInputRef.current?.click()}
        loading={loading}
        disabled={disabled}
      >
        Add Resume
      </Button>
    </>
  );
}
