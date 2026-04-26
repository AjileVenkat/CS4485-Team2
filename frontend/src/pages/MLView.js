import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  ResponsiveContainer, Cell,
} from 'recharts';
import { api, groupColor } from '../utils/api';

const CLASS_ORDER = ['AD', 'CN', 'FTD'];
const COLORS = { AD: '#ff4c6a', CN: '#00e5a0', FTD: '#b87fff' };

export default function MLView() {
  const [results, setResults]   = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const train = () => {
    setLoading(true);
    setError(null);
    fetch('http://127.0.0.1:5000/api/ml/train', { method: 'POST' })
      .then(r => r.json())
      .then(d => { if (d.error) throw new Error(d.error); setResults(d); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  const cm      = results?.confusion_matrix;
  const classes = results?.classes || CLASS_ORDER;
  const report  = results?.classification_report;

  // Per-subject results grouped by correctness
  const correct   = results?.per_subject?.filter(s => s.correct)  || [];
  const incorrect = results?.per_subject?.filter(s => !s.correct) || [];

  // Feature importance chart data
  const featData = results?.feature_importances?.slice(0, 10).map(f => ({
    name: f.feature.replace(/_/g, ' '),
    value: +(f.importance * 100).toFixed(2),
  })) || [];

  // Per-class metrics
  const classMetrics = classes.map(cls => ({
    class: cls,
    precision: report?.[cls]?.precision ?? 0,
    recall:    report?.[cls]?.recall    ?? 0,
    f1:        report?.[cls]?.['f1-score'] ?? 0,
    support:   report?.[cls]?.support   ?? 0,
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="card card-glow">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', marginBottom: 6 }}>
              Random Forest Classifier
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: 560, lineHeight: 1.6 }}>
              Trained on 36 EEG spectral features per subject including band powers, 
              power ratios, and regional averages across frontal, temporal, central, 
              parietal and occipital regions. Evaluated with stratified 5-fold cross-validation.
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={train}
            disabled={loading}
            style={{ flexShrink: 0, padding: '10px 24px' }}
          >
            {loading ? 'Training…' : results ? 'Retrain Model' : 'Train Model'}
          </button>
        </div>

        {loading && (
          <div style={{ marginTop: '1.5rem' }}>
            <div style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', marginBottom: 8 }}>
              Loading all 88 subjects and training — this takes 1–3 minutes…
            </div>
            <div className="progress-wrap">
              <div className="progress-fill" style={{ width: '100%', background: 'var(--cyan)', animation: 'indeterminate 1.5s ease-in-out infinite' }} />
            </div>
            <style>{`@keyframes indeterminate { 0%{transform:translateX(-100%)} 100%{transform:translateX(100%)} }`}</style>
          </div>
        )}
      </div>

      {error && <div className="error-box">Error: {error}</div>}

      {results && (
        <>
          {/* Key metrics */}
          <div className="grid-4">
            <MetricTile label="Overall Accuracy" value={`${(results.accuracy * 100).toFixed(1)}%`} color="var(--cyan)" />
            <MetricTile label="Balanced Accuracy" value={`${(results.balanced_accuracy * 100).toFixed(1)}%`} color="var(--green)" />
            <MetricTile label="Subjects Trained" value={results.n_subjects} color="var(--text-primary)" />
            <MetricTile label="CV Method" value={results.cv_folds === 88 ? 'LOOCV' : `${results.cv_folds}-Fold`} sub={results.cv_folds === 88 ? 'Leave-One-Out' : 'Stratified K-Fold'} color="var(--text-primary)" />
          </div>

          {/* Correct / incorrect summary */}
          <div className="grid-2">
            <div className="stat-tile" style={{ borderColor: '#00e5a044' }}>
              <div className="stat-label">Correctly Classified</div>
              <div className="stat-value" style={{ color: 'var(--green)' }}>{correct.length}</div>
              <div className="stat-sub">out of {results.n_subjects} subjects</div>
            </div>
            <div className="stat-tile" style={{ borderColor: '#ff4c6a44' }}>
              <div className="stat-label">Misclassified</div>
              <div className="stat-value" style={{ color: 'var(--red)' }}>{incorrect.length}</div>
              <div className="stat-sub">
                {incorrect.map(s => `${s.subject_id} (${s.true}→${s.predicted})`).join(', ') || 'None'}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div>
            <div className="tabs">
              {['overview','confusion','features','subjects'].map(t => (
                <button key={t} className={`tab ${activeTab===t?'active':''}`} onClick={() => setActiveTab(t)}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>

            {activeTab === 'overview' && (
              <div className="grid-2">
                {/* Per-class metrics bar chart */}
                <div className="card">
                  <div className="section-header"><div className="section-title">Per-Class F1 Score</div></div>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={classMetrics} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
                      <CartesianGrid vertical={false} stroke="var(--border)" />
                      <XAxis dataKey="class" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0,1]} tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
                      <Tooltip
                        contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                        formatter={(v, n) => [`${(v*100).toFixed(1)}%`, n]}
                      />
                      <Bar dataKey="f1" name="F1 Score" radius={[4,4,0,0]}>
                        {classMetrics.map(d => <Cell key={d.class} fill={COLORS[d.class] || 'var(--cyan)'} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Per-class precision/recall table */}
                <div className="card">
                  <div className="section-header"><div className="section-title">Classification Report</div></div>
                  <table className="ch-table">
                    <thead>
                      <tr>
                        <th>Class</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1</th>
                        <th>Support</th>
                      </tr>
                    </thead>
                    <tbody>
                      {classMetrics.map(m => (
                        <tr key={m.class}>
                          <td><span className={`group-badge group-${m.class}`}>{m.class}</span></td>
                          <td style={{ color: m.precision > 0.8 ? 'var(--green)' : m.precision > 0.6 ? 'var(--amber)' : 'var(--red)' }}>
                            {(m.precision * 100).toFixed(1)}%
                          </td>
                          <td style={{ color: m.recall > 0.8 ? 'var(--green)' : m.recall > 0.6 ? 'var(--amber)' : 'var(--red)' }}>
                            {(m.recall * 100).toFixed(1)}%
                          </td>
                          <td style={{ color: m.f1 > 0.8 ? 'var(--green)' : m.f1 > 0.6 ? 'var(--amber)' : 'var(--red)', fontWeight: 700 }}>
                            {(m.f1 * 100).toFixed(1)}%
                          </td>
                          <td style={{ color: 'var(--text-secondary)' }}>{m.support}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'confusion' && cm && (
              <div className="card">
                <div className="section-header">
                  <div>
                    <div className="section-title">Confusion Matrix</div>
                    <div className="section-sub">Rows = True label · Columns = Predicted label</div>
                  </div>
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ borderCollapse: 'collapse', margin: '0 auto' }}>
                    <thead>
                      <tr>
                        <th style={{ padding: '8px 16px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>True \ Pred</th>
                        {classes.map(c => (
                          <th key={c} style={{ padding: '8px 16px', color: COLORS[c], fontFamily: 'var(--font-display)', fontSize: '0.85rem' }}>{c}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {cm.map((row, i) => {
                        const rowSum = row.reduce((a, b) => a + b, 0);
                        return (
                          <tr key={i}>
                            <td style={{ padding: '8px 16px', color: COLORS[classes[i]], fontFamily: 'var(--font-display)', fontSize: '0.85rem', fontWeight: 700 }}>
                              {classes[i]}
                            </td>
                            {row.map((val, j) => {
                              const isDiag = i === j;
                              const pct = rowSum > 0 ? val / rowSum : 0;
                              return (
                                <td key={j} style={{
                                  padding: '16px 24px',
                                  textAlign: 'center',
                                  background: isDiag
                                    ? `${COLORS[classes[i]]}${Math.round(pct * 180).toString(16).padStart(2,'0')}`
                                    : val > 0 ? '#ff4c6a22' : 'var(--bg-elevated)',
                                  borderRadius: 8,
                                  margin: 4,
                                  fontFamily: 'var(--font-display)',
                                  fontSize: '1.2rem',
                                  color: isDiag ? COLORS[classes[i]] : val > 0 ? 'var(--red)' : 'var(--text-muted)',
                                  fontWeight: isDiag ? 700 : 400,
                                  minWidth: 80,
                                }}>
                                  {val}
                                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 2 }}>
                                    {(pct * 100).toFixed(0)}%
                                  </div>
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <div style={{ marginTop: '1rem', fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                  Diagonal = correct predictions · Off-diagonal = misclassifications
                </div>
              </div>
            )}

            {activeTab === 'features' && (
              <div className="card">
                <div className="section-header">
                  <div>
                    <div className="section-title">Top 10 Feature Importances</div>
                    <div className="section-sub">Which EEG features the Random Forest relies on most</div>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart data={featData} layout="vertical" margin={{ top: 4, right: 20, bottom: 4, left: 160 }}>
                    <CartesianGrid horizontal={false} stroke="var(--border)" />
                    <XAxis type="number" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} />
                    <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} width={160} />
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
                      formatter={v => [`${v}%`, 'Importance']}
                    />
                    <Bar dataKey="value" radius={[0,4,4,0]}>
                      {featData.map((_, i) => (
                        <Cell key={i} fill={`hsl(${190 + i * 12}, 80%, ${60 - i * 2}%)`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {activeTab === 'subjects' && results?.per_subject && (
              <div className="card">
                <div className="section-header"><div className="section-title">Per-Subject Predictions</div></div>
                <div style={{ overflowX: 'auto', maxHeight: 420, overflowY: 'auto' }}>
                  <table className="ch-table">
                    <thead>
                      <tr>
                        <th>Subject</th>
                        <th>True Group</th>
                        <th>Predicted</th>
                        <th>Result</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.per_subject.map(s => (
                        <tr key={s.subject_id}>
                          <td style={{ fontFamily: 'var(--font-display)', fontSize: '0.82rem' }}>{s.subject_id}</td>
                          <td><span className={`group-badge group-${s.true}`}>{s.true}</span></td>
                          <td><span className={`group-badge group-${s.predicted}`}>{s.predicted}</span></td>
                          <td style={{ color: s.correct ? 'var(--green)' : 'var(--red)', fontWeight: 700, fontSize: '0.85rem' }}>
                            {s.correct ? '✓ Correct' : '✗ Wrong'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {!results && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🧠</div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', marginBottom: '0.5rem' }}>Ready to Train</div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', maxWidth: 400, margin: '0 auto' }}>
            Click "Train Model" to load all 88 subjects, extract EEG features, and train
            a Random Forest classifier with 5-fold cross-validation.
          </p>
        </div>
      )}
    </div>
  );
}

function MetricTile({ label, value, sub, color }) {
  return (
    <div className="stat-tile">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color: color || 'var(--cyan)', fontSize: value > 10 ? '1rem' : '1.5rem' }}>{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}