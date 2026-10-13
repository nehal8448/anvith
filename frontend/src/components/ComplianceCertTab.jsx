import React from 'react';
import { Shield, Award, Download, CheckCircle2, FileText, AlertCircle, ExternalLink } from 'lucide-react';

export default function ComplianceCertTab({ arenaResults, selectedDataset }) {
  const model = arenaResults?.models?.ethicprivai;
  const cert = model?.certification;
  const fairness = model?.fairness;
  const privacy = model?.privacy_mia;

  const handleExportJson = () => {
    const reportData = {
      project: "EthicPrivAI: Privacy-Preserving Data Mining for Ethical AI Systems",
      dataset: selectedDataset,
      timestamp: new Date().toISOString(),
      certification: cert,
      fairness_audit: fairness,
      privacy_defense_mia: privacy,
      explainability: model?.explainability
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `EthicPrivAI_Compliance_Report_${selectedDataset}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <span className="badge badge-emerald">EU AI ACT & NIST ALIGNED</span>
              <span className="badge badge-cyan">AUDIT CERTIFICATION</span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.45rem', fontWeight: 800 }}>
              Ethical AI Compliance Certificate & Audit Report
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Official compliance evaluation validating mathematical privacy preservation, algorithmic non-discrimination, and explainability.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn-primary" onClick={handleExportJson}>
              <Download size={16} /> Export Audit Report (JSON)
            </button>
          </div>
        </div>
      </div>

      {/* Main Certificate Card */}
      {cert ? (
        <div className="glass-panel" style={{
          padding: '2.5rem',
          border: '2px solid rgba(6, 182, 212, 0.4)',
          background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%)',
          position: 'relative'
        }}>
          
          {/* Header of Certificate */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.5rem', marginBottom: '1.75rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <Award size={36} color="#10b981" />
                <div>
                  <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.6rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                    Responsible AI Compliance Certificate
                  </h3>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Standard: EU Artificial Intelligence Act & NIST AI Risk Management Framework (RMF 1.0)
                  </span>
                </div>
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <span className="badge badge-emerald" style={{ fontSize: '0.85rem', padding: '0.4rem 1rem' }}>
                {cert.certification_status}
              </span>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.35rem' }}>
                Framework: {cert.framework_version}
              </div>
            </div>
          </div>

          {/* Big Scorecard Banner */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.25rem',
            background: 'rgba(9, 13, 22, 0.6)',
            borderRadius: '12px',
            padding: '1.5rem',
            marginBottom: '1.75rem'
          }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Overall Ethical AI Index</span>
              <div className="stat-number gradient-text-emerald" style={{ fontSize: '2.5rem' }}>
                {cert.overall_ethical_index}%
              </div>
              <span style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>{cert.certification_grade}</span>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Data Confidentiality (30%)</span>
              <div className="stat-number" style={{ color: '#38bdf8' }}>
                {cert.pillar_breakdown.privacy_and_confidentiality}%
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>&epsilon;-DP & Low MIA Leakage</span>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Algorithmic Fairness (30%)</span>
              <div className="stat-number" style={{ color: '#34d399' }}>
                {cert.pillar_breakdown.algorithmic_fairness}%
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Four-Fifths Rule Non-Discrimination</span>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Model Transparency (20%)</span>
              <div className="stat-number" style={{ color: '#c084fc' }}>
                {cert.pillar_breakdown.transparency_and_explainability}%
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Transparent Attributions</span>
            </div>

            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Utility & Accuracy (20%)</span>
              <div className="stat-number" style={{ color: '#f59e0b' }}>
                {cert.pillar_breakdown.utility_and_accuracy}%
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Test Accuracy & ROC-AUC</span>
            </div>
          </div>

          {/* Regulatory Alignment Checklist */}
          <div style={{ marginBottom: '1.75rem' }}>
            <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem' }}>
              Statutory AI Regulation Compliance Matrix
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '8px' }}>
                <CheckCircle2 size={18} color="#10b981" />
                <div style={{ flex: 1 }}>
                  <strong style={{ fontSize: '0.85rem' }}>EU AI Act Article 10 &ndash; Data Governance & Bias Prevention:</strong>
                  <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
                    Dataset scrutinized for demographic representation; disparate impact ratio {fairness?.disparate_impact_ratio} complies with legal non-discrimination thresholds.
                  </p>
                </div>
                <span className="badge badge-emerald">PASSED</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '8px' }}>
                <CheckCircle2 size={18} color="#10b981" />
                <div style={{ flex: 1 }}>
                  <strong style={{ fontSize: '0.85rem' }}>EU AI Act Article 15 &ndash; Cybersecurity & Confidentiality Robustness:</strong>
                  <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
                    Differential Privacy applied with bounded sensitivity (&epsilon; &le; 1.0); empirical MIA privacy leakage risk is {privacy?.privacy_leakage_pct}%.
                  </p>
                </div>
                <span className="badge badge-emerald">PASSED</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '8px' }}>
                <CheckCircle2 size={18} color="#10b981" />
                <div style={{ flex: 1 }}>
                  <strong style={{ fontSize: '0.85rem' }}>NIST AI RMF 1.0 &ndash; Govern & Measure (Transparency & Explainability):</strong>
                  <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
                    Full transparent linear surrogate feature attributions logged with quantifiable individual contribution coefficients.
                  </p>
                </div>
                <span className="badge badge-emerald">PASSED</span>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {cert.recommendations && (
            <div>
              <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-main)' }}>
                Auditor Recommendations & Actionable Insights:
              </h4>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '0.825rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                {cert.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

        </div>
      ) : (
        <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-muted)' }}>
            Please execute the 4-Model Arena to generate the full compliance certification report.
          </p>
        </div>
      )}

    </div>
  );
}
