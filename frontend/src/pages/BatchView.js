import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  ResponsiveContainer, ErrorBar,
} from 'recharts';
import { api, groupColor, bandColor } from '../utils/api';

const GROUPS = ['AD', 'FTD', 'CN', 'ALL'];
const BANDS  = ['delta', 'theta', 'alpha', 'beta'];
const SCORE_KEYS = ['theta_alpha_ratio', 'delta_alpha_ratio', 'brain_cognitive_score', 'alpha3_alpha2_ratio'];
const SCORE_LABELS = {
  theta_alpha_ratio:     'θ/α Ratio',
  delta_alpha_ratio:     'δ/α Ratio',
  brain_cognitive_score: 'Brain Cognitive Score',
  alpha3_alpha2_ratio:   'α3/α2 Ratio',
};
const SCORE_THRESH = {
  theta_alpha_ratio:     1.5,
  delta_alpha_ratio:     2.0,
  brain_cognitive_score: 2.5,
  alpha3_alpha2_ratio:   1.35,
};

export default function BatchView() {
  const [group, setGroup] = useState('AD');
  const [maxSubj, setMaxSubj] = useState(10);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = () => {
    setLoading(true); setError(null); setData(null);
    api.batch(group, maxSubj)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  const agg = data?.aggregates;

  // Build band power chart
  const bandChartData = agg
    ? BANDS.map(b => {
        const row = { band: b.charAt(0).toUpperCase() + b.slice(1) };
        Object.entries(agg).forEach(([grp, vals]) => {
          if (vals[`${b}_mean`] !== undefined) {
            row[grp] = +(vals[`${b}_mean`] * 1e12).toFixed(4);
            row[`${grp}_err`] = +(vals[`${b}_std`] * 1e12).toFixed(4);
          }
        });
        return row;
      })
    : [];

  const scoreChartData = SCORE_KEYS.map(k => {
    const row = { metric: SCORE_LABELS[k] };
    if (agg) {
      Object.entries(agg).forEach(([grp, vals]) => {
        if (vals[`${k}_mean`] !== undefined) {
          row[grp] = +vals[`${k}_mean`].toFixed(4);
        }
      });
    }
    return row;
  });

  const grpColors = { AD: '#ff4c6a', FTD: '#b87fff', CN: '#00e5a0', ALL: '#00c8ff' };
  const presentGroups = agg ? Object.keys(agg) : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="card">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <select className="select" style={{ width: 'auto' }} value={group} onChange={e => setGroup(e.target.value)}>
            {GROUPS.map(g => <option key={g}>{g}</option>)}
          </select>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>Max subjects:</label>
            <input
              type="number" min={1} max={36} className="input" style={{ width: 70 }}
              value={maxSubj} onChange={e => setMaxSubj(+e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={run} disabled={loading}>
            {loading ? 'Processing…' : 'Run Batch Analysis'}
          </button>
        </div>
        <div style={{ marginTop: 6, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Aggregate statistics across all subjects in the selected group. "ALL" includes AD, FTD, and CN.
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}
      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <div className="loading-text">Processing {maxSubj} subjects — this may take a moment…</div>
        </div>
      )}

      {data && (
        <>
          <div className="grid-3">
            <div className="stat-tile">
              <div className="stat-label">Group</div>
              <div className="stat-value" style={{ color: grpColors[group] || 'var(--cyan)', fontSize: '1.3rem' }}>{group}</div>
              <div className="stat-sub">{data.n_subjects} subjects analyzed</div>
            </div>
            {agg && presentGroups.slice(0, 2).map(grp => (
              <div key={grp} className="stat-tile" style={{ borderColor: grpColors[grp] + '55' }}>
                <div className="stat-label">Avg θ/α · {grp}</div>
                <div className="stat-value" style={{ color: grpColors[grp], fontSize: '1.3rem' }}>
                  {agg[grp]?.theta_alpha_ratio_mean?.toFixed(3) ?? '—'}
                </div>
                <div className="stat-sub">± {agg[grp]?.theta_alpha_ratio_std?.toFixed(3) ?? '—'}</div>
              </div>
            ))}
          </div>

          {/* Band power chart */}
          <div className="card">
            <div className="section-header"><div className="section-title">Mean Band Power by Group (pW)</div></div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={bandChartData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis dataKey="band" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                  formatter={(v, n) => [v.toFixed(4) + ' pW', n]}
                />
                {presentGroups.map(grp => (
                  <Bar key={grp} dataKey={grp} fill={grpColors[grp]} radius={[3,3,0,0]}>
                    <ErrorBar dataKey={`${grp}_err`} width={4} strokeWidth={2} stroke={grpColors[grp]} opacity={0.6} />
                  </Bar>
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Risk score chart */}
          <div className="card">
            <div className="section-header"><div className="section-title">Mean Risk Score Comparison</div></div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={scoreChartData} layout="vertical" margin={{ top: 4, right: 20, bottom: 4, left: 140 }}>
                <CartesianGrid horizontal={false} stroke="var(--border)" />
                <XAxis type="number" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="metric" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} width={140} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                  formatter={(v, n) => [v.toFixed(4), n]}
                />
                {presentGroups.map(grp => (
                  <Bar key={grp} dataKey={grp} fill={grpColors[grp]} radius={[0,3,3,0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Subject-level table */}
          <div className="card">
            <div className="section-header"><div className="section-title">Subject-Level Results</div></div>
            <div style={{ overflowX: 'auto', maxHeight: 380, overflowY: 'auto' }}>
              <table className="ch-table">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Group</th>
                    <th>θ/α</th>
                    <th>δ/α</th>
                    <th>BCS</th>
                    <th>α3/α2</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {data.subjects.map(s => (
                    <tr key={s.subject_id}>
                      <td style={{ fontFamily: 'var(--font-display)', fontSize: '0.82rem' }}>{s.subject_id}</td>
                      <td><span className={`group-badge group-${s.group}`}>{s.group}</span></td>
                      <td style={{ color: s.theta_alpha_ratio > 1.5 ? 'var(--red)' : 'var(--green)' }}>
                        {s.theta_alpha_ratio?.toFixed(3) ?? '—'}
                      </td>
                      <td style={{ color: s.delta_alpha_ratio > 2.0 ? 'var(--red)' : 'var(--green)' }}>
                        {s.delta_alpha_ratio?.toFixed(3) ?? '—'}
                      </td>
                      <td>{s.brain_cognitive_score?.toFixed(3) ?? '—'}</td>
                      <td>{s.alpha3_alpha2_ratio?.toFixed(3) ?? '—'}</td>
                      <td><span className={`risk-badge risk-${s.risk_level}`}>{s.risk_level}</span></td>
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
