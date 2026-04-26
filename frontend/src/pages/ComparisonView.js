import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  ResponsiveContainer, Legend,
} from 'recharts';
import { api, groupColor, bandColor } from '../utils/api';

const BANDS = ['delta', 'theta', 'alpha', 'beta'];

export default function ComparisonView() {
  const [ids, setIds] = useState(['sub-001', 'sub-065']);
  const [inputVal, setInputVal] = useState('sub-001, sub-065');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = () => {
    const subjects = inputVal.split(',').map(s => {
      s = s.trim();
      return s.startsWith('sub-') ? s : `sub-${s.padStart(3, '0')}`;
    }).filter(Boolean);
    if (subjects.length < 2) { setError('Enter at least 2 subject IDs separated by commas'); return; }
    setError(null);
    setLoading(true);
    setResults(null);
    api.compare(subjects)
      .then(d => setResults(d.comparisons))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  // Build band power comparison chart data
  const bandChartData = BANDS.map(band => {
    const entry = { band: band.charAt(0).toUpperCase() + band.slice(1) };
    if (results) {
      results.forEach(r => {
        if (!r.error) {
          entry[r.subject_id] = +(r.band_powers[band] * 1e12).toFixed(4);
        }
      });
    }
    return entry;
  });

  // Score comparison table
  const SCORE_KEYS = ['theta_alpha_ratio','delta_alpha_ratio','brain_cognitive_score','alpha3_alpha2_ratio'];
  const SCORE_LABELS = {
    theta_alpha_ratio: 'θ/α',
    delta_alpha_ratio: 'δ/α',
    brain_cognitive_score: 'BCS',
    alpha3_alpha2_ratio: 'α3/α2',
  };
  const SCORE_THRESH = {
    theta_alpha_ratio: 1.5,
    delta_alpha_ratio: 2.0,
    brain_cognitive_score: 2.5,
    alpha3_alpha2_ratio: 1.35,
  };

  const COLORS = ['#00c8ff','#ff4c6a','#00e5a0','#ffb347','#b87fff','#ff9a00'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="card">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            className="input"
            value={inputVal}
            onChange={e => setInputVal(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && run()}
            placeholder="sub-001, sub-065, sub-037"
            style={{ flex: 1, minWidth: 260 }}
          />
          <button className="btn btn-primary" onClick={run} disabled={loading}>
            {loading ? 'Loading…' : 'Compare'}
          </button>
        </div>
        <div style={{ marginTop: 6, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Enter 2–6 subject IDs separated by commas. Tip: sub-001…036 = AD, sub-037…059 = FTD, sub-060…088 = CN
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}
      {loading && <div className="loading-wrap"><div className="spinner" /><div className="loading-text">Loading subjects…</div></div>}

      {results && (
        <>
          {/* Header cards */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {results.map((r, i) => (
              <div key={r.subject_id} className="card" style={{
                flex: '1 1 160px',
                borderColor: (r.error ? '#ff4c6a' : groupColor(r.group)) + '55',
              }}>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.95rem', color: COLORS[i], marginBottom: 4 }}>
                  {r.subject_id}
                </div>
                {r.error
                  ? <div style={{ color: 'var(--red)', fontSize: '0.8rem' }}>{r.error}</div>
                  : <>
                      <span className={`group-badge group-${r.group}`}>{r.group}</span>
                      <div style={{ marginTop: 8 }}>
                        <span className={`risk-badge risk-${r.risk_scores.risk_level}`}>{r.risk_scores.risk_level} risk</span>
                      </div>
                    </>
                }
              </div>
            ))}
          </div>

          {/* Band power chart */}
          <div className="card">
            <div className="section-header"><div className="section-title">Band Power Comparison (pW)</div></div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={bandChartData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis dataKey="band" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                  formatter={(v, n) => [v.toFixed(4) + ' pW', n]}
                />
                <Legend wrapperStyle={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }} />
                {results.filter(r => !r.error).map((r, i) => (
                  <Bar key={r.subject_id} dataKey={r.subject_id} fill={COLORS[i]} radius={[3,3,0,0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Score table */}
          <div className="card">
            <div className="section-header"><div className="section-title">Risk Score Comparison</div></div>
            <div style={{ overflowX: 'auto' }}>
              <table className="ch-table">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Group</th>
                    {SCORE_KEYS.map(k => <th key={k}>{SCORE_LABELS[k]}</th>)}
                    <th>Risk Level</th>
                  </tr>
                </thead>
                <tbody>
                  {results.filter(r => !r.error).map((r, i) => (
                    <tr key={r.subject_id}>
                      <td style={{ fontFamily: 'var(--font-display)', color: COLORS[i] }}>{r.subject_id}</td>
                      <td><span className={`group-badge group-${r.group}`}>{r.group}</span></td>
                      {SCORE_KEYS.map(k => {
                        const v = r.risk_scores[k];
                        const high = v > SCORE_THRESH[k];
                        return (
                          <td key={k} style={{ color: high ? 'var(--red)' : 'var(--green)', fontWeight: high ? 700 : 400 }}>
                            {v?.toFixed(4)}
                          </td>
                        );
                      })}
                      <td><span className={`risk-badge risk-${r.risk_scores.risk_level}`}>{r.risk_scores.risk_level}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
