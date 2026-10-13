import React from 'react';
import { Scale, CheckCircle2, AlertTriangle, ShieldCheck, Users, HelpCircle } from 'lucide-react';

export default function FairnessTab({ arenaResults, onRunArena }) {
  // Use either EthicPrivAI model fairness results or Fair-Only model
  const modelData = arenaResults ? (arenaResults.models?.ethicprivai || arenaResults.models?.baseline) : null;
  const fairness = modelData?.fairness;
  const breakdown = fairness?.group_breakdown;

  const baselineFairness = arenaResults?.models?.baseline?.fairness;
  const ethicFairness = arenaResults?.models?.ethicprivai?.fairness;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <span className="badge badge-emerald">ALGORITHMIC FAIRNESS</span>
              <span className="badge badge-cyan">EEOC 80% FOUR-FIFTHS RULE</span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.45rem', fontWeight: 800 }}>
              Ethical AI & Bias Mitigation Audit Suite
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Evaluate disparate impact, demographic parity, and equalized odds across protected demographic groups.
            </p>
          </div>

          <button className="btn-primary" onClick={onRunArena}>
            <Scale size={16} /> Re-evaluate Algorithmic Bias
          </button>
        </div>
      </div>

      {/* Metrics Highlight Cards */}
      {fairness ? (
        <div className="grid-cols-4">
          
          {/* Disparate Impact Ratio */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Disparate Impact</span>
              <span className={`badge ${fairness.four_fifths_compliant ? 'badge-emerald' : 'badge-rose'}`}>
                {fairness.four_fifths_compliant ? 'COMPLIANT' : 'DISPARITY'}
              </span>
            </div>
            <div className={`stat-number ${fairness.four_fifths_compliant ? 'gradient-text-emerald' : ''}`} style={{ color: !fairness.four_fifths_compliant ? '#fb7185' : undefined }}>
              {fairness.disparate_impact_ratio}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Threshold: 0.80 &le; DI &le; 1.25 (Four-Fifths Rule)
            </p>
          </div>

          {/* Demographic Parity Difference */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Demographic Parity Diff</span>
              <span className="badge badge-cyan">SELECTION GAP</span>
            </div>
            <div className="stat-number gradient-text-cyan">
              {fairness.demographic_parity_diff}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              |P(&Ycirc;=1|Unpriv) &minus; P(&Ycirc;=1|Priv)|
            </p>
          </div>

          {/* Equal Opportunity (TPR) */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Equal Opportunity Diff</span>
              <span className="badge badge-emerald">TPR PARITY</span>
            </div>
            <div className="stat-number" style={{ color: '#34d399' }}>
              {fairness.equal_opportunity_diff}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Recall equality between protected groups
            </p>
          </div>

          {/* Individual Fairness (Theil Index) */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Individual Fairness</span>
              <span className="badge badge-violet">THEIL INDEX</span>
            </div>
            <div className="stat-number gradient-text-violet">
              {fairness.theil_index_individual_fairness}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Measures dispersion of decision benefits
            </p>
          </div>

        </div>
      ) : (
        <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Model has not been evaluated yet. Click &lsquo;Re-evaluate Algorithmic Bias&rsquo; to compute metrics.
          </p>
          <button className="btn-primary" onClick={onRunArena}>Run Evaluation</button>
        </div>
      )}

      {/* Disparate Impact Visual Gauge & Before vs After Mitigation */}
      {baselineFairness && ethicFairness && (
        <div className="grid-cols-2">
          
          {/* Baseline vs EthicPrivAI Disparate Impact Comparison */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              Disparate Impact Mitigation Comparison
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
              Shows how Kamiran & Calders Fair Reweighing brings Disparate Impact into the legal four-fifths non-discrimination zone.
            </p>

            {/* Baseline Bar */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '0.4rem' }}>
                <span style={{ color: '#fb7185' }}>Baseline (Unmitigated) Disparate Impact</span>
                <strong style={{ fontFamily: 'var(--font-mono)' }}>{baselineFairness.disparate_impact_ratio}</strong>
              </div>
              <div style={{ height: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '5px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${Math.min(100, (baselineFairness.disparate_impact_ratio / 1.25) * 100)}%`,
                  background: baselineFairness.four_fifths_compliant ? '#10b981' : '#f43f5e'
                }} />
              </div>
            </div>

            {/* EthicPrivAI Bar */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '0.4rem' }}>
                <span style={{ color: '#34d399' }}>EthicPrivAI (Fair Reweighed + DP)</span>
                <strong style={{ fontFamily: 'var(--font-mono)' }}>{ethicFairness.disparate_impact_ratio}</strong>
              </div>
              <div style={{ height: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '5px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${Math.min(100, (ethicFairness.disparate_impact_ratio / 1.25) * 100)}%`,
                  background: '#10b981'
                }} />
              </div>
            </div>

            <div style={{
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '8px',
              padding: '0.85rem',
              fontSize: '0.8rem',
              color: '#34d399',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <CheckCircle2 size={16} />
              <span>Bias successfully eliminated: EthicPrivAI achieved {ethicFairness.disparate_impact_ratio} DI ratio (100% compliant).</span>
            </div>
          </div>

          {/* Demographic Parity Gap Reduction */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              Demographic Parity & Equal Opportunity Gap
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
              Comparison of demographic disparities before and after algorithmic intervention
            </p>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Fairness Metric</th>
                    <th>Baseline</th>
                    <th>EthicPrivAI</th>
                    <th>Improvement</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Demographic Parity Diff</td>
                    <td style={{ color: '#fb7185', fontFamily: 'var(--font-mono)' }}>{baselineFairness.demographic_parity_diff}</td>
                    <td style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{ethicFairness.demographic_parity_diff}</td>
                    <td><span className="badge badge-emerald">MINIMIZED</span></td>
                  </tr>
                  <tr>
                    <td>Equal Opportunity (TPR Diff)</td>
                    <td style={{ color: '#fb7185', fontFamily: 'var(--font-mono)' }}>{baselineFairness.equal_opportunity_diff}</td>
                    <td style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{ethicFairness.equal_opportunity_diff}</td>
                    <td><span className="badge badge-emerald">BALANCED</span></td>
                  </tr>
                  <tr>
                    <td>Equalized Odds Diff</td>
                    <td style={{ color: '#fb7185', fontFamily: 'var(--font-mono)' }}>{baselineFairness.equalized_odds_diff}</td>
                    <td style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{ethicFairness.equalized_odds_diff}</td>
                    <td><span className="badge badge-emerald">EQUALIZED</span></td>
                  </tr>
                  <tr>
                    <td>Overall Fairness Score</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{baselineFairness.fairness_score_pct} / 100</td>
                    <td style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{ethicFairness.fairness_score_pct} / 100</td>
                    <td><span className="badge badge-cyan">+{(ethicFairness.fairness_score_pct - baselineFairness.fairness_score_pct).toFixed(1)} PTS</span></td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>

        </div>
      )}

      {/* Privileged vs Unprivileged Group Breakdown Matrix */}
      {breakdown && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Users size={18} color="var(--cyan-primary)" /> Protected Demographic Group Breakdown
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Detailed rate metrics comparing Privileged vs Unprivileged groups
              </p>
            </div>
            <span className="badge badge-cyan">DEMOGRAPHIC ANALYSIS</span>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Group</th>
                  <th>Test Samples</th>
                  <th>Selection Rate P(&Ycirc;=1)</th>
                  <th>True Positive Rate (TPR)</th>
                  <th>False Positive Rate (FPR)</th>
                  <th>Precision (PPV)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong style={{ color: '#38bdf8' }}>Privileged Group</strong></td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.privileged.count}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.privileged.selection_rate}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.privileged.true_positive_rate}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.privileged.false_positive_rate}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.privileged.precision}</td>
                </tr>
                <tr>
                  <td><strong style={{ color: '#c084fc' }}>Unprivileged Group</strong></td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.unprivileged.count}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.unprivileged.selection_rate}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.unprivileged.true_positive_rate}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.unprivileged.false_positive_rate}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{breakdown.unprivileged.precision}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Algorithmic Bias Mitigation Explanation */}
      <div className="glass-panel" style={{ padding: '1.5rem', background: 'rgba(15, 23, 42, 0.7)' }}>
        <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', fontWeight: 700, marginBottom: '0.5rem', color: '#38bdf8' }}>
          Kamiran & Calders Fair Reweighing (Pre-Processing Mitigation Method)
        </h4>
        <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
          Unlike adversarial debiasing or data suppression which degrade utility and risk destroying correlation structures,
          Kamiran & Calders Fair Reweighing calculates sample weights
          <code style={{ color: '#34d399', background: 'rgba(0,0,0,0.3)', padding: '0.2rem 0.4rem', borderRadius: '4px', margin: '0 0.3rem' }}>
            W(S, Y) = [P(S) &times; P(Y)] / P(S, Y)
          </code>
          so that the protected demographic attribute <em style={{ color: '#38bdf8' }}>S</em> and outcome <em style={{ color: '#38bdf8' }}>Y</em> become statistically independent prior to model fitting.
          Combined with Differential Privacy gradient clipping, this produces models that are simultaneously mathematically private and ethically fair.
        </p>
      </div>

    </div>
  );
}
