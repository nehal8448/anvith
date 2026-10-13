import React, { useState, useEffect } from 'react';
import { Shield, Sliders, RefreshCw, AlertCircle, CheckCircle, HelpCircle } from 'lucide-react';
import { api } from '../services/api';

export default function DPSandboxTab({ budgetStatus, onRefreshBudget }) {
  const [epsilon, setEpsilon] = useState(1.0);
  const [delta, setDelta] = useState(0.00001);
  const [mechanism, setMechanism] = useState('laplace');
  const [sensitivity, setSensitivity] = useState(1.0);
  const [simData, setSimData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch simulation curve on parameter change
  useEffect(() => {
    async function fetchSim() {
      setLoading(true);
      try {
        const data = await api.simulateMechanism({
          mechanism,
          epsilon: parseFloat(epsilon),
          delta: parseFloat(delta),
          sensitivity: parseFloat(sensitivity),
        });
        setSimData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchSim();
  }, [epsilon, delta, mechanism, sensitivity]);

  const handleResetBudget = async () => {
    try {
      await api.resetBudget();
      onRefreshBudget();
    } catch (err) {
      console.error(err);
    }
  };

  // SVG Chart rendering for PDF curve
  const renderSvgPdf = () => {
    if (!simData || !simData.pdf_curve || simData.pdf_curve.length === 0) return null;

    const points = simData.pdf_curve;
    const width = 640;
    const height = 240;
    const padding = 35;

    const xVals = points.map(p => p.x);
    const yVals = points.map(p => p.density);

    const minX = Math.min(...xVals);
    const maxX = Math.max(...xVals);
    const maxY = Math.max(...yVals, 0.0001);

    const scaleX = (x) => padding + ((x - minX) / (maxX - minX)) * (width - 2 * padding);
    const scaleY = (y) => height - padding - (y / maxY) * (height - 2 * padding);

    const pathD = points.reduce((acc, p, i) => {
      const sx = scaleX(p.x);
      const sy = scaleY(p.density);
      return i === 0 ? `M ${sx} ${sy}` : `${acc} L ${sx} ${sy}`;
    }, '');

    // Area fill
    const areaD = `${pathD} L ${scaleX(maxX)} ${height - padding} L ${scaleX(minX)} ${height - padding} Z`;

    return (
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.02" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
        <line x1={scaleX(0)} y1={padding} x2={scaleX(0)} y2={height - padding} stroke="rgba(6,182,212,0.4)" strokeDasharray="4 4" strokeWidth="1.5" />

        {/* Shaded Area */}
        <path d={areaD} fill="url(#curveGradient)" />

        {/* Curve Line */}
        <path d={pathD} fill="none" stroke="#38bdf8" strokeWidth="2.5" />

        {/* Center label */}
        <text x={scaleX(0)} y={padding - 10} fill="#38bdf8" fontSize="11" textAnchor="middle" fontFamily="var(--font-mono)">
          Mean &mu; = 0
        </text>

        {/* Axis Labels */}
        <text x={scaleX(minX)} y={height - padding + 18} fill="var(--text-dim)" fontSize="11" textAnchor="start" fontFamily="var(--font-mono)">
          {minX.toFixed(1)}
        </text>
        <text x={scaleX(0)} y={height - padding + 18} fill="var(--text-muted)" fontSize="11" textAnchor="middle" fontFamily="var(--font-mono)">
          0.0 (Noisy Perturbation)
        </text>
        <text x={scaleX(maxX)} y={height - padding + 18} fill="var(--text-dim)" fontSize="11" textAnchor="end" fontFamily="var(--font-mono)">
          {maxX.toFixed(1)}
        </text>
      </svg>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Top Header */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <span className="badge badge-cyan">MATHEMATICAL PRIVACY</span>
              <span className="badge badge-emerald">PROVABLE GUARANTEE</span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.45rem', fontWeight: 800 }}>
              Differential Privacy (DP) Noise Simulator & Budget Ledger
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Tune privacy parameters (&epsilon;, &delta;) to inspect calibrated noise distributions and track cumulative privacy budget consumption.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn-secondary" onClick={handleResetBudget}>
              <RefreshCw size={14} /> Reset Budget Ledger
            </button>
          </div>
        </div>
      </div>

      {/* Main Controls & Simulation Row */}
      <div className="grid-cols-2">
        
        {/* Left: Interactive Controls */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sliders size={18} color="var(--cyan-primary)" /> Privacy Calibration Controls
          </h3>

          {/* Mechanism Selector */}
          <div>
            <label style={{ fontSize: '0.825rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
              Noise Perturbation Mechanism
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                className={`tab-pill ${mechanism === 'laplace' ? 'active' : ''}`}
                style={{ flex: 1, justifyContent: 'center' }}
                onClick={() => setMechanism('laplace')}
              >
                Laplace (&epsilon;-DP)
              </button>
              <button
                className={`tab-pill ${mechanism === 'gaussian' ? 'active' : ''}`}
                style={{ flex: 1, justifyContent: 'center' }}
                onClick={() => setMechanism('gaussian')}
              >
                Gaussian (&epsilon;, &delta;)-DP
              </button>
            </div>
          </div>

          {/* Epsilon Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                Privacy Budget (&epsilon;): <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{epsilon}</span>
              </label>
              <span className={`badge ${epsilon <= 0.5 ? 'badge-emerald' : epsilon <= 2.0 ? 'badge-cyan' : 'badge-amber'}`}>
                {epsilon <= 0.5 ? 'Strong Privacy' : epsilon <= 2.0 ? 'Balanced' : 'High Utility / Low Privacy'}
              </span>
            </div>
            <input
              type="range"
              min="0.1"
              max="5.0"
              step="0.1"
              value={epsilon}
              onChange={(e) => setEpsilon(parseFloat(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>
              <span>0.1 (High Noise)</span>
              <span>2.5 (Moderate)</span>
              <span>5.0 (Low Noise)</span>
            </div>
          </div>

          {/* Delta input (if Gaussian) */}
          {mechanism === 'gaussian' && (
            <div>
              <label style={{ fontSize: '0.825rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                Failure Probability Relaxation (&delta;):
              </label>
              <input
                type="number"
                step="0.000001"
                min="0.000001"
                max="0.01"
                className="form-input"
                value={delta}
                onChange={(e) => setDelta(parseFloat(e.target.value))}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.2rem', display: 'block' }}>
                Standard recommendation: &delta; &le; 1/N (e.g. 10&minus;5)
              </span>
            </div>
          )}

          {/* Sensitivity */}
          <div>
            <label style={{ fontSize: '0.825rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
              Query L1 Sensitivity (&Delta;f):
            </label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              max="10.0"
              className="form-input"
              value={sensitivity}
              onChange={(e) => setSensitivity(parseFloat(e.target.value))}
            />
          </div>

          {/* Mathematical Card */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '1rem',
            fontSize: '0.825rem'
          }}>
            <h4 style={{ color: 'var(--text-main)', marginBottom: '0.4rem', fontWeight: 600 }}>
              Mathematical Guarantee:
            </h4>
            {mechanism === 'laplace' ? (
              <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', lineHeight: 1.5 }}>
                P(M(D) &isin; S) &le; e<sup>&epsilon;</sup> &middot; P(M(D') &isin; S)<br />
                Scale b = &Delta;f / &epsilon; = {sensitivity} / {epsilon} = <strong style={{ color: '#38bdf8' }}>{simData?.scale_parameter}</strong>
              </p>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', lineHeight: 1.5 }}>
                P(M(D) &isin; S) &le; e<sup>&epsilon;</sup> &middot; P(M(D') &isin; S) + &delta;<br />
                StdDev &sigma; = &radic;(2 ln(1.25/&delta;)) &middot; (&Delta;f / &epsilon;) = <strong style={{ color: '#38bdf8' }}>{simData?.scale_parameter}</strong>
              </p>
            )}
          </div>

        </div>

        {/* Right: Real-time PDF Graph */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700 }}>
              Calibrated Noise Probability Density (PDF)
            </h3>
            <span className="badge badge-cyan">
              SCALE = {simData ? simData.scale_parameter : '...'}
            </span>
          </div>

          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            The probability distribution of noise added to query results. Tighter peaks around 0 mean less distortion (higher utility, lower privacy); broader curves mean stronger confidentiality protection.
          </p>

          {/* SVG Visualizer */}
          <div style={{
            background: 'rgba(9, 13, 22, 0.9)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '1rem',
            minHeight: '260px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {renderSvgPdf()}
          </div>

          {/* Quantile Breakdown */}
          {simData && simData.sample_quantiles && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(5, 1fr)',
              gap: '0.5rem',
              textAlign: 'center',
              fontSize: '0.75rem',
              padding: '0.75rem',
              background: 'rgba(15, 23, 42, 0.5)',
              borderRadius: '8px'
            }}>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block' }}>5th Pct</span>
                <strong style={{ fontFamily: 'var(--font-mono)', color: '#fb7185' }}>{simData.sample_quantiles.p5}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block' }}>25th Pct</span>
                <strong style={{ fontFamily: 'var(--font-mono)' }}>{simData.sample_quantiles.p25}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block' }}>Median</span>
                <strong style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>{simData.sample_quantiles.median}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block' }}>75th Pct</span>
                <strong style={{ fontFamily: 'var(--font-mono)' }}>{simData.sample_quantiles.p75}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block' }}>95th Pct</span>
                <strong style={{ fontFamily: 'var(--font-mono)', color: '#fb7185' }}>{simData.sample_quantiles.p95}</strong>
              </div>
            </div>
          )}

        </div>

      </div>

      {/* Cumulative Privacy Budget Tracker & Ledger */}
      {budgetStatus && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700 }}>
                Privacy Budget (&epsilon;, &delta;) Accounting Ledger
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Monitors composition across all analytical operations under sequential composition theorem
              </p>
            </div>
            <span className="badge badge-cyan">
              BASIC COMPOSITION ACTIVE
            </span>
          </div>

          {/* Progress Bar */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
              <span>Total Consumed Budget: <strong style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{budgetStatus.consumed_epsilon} &epsilon;</strong></span>
              <span>Available Remaining: <strong style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{budgetStatus.remaining_epsilon} &epsilon;</strong></span>
            </div>
            <div style={{ height: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '5px', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${budgetStatus.utilization_pct}%`,
                background: budgetStatus.utilization_pct > 80 ? 'linear-gradient(90deg, #f59e0b, #f43f5e)' : 'linear-gradient(90deg, #06b6d4, #10b981)',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>

          {/* Transaction Ledger Table */}
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Operation Tag</th>
                  <th>&epsilon; Spent</th>
                  <th>&delta; Spent</th>
                  <th>Cumulative &epsilon;</th>
                  <th>Remaining &epsilon;</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {budgetStatus.transactions && budgetStatus.transactions.length > 0 ? (
                  budgetStatus.transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>#{tx.id}</td>
                      <td>{tx.tag}</td>
                      <td style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>+{tx.epsilon_spent}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{tx.delta_spent}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{tx.cumulative_epsilon}</td>
                      <td style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{tx.remaining_epsilon}</td>
                      <td>
                        <span className="badge badge-emerald">ACCOUNTED</span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '1.5rem' }}>
                      No budget transactions logged yet. Run data perturbation or mining to record budget consumption.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

        </div>
      )}

    </div>
  );
}
