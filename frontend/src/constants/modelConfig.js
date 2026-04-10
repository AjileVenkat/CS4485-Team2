export const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/predict'

export const ACCEPTED_EXTENSIONS = ['.set', '.edf', '.fif', '.csv', '.txt']

export const MODE_LABELS = {
  mock: 'Mock Demo',
  live: 'Live API',
  'mock-fallback': 'Mock Fallback',
}

export const MAX_HISTORY_ITEMS = 8
