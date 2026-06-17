import { Star } from 'lucide-react';
import { useCallback } from 'react';

interface StarRatingProps {
  value: number;
  onChange: (value: number) => void;
}

export default function StarRating({ value, onChange }: StarRatingProps) {
  const handleKeyDown = useCallback((e: React.KeyboardEvent, star: number) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onChange(star);
      return;
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      onChange(Math.min(5, star + 1));
      return;
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      onChange(Math.max(1, star - 1));
    }
  }, [onChange]);

  return (
    <div
      className="flex gap-1"
      role="radiogroup"
      aria-label="Rating"
    >
      {[1, 2, 3, 4, 5].map((star) => {
        const isFilled = star <= value;
        return (
          <button
            key={star}
            role="radio"
            aria-checked={star === value}
            aria-label={`${star} out of 5 stars`}
            tabIndex={star === value ? 0 : -1}
            className="p-0.5 transition-transform hover:scale-110 focus-visible:outline-2 focus-visible:outline-gold"
            onClick={() => onChange(star)}
            onKeyDown={(e) => handleKeyDown(e, star)}
          >
            <Star
              size={20}
              className={isFilled ? 'fill-gold text-gold' : 'text-text-tertiary'}
            />
          </button>
        );
      })}
    </div>
  );
}
