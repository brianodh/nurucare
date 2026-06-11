import { useState, useCallback } from 'react';

const KEY = 'nurucare_progress';

export const loadProgress = () => {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
};

export const saveProgress = (data) => {
  try {
    const existing = loadProgress();
    localStorage.setItem(KEY, JSON.stringify({ ...existing, ...data, savedAt: Date.now() }));
  } catch {}
};

export const clearProgress = () => {
  try { localStorage.removeItem(KEY); } catch {}
};

// ── Convenience getters ──────────────────────────────────
export const getSavedProfileId = () => loadProgress().profileId || null;
export const getSavedResults   = () => loadProgress().results   || null;
export const isCompleted       = () => !!loadProgress().completed;

export function useProgress() {
  const [progress, setProgress] = useState(() => loadProgress());

  const update = useCallback((patch) => {
    setProgress((prev) => {
      const next = { ...prev, ...patch, savedAt: Date.now() };
      try { localStorage.setItem(KEY, JSON.stringify(next)); } catch {}
      return next;
    });
  }, []);

  const clear = useCallback(() => {
    clearProgress();
    setProgress({});
  }, []);

  // Call this after a successful intake submission
  const markCompleted = useCallback((profileId, results) => {
    setProgress((prev) => {
      const next = {
        ...prev,
        profileId,
        results,
        completed: true,
        completedAt: Date.now(),
        savedAt: Date.now(),
      };
      try { localStorage.setItem(KEY, JSON.stringify(next)); } catch {}
      return next;
    });
  }, []);

  return { progress, update, clear, markCompleted };
}
