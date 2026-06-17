import type { FeedbackData, FeedbackResponse } from '../types';

const BEYOND_THE_FRAME_API = 'https://beyondtheframe.vercel.app/api';

export async function submitFeedback(data: FeedbackData): Promise<void> {
  const submitName = data.isAnonymous
    ? 'Anonymous'
    : data.name?.trim() || 'Anonymous';

  const res = await fetch(`${BEYOND_THE_FRAME_API}/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: data.type,
      rating: data.rating,
      message: data.message,
      email: data.email || '',
      name: submitName,
    }),
  });

  const result: FeedbackResponse = await res.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to submit feedback');
  }
}
