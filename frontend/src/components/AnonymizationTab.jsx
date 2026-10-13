import React, { useState } from 'react';
import { Database, Lock, Eye, EyeOff, CheckCircle2, AlertTriangle, Play } from 'lucide-react';
import { api } from '../services/api';

export default function AnonymizationTab({ datasets, selectedDataset, onRefreshBudget }) {
  const currentDataset = datasets.find(d => d.id === selectedDataset) || datasets[0];

  const [targetK, setTargetK] = useState(5);
  const [quasiIdentifiers, setQuasiIdentifiers] = useState(currentDataset.quasi_identifiers || ['age']);
  const [anonymizeResult, setAnonymizeResult] = useState(null);
  const [perturbResult, setPerturbResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleToggleQI = (col) => {
    if (quasiIdentifiers.includes(col)) {
      setQuasiIdentifiers(quasiIdentifiers.filter(c => c !== col));
    } else {
      setQuasiIdentifiers([...quasiIdentifiers, col]);
    }
  };

  const handleRunAnonymization = async () => {
    setLoading(true);
    try {
      const anonRes = await api.runAnonymization({
        dataset_id: selectedDataset,
        target_k: targetK,
        quasi_identifiers: quasiIdentifiers
      });
      setAnonymizeResult(anonRes);

      const pertRes = await api.perturbDataset({
        dataset_id: selectedDataset,
        epsilon: 1.0,
        mechanism: 'laplace'
      });
      setPerturbResult(pertRes);
      onRefreshBudget();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Configuration Header */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <span className="badge badge-cyan">DE-IDENTIFICATION ENGINE</span>
              <span className="badge badge-emerald">MONDRIAN PARTITIONING</span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.45rem', fontWeight: 800 }}>
              k-Anonymity, l-Diversity & Tabular Perturbation
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Generalize quasi-identifiers into indistinguishable equivalence classes of size &ge; k to prevent linkage attacks.
            </p>
          </div>

          <button
            className="btn-primary"
            onClick={handleRunAnonymization}
            disabled={loading || quasiIdentifiers.length === 0}
          >
            <Play size={16} /> {loading ? 'Processing Anonymization...' : 'Execute Anonymization & DP'}
          </button>
        </div>

        {/* Parameter Row */}
        <div style={{
          marginTop: '1.25rem',
          paddingTop: '1.25rem',
          borderTop: '1px solid var(--border-subtle)',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem'
        }}>
          {/* Target K Selector */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                Target Anonymity Parameter (k): <strong style={{ color: '#38bdf8' }}>k = {targetK}</strong>
              </label>
              <span className="badge badge-cyan">Min Class Size</span>
            </div>
            <input
              type="range"
              min="2"
              max="15"
              step="1"
              value={targetK}
              onChange={(e) => setTargetK(parseInt(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              <span>k = 2 (Weak)</span>
              <span>k = 5 (Standard HIPAA)</span>
              <span>k = 15 (High Privacy)</span>
            </div>
          </div>

          {/* Quasi-Identifier Checkboxes */}
          <div>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem', display: 'block' }}>
              Select Quasi-Identifiers (QI Attributes to Generalize):
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {currentDataset.columns.map((col) => {
                const isSelected = quasiIdentifiers.includes(col);
                const isTarget = col === currentDataset.target_column;
                return (
                  <button
                    key={col}
                    onClick={() => !isTarget && handleToggleQI(col)}
                    disabled={isTarget}
                    className="badge"
                    style={{
                      background: isSelected ? 'rgba(6, 182, 212, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                      color: isSelected ? '#38bdf8' : 'var(--text-muted)',
                      border: isSelected ? '1px solid #06b6d4' : '1px solid var(--border-subtle)',
                      cursor: isTarget ? 'not-allowed' : 'pointer',
                      padding: '0.4rem 0.75rem',
                      fontSize: '0.8rem'
                    }}
                  >
                    {isSelected ? <Lock size={12} /> : <Eye size={12} />} {col} {isTarget ? '(Target)' : ''}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Results Overview Metrics */}
      {anonymizeResult && (
        <div className="grid-cols-4">
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Before Anonymization</span>
            <div className="stat-number" style={{ color: '#fb7185' }}>
              k = {anonymizeResult.before_anonymization.current_k}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              {anonymizeResult.before_anonymization.violating_classes_count} vulnerable singleton classes
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Achieved Guarantee</span>
            <div className="stat-number gradient-text-emerald">
              k = {anonymizeResult.after_anonymization.target_k}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              All equivalence classes satisfy &ge; {anonymizeResult.after_anonymization.target_k} records
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>l-Diversity Protection</span>
            <div className="stat-number gradient-text-cyan">
              l = {anonymizeResult.l_diversity.distinct_l}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Entropy: {anonymizeResult.l_diversity.average_entropy} (Prevents homogeneity attack)
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Suppression Rate</span>
            <div className="stat-number" style={{ color: '#c084fc' }}>
              {anonymizeResult.after_anonymization.suppression_rate_pct}%
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              {anonymizeResult.after_anonymization.suppressed_records} outlier rows masked
            </p>
          </div>
        </div>
      )}

      {/* Side-by-side Table Preview */}
      {anonymizeResult && anonymizeResult.sample_preview && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700 }}>
                k-Anonymized & Generalization Sample Table
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Numerical attributes are binned into intervals; rare outliers are masked with &lsquo;*&rsquo; to prevent re-identification.
              </p>
            </div>
            <span className="badge badge-emerald">PROTECTED DATASET PREVIEW</span>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {Object.keys(anonymizeResult.sample_preview[0] || {}).map((col) => (
                    <th key={col}>
                      {col} {quasiIdentifiers.includes(col) ? '(QI)' : ''}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {anonymizeResult.sample_preview.map((row, idx) => (
                  <tr key={idx}>
                    {Object.entries(row).map(([col, val]) => {
                      const isMasked = String(val).includes('*');
                      const isInterval = String(val).includes('(') || String(val).includes('[');
                      return (
                        <td key={col} style={{
                          fontFamily: isInterval || isMasked ? 'var(--font-mono)' : 'inherit',
                          color: isMasked ? '#fb7185' : isInterval ? '#38bdf8' : 'inherit'
                        }}>
                          {String(val)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Differential Privacy Feature Perturbation Preview */}
      {perturbResult && perturbResult.preview_comparison && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700 }}>
                Differential Privacy Tabular Noise Injection Comparison
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Comparing original feature values vs differentially private perturbed values (&epsilon; = 1.0)
              </p>
            </div>
            <span className="badge badge-cyan">LAPLACE PERTURBATION</span>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Row Index</th>
                  <th>Original Values</th>
                  <th>DP Perturbed Values</th>
                  <th>Perturbation Effect</th>
                </tr>
              </thead>
              <tbody>
                {perturbResult.preview_comparison.map((item) => (
                  <tr key={item.index}>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>Row #{item.index + 1}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                      {JSON.stringify(item.original)}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                      {JSON.stringify(item.noisy)}
                    </td>
                    <td>
                      <span className="badge badge-emerald">CONFIDENTIALITY PRESERVED</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}
