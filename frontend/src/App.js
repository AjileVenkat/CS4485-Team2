import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import SubjectAnalysis from './pages/SubjectAnalysis';
import ComparisonView from './pages/ComparisonView';
import BatchView from './pages/BatchView';
import MLView from './pages/MLView';
import './App.css';

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [selectedSubject, setSelectedSubject] = useState(null);

  const navigate = (to, data = null) => {
    if (data) setSelectedSubject(data);
    setPage(to);
  };

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-brand">
          <span className="nav-pulse" />
          <span className="nav-title">EEG Biomarkers for <em>Alzheimer's</em></span>
        </div>
        <div className="nav-links">
          {[
            { id: 'dashboard',  label: 'Dashboard' },
            { id: 'analysis',   label: 'Subject Analysis' },
            { id: 'comparison', label: 'Comparison' },
            { id: 'batch',      label: 'Batch Stats' },
            { id: 'ml',         label: '🧠 ML Classifier' },
          ].map(({ id, label }) => (
            <button
              key={id}
              className={`nav-link ${page === id ? 'active' : ''}`}
              onClick={() => navigate(id)}
            >
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main className="main">
        {page === 'dashboard'  && <Dashboard onNavigate={navigate} />}
        {page === 'analysis'   && <SubjectAnalysis preselect={selectedSubject} />}
        {page === 'comparison' && <ComparisonView />}
        {page === 'batch'      && <BatchView />}
        {page === 'ml'         && <MLView />}
      </main>
    </div>
  );
}