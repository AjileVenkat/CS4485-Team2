import React, { useEffect, useState } from 'react';
import { api, groupColor } from '../utils/api';

const INFO_CARDS = [
  {
    title: 'AD Group',
    n: 36,
    mmse: '17.75 ± 4.5',
    age: '66.4 ± 7.9',
    color: '#ff4c6a',
    desc: 'Alzheimer\'s Disease patients. EEG shows elevated theta/delta, reduced alpha.',
  },
  {
    title: 'FTD Group',
    n: 23,
    mmse: '22.17 ± 8.22',
    age: '63.6 ± 8.2',
    color: '#b87fff',
    desc: 'Frontotemporal Dementia. Often shows frontal theta predominance.',
  },
  {
    title: 'CN Group',
    n: 29,
    mmse: '30.0',
    age: '67.9 ± 5.4',
    color: '#00e5a0',
    desc: 'Cognitively Normal controls. Strong posterior alpha rhythm.',
  },
];

const BIOMARKERS = [
  { label: 'Theta/Alpha Ratio', desc: 'Elevated in MCI and AD. >1.5 indicates risk.', threshold: '>1.5 = risk' },
  { label: 'Delta/Alpha Ratio', desc: 'High delta relative to alpha signals cortical slowing.', threshold: '>2.0 = high risk' },
  { label: 'Brain Cognitive Score', desc: '(δ+θ)/(α+β) — generalized slowing index.', threshold: 'Higher = worse' },
  { label: 'Alpha3/Alpha2 Ratio', desc: 'MCI-to-AD conversion biomarker (parietal channels).', threshold: '>1.35 = conversion' },
];

export default function Dashboard({ onNavigate }) {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(null);

  useEffect(() => {
    api.health()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
    api.subjects()
      .then(setSubjects)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const grouped = subjects.reduce((acc, s) => {
    acc[s.group] = (acc[s.group] || []).concat(s);
    return acc;
  }, {});

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero */}
      <div className="card card-glow" style={{ position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute', inset: 0, opacity: 0.04,
          background: 'repeating-linear-gradient(0deg, transparent, transparent 28px, #00c8ff 28px, #00c8ff 29px)',
          pointerEvents: 'none',
        }} />
        <div style={{ position: 'relative' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                EEG-Based Alzheimer's Detection
              </h1>
              <p style={{ color: 'var(--text-secondary)', maxWidth: 640, lineHeight: 1.6, fontSize: '0.95rem' }}>
                Resting-state EEG analysis of 88 subjects using spectral biomarkers — theta/alpha ratio,
                brain cognitive score, and alpha subband ratios — to stratify AD, FTD, and healthy controls.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                width: 8, height: 8, borderRadius: '50%',
                background: apiOnline === null ? '#6a8aaa' : apiOnline ? '#00e5a0' : '#ff4c6a',
                boxShadow: apiOnline ? '0 0 8px #00e5a0' : 'none',
                flexShrink: 0,
              }} />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                {apiOnline === null ? 'Checking API…' : apiOnline ? 'API Connected' : 'API Offline — start Flask backend'}
              </span>
            </div>
          </div>

          <div className="grid-4" style={{ marginTop: '1.5rem' }}>
            <Tile label="Total Subjects" value="88" sub="19-channel EEG" />
            <Tile label="AD Subjects" value="36" sub="Avg MMSE 17.75" color="#ff4c6a" />
            <Tile label="FTD Subjects" value="23" sub="Avg MMSE 22.17" color="#b87fff" />
            <Tile label="CN Subjects" value="29" sub="MMSE 30 (normal)" color="#00e5a0" />
          </div>
        </div>
      </div>

      {/* Subject Group Cards */}
      <div>
        <div className="section-header">
          <div>
            <div className="section-title">Dataset Overview</div>
            <div className="section-sub">Recording specs: 500 Hz, 10-20 system, eyes-closed resting state</div>
          </div>
        </div>
        <div className="grid-3">
          {INFO_CARDS.map(g => (
            <div key={g.title} className="card" style={{ borderColor: g.color + '44' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <span className="section-title" style={{ color: g.color }}>{g.title}</span>
                <span style={{
                  background: g.color + '22', color: g.color,
                  borderRadius: 999, padding: '3px 10px', fontSize: '0.75rem', fontWeight: 700,
                }}>n = {g.n}</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.55, marginBottom: '1rem' }}>
                {g.desc}
              </p>
              <div style={{ display: 'flex', gap: '1.5rem' }}>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>MMSE</div>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.95rem', color: 'var(--text-primary)' }}>{g.mmse}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Mean Age</div>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.95rem', color: 'var(--text-primary)' }}>{g.age}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Biomarkers */}
      <div>
        <div className="section-header">
          <div>
            <div className="section-title">EEG Biomarkers Used</div>
            <div className="section-sub">Spectral power band ratios for cognitive decline detection</div>
          </div>
        </div>
        <div className="grid-2">
          {BIOMARKERS.map(b => (
            <div key={b.label} className="card" style={{ display: 'flex', gap: '1rem' }}>
              <div style={{
                width: 3, borderRadius: 3, flexShrink: 0,
                background: 'linear-gradient(to bottom, var(--cyan), var(--purple))',
              }} />
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.9rem', marginBottom: '0.3rem' }}>{b.label}</div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>{b.desc}</div>
                <div style={{
                  marginTop: '0.5rem', fontSize: '0.72rem', fontFamily: 'var(--font-display)',
                  color: 'var(--cyan)', background: 'var(--cyan-dim)', display: 'inline-block',
                  padding: '2px 8px', borderRadius: 4,
                }}>{b.threshold}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick access subject list */}
      {subjects.length > 0 && (
        <div>
          <div className="section-header">
            <div>
              <div className="section-title">Quick Access</div>
              <div className="section-sub">Click a subject to analyze</div>
            </div>
          </div>
          <div className="card">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {subjects.filter(s => s.available).slice(0, 30).map(s => (
                <button
                  key={s.id}
                  onClick={() => onNavigate('analysis', s.id)}
                  style={{
                    background: 'var(--bg-elevated)',
                    border: `1px solid ${groupColor(s.group)}44`,
                    borderRadius: 6,
                    padding: '4px 10px',
                    cursor: 'pointer',
                    fontSize: '0.78rem',
                    fontFamily: 'var(--font-display)',
                    color: groupColor(s.group),
                    transition: 'var(--transition)',
                  }}
                  onMouseEnter={e => e.target.style.borderColor = groupColor(s.group)}
                  onMouseLeave={e => e.target.style.borderColor = groupColor(s.group) + '44'}
                >
                  {s.id.replace('sub-', '')}
                </button>
              ))}
            </div>
            <div style={{ marginTop: '1rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              <span style={{ color: '#ff4c6a' }}>■</span> AD &nbsp;
              <span style={{ color: '#b87fff' }}>■</span> FTD &nbsp;
              <span style={{ color: '#00e5a0' }}>■</span> CN
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          {apiOnline === false
            ? '⚠ Backend not reachable. Start Flask: python backend/app.py'
            : 'Loading subjects…'}
        </div>
      )}
    </div>
  );
}

function Tile({ label, value, sub, color = 'var(--cyan)' }) {
  return (
    <div className="stat-tile">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color }}>{value}</div>
      <div className="stat-sub">{sub}</div>
    </div>
  );
}
