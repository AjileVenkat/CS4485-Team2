import React, { useState, useEffect, useCallback } from 'react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid,
} from 'recharts';
import { api, fmtPower, riskColor, bandColor, groupColor } from '../utils/api';

const CHANNELS = ['Fp1','Fp2','F7','F3','Fz','F4','F8','T3','C3','Cz','C4','T4','T5','P3','Pz','P4','T6','O1','O2'];
const REGIONS = ['frontal','temporal','central','parietal','occipital'];

export default function SubjectAnalysis({ preselect }) {
  const [subjectId, setSubjectId] = useState(preselect || 'sub-001');
  const [inputVal, setInputVal] = useState(preselect || 'sub-001');
  const [data, setData] = useState(null);
  const [waveform, setWaveform] = useState(null);
  const [waveChannel, setWaveChannel] = useState('P3');
  const [loading, setLoading] = useState(false);
  const [waveLoading, setWaveLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [preprocessed, setPreprocessed] = useState(true);

  const load = useCallback((id) => {
    setLoading(true);
    setError(null);
    setData(null);
    api.analyze(id, preprocessed)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [preprocessed]);

  const loadWaveform = useCallback((id, ch) => {
    setWaveLoading(true);
    api.waveform(id, ch)
      .then(setWaveform)
      .catch(() => setWaveform(null))
      .finally(() => setWaveLoading(false));
  }, []);

  useEffect(() => {
    load(subjectId);
  }, [subjectId, load]);

  useEffect(() => {
    if (data) loadWaveform(subjectId, waveChannel);
  }, [subjectId, waveChannel, data, loadWaveform]);

  const submit = () => {
    const id = inputVal.trim().startsWith('sub-') ? inputVal.trim() : `sub-${inputVal.trim().padStart(3, '0')}`;
    setSubjectId(id);
  };

  const scores  = data?.risk_scores;
  const regions = data?.regional_powers;
  const avgPow  = data?.band_powers?.averages;
  const perCh   = data?.band_powers?.per_channel;

  // Prepare radar data
  const radarData = regions
    ? REGIONS.map(r => ({
        region: r.charAt(0).toUpperCase() + r.slice(1),
        theta: regions[r]?.theta * 1e12 || 0,
        alpha: regions[r]?.alpha * 1e12 || 0,
        delta: regions[r]?.delta * 1e12 || 0,
      }))
    : [];

  // Band power bar chart
  const bandData = avgPow
    ? ['delta','theta','alpha','beta'].map(b => ({
        band: b.charAt(0).toUpperCase() + b.slice(1),
        power: avgPow[b] * 1e12,
        fill: bandColor(b),
      }))
    : [];

  const waveData = waveform
    ? waveform.times.map((t, i) => ({ t: +t.toFixed(3), v: +waveform.amplitudes[i].toFixed(4) }))
    : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Subject selector */}
      <div className="card">
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            className="input"
            style={{ maxWidth: 200 }}
            value={inputVal}
            onChange={e => setInputVal(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && submit()}
            placeholder="sub-001"
          />
          <button className="btn btn-primary" onClick={submit} disabled={loading}>
            {loading ? 'Loading…' : 'Analyze'}
          </button>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={preprocessed}
              onChange={e => setPreprocessed(e.target.checked)}
              style={{ accentColor: 'var(--cyan)' }}
            />
            Use preprocessed data
          </label>
          {data && (
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginLeft: 'auto' }}>
              <span className={`group-badge group-${data.group}`}>{data.group}</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {data.n_channels}ch · {data.duration_seconds}s · {data.sampling_rate_hz}Hz
              </span>
            </div>
          )}
        </div>
      </div>

      {error && <div className="error-box">Error: {error}</div>}
      {loading && <div className="loading-wrap"><div className="spinner" /><div className="loading-text">Analyzing EEG signal…</div></div>}

      {data && (
        <>
          {/* Risk scores row */}
          <div className="grid-4">
            <ScoreCard label="Theta/Alpha Ratio" value={scores.theta_alpha_ratio} threshold={1.5} fmt="x" />
            <ScoreCard label="Delta/Alpha Ratio" value={scores.delta_alpha_ratio} threshold={2.0} fmt="x" />
            <ScoreCard label="Brain Cognitive Score" value={scores.brain_cognitive_score} threshold={2.5} fmt="" />
            <ScoreCard label="Alpha3/Alpha2 Ratio" value={scores.alpha3_alpha2_ratio} threshold={1.35} fmt="x" />
          </div>

          {/* Risk summary */}
          <div className="card" style={{ borderColor: riskColor(scores.risk_level) + '55', display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
            <RingGauge pct={scores.risk_percent} color={riskColor(scores.risk_level)} size={80} />
            <div>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 4 }}>
                AD Risk Assessment
              </div>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 6 }}>
                <span className={`risk-badge risk-${scores.risk_level}`}>{scores.risk_level} risk</span>
                <span className={`group-badge group-${data.group}`}>Actual: {data.group}</span>
              </div>
              <p style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', maxWidth: 520, lineHeight: 1.5 }}>
                {RISK_DESCRIPTIONS[scores.risk_level]}
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div>
            <div className="tabs">
              {['overview','waveform','channels','regions'].map(t => (
                <button key={t} className={`tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>

            {activeTab === 'overview' && (
              <div className="grid-2">
                <div className="card">
                  <div className="section-header"><div className="section-title">Band Power (avg, pW)</div></div>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={bandData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
                      <CartesianGrid vertical={false} stroke="var(--border)" />
                      <XAxis dataKey="band" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => v.toFixed(2)} />
                      <Tooltip
                        contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                        labelStyle={{ color: 'var(--text-primary)' }}
                        formatter={v => [v.toFixed(4) + ' pW', '']}
                      />
                      <Bar dataKey="power" radius={[4, 4, 0, 0]}>
                        {bandData.map((d, i) => (
                          <rect key={i} fill={d.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="card">
                  <div className="section-header"><div className="section-title">Regional Radar</div></div>
                  <ResponsiveContainer width="100%" height={220}>
                    <RadarChart data={radarData} outerRadius={80}>
                      <PolarGrid stroke="var(--border)" />
                      <PolarAngleAxis dataKey="region" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
                      <Radar name="Theta" dataKey="theta" stroke="var(--cyan)" fill="var(--cyan)" fillOpacity={0.15} />
                      <Radar name="Alpha" dataKey="alpha" stroke="#00e5a0" fill="#00e5a0" fillOpacity={0.15} />
                      <Tooltip
                        contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                        formatter={v => [v.toFixed(4) + ' pW', '']}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                  <div style={{ display: 'flex', gap: 12, justifyContent: 'center', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--cyan)' }}>● Theta</span>
                    <span style={{ color: '#00e5a0' }}>● Alpha</span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'waveform' && (
              <div className="card">
                <div className="section-header">
                  <div>
                    <div className="section-title">Raw EEG Waveform</div>
                    <div className="section-sub">10–20 second window · amplitude in µV</div>
                  </div>
                  <select className="select" style={{ width: 'auto' }} value={waveChannel} onChange={e => setWaveChannel(e.target.value)}>
                    {CHANNELS.map(c => <option key={c}>{c}</option>)}
                  </select>
                </div>
                {waveLoading && <div className="loading-wrap"><div className="spinner" /></div>}
                {!waveLoading && waveData.length > 0 && (
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={waveData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
                      <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                      <XAxis dataKey="t" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} label={{ value: 'Time (s)', position: 'insideBottom', fill: 'var(--text-muted)', offset: -2 }} />
                      <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
                      <Tooltip
                        contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                        formatter={v => [v.toFixed(3) + ' µV', waveChannel]}
                      />
                      <Line type="monotone" dataKey="v" stroke="var(--cyan)" dot={false} strokeWidth={1.2} />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            )}

            {activeTab === 'channels' && perCh && (
              <div className="card">
                <div className="section-header"><div className="section-title">Per-Channel Band Powers</div></div>
                <div style={{ overflowX: 'auto' }}>
                  <table className="ch-table">
                    <thead>
                      <tr>
                        <th>Channel</th>
                        <th>Delta (pW)</th>
                        <th>Theta (pW)</th>
                        <th>Alpha (pW)</th>
                        <th>Beta (pW)</th>
                        <th>θ/α</th>
                      </tr>
                    </thead>
                    <tbody>
                      {CHANNELS.filter(c => perCh[c]).map(ch => {
                        const p = perCh[ch];
                        const ratio = p.alpha > 0 ? p.theta / p.alpha : 0;
                        return (
                          <tr key={ch}>
                            <td style={{ fontFamily: 'var(--font-display)', color: 'var(--cyan)' }}>{ch}</td>
                            <td style={{ color: '#b87fff' }}>{(p.delta * 1e12).toFixed(3)}</td>
                            <td style={{ color: 'var(--cyan)' }}>{(p.theta * 1e12).toFixed(3)}</td>
                            <td style={{ color: '#00e5a0' }}>{(p.alpha * 1e12).toFixed(3)}</td>
                            <td style={{ color: 'var(--amber)' }}>{(p.beta * 1e12).toFixed(3)}</td>
                            <td style={{ color: ratio > 1.5 ? 'var(--red)' : 'var(--text-secondary)', fontWeight: ratio > 1.5 ? 700 : 400 }}>
                              {ratio.toFixed(3)}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'regions' && regions && (
              <div className="grid-3">
                {REGIONS.filter(r => regions[r]).map(r => (
                  <div key={r} className="card">
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.9rem', marginBottom: '1rem', textTransform: 'capitalize' }}>{r}</div>
                    {['delta','theta','alpha','beta'].map(b => (
                      <div key={b} style={{ marginBottom: '0.6rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 3 }}>
                          <span style={{ color: bandColor(b), textTransform: 'capitalize' }}>{b}</span>
                          <span style={{ color: 'var(--text-secondary)' }}>{(regions[r][b] * 1e12).toFixed(3)} pW</span>
                        </div>
                        <div className="progress-wrap">
                          <div className="progress-fill" style={{
                            width: `${Math.min(100, (regions[r][b] * 1e12) / 0.2 * 100)}%`,
                            background: bandColor(b),
                          }} />
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function ScoreCard({ label, value, threshold, fmt }) {
  const above = value > threshold;
  return (
    <div className="stat-tile" style={{ borderColor: above ? 'var(--red)44' : 'var(--border)' }}>
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color: above ? 'var(--red)' : 'var(--green)', fontSize: '1.4rem' }}>
        {value?.toFixed(4)}{fmt}
      </div>
      <div className="stat-sub" style={{ color: above ? 'var(--red)' : 'var(--text-secondary)' }}>
        {above ? `⚠ Above ${threshold}${fmt}` : `✓ Normal (<${threshold}${fmt})`}
      </div>
    </div>
  );
}

function RingGauge({ pct, color, size = 80 }) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <div className="score-ring-wrap">
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--bg-elevated)" strokeWidth={8} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={color} strokeWidth={8}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
      </svg>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.9rem', color, marginTop: -4 }}>{pct}%</div>
    </div>
  );
}

const RISK_DESCRIPTIONS = {
  low:      'EEG spectral biomarkers are within normal range. Theta/alpha ratio consistent with healthy cognitive function.',
  moderate: 'Some elevation in slow-wave activity. Theta/alpha ratio mildly elevated. Further monitoring recommended.',
  elevated: 'Significant theta dominance over alpha. Pattern consistent with mild cognitive impairment or early AD. Clinical evaluation advised.',
  high:     'Marked cortical slowing with strong theta/delta predominance. Biomarker profile highly consistent with moderate-to-severe AD.',
};
