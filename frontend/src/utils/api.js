const BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

async function get(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || res.statusText);
  }
  return res.json();
}

async function post(path, body) {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || res.statusText);
  }
  return res.json();
}

export const api = {
  health: () => get('/api/health'),
  subjects: () => get('/api/subjects'),
  analyze: (id, preprocessed = true) =>
    get(`/api/analyze/${id}?preprocessed=${preprocessed}`),
  compare: (subjects) => post('/api/compare', { subjects }),
  batch: (group, max = 10) => post('/api/batch', { group, max_subjects: max }),
  waveform: (id, channel = 'P3', start = 10, stop = 20) =>
    get(`/api/waveform/${id}?channel=${channel}&start=${start}&stop=${stop}`),
};

export function fmtPower(val) {
  if (val === undefined || val === null) return '—';
  return val.toExponential(3);
}

export function riskColor(level) {
  const map = { low: '#00e5a0', moderate: '#ffb347', elevated: '#ff9a00', high: '#ff4c6a' };
  return map[level] || '#6a8aaa';
}

export function groupColor(group) {
  const map = { AD: '#ff4c6a', FTD: '#b87fff', CN: '#00e5a0' };
  return map[group] || '#6a8aaa';
}

export function bandColor(band) {
  const map = {
    delta: '#b87fff',
    theta: '#00c8ff',
    alpha: '#00e5a0',
    beta:  '#ffb347',
  };
  return map[band] || '#6a8aaa';
}