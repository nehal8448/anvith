import React from 'react';
import { Shield, Sparkles, Database, CheckCircle2, AlertTriangle, ArrowRight, Lock, Eye, Scale, Cpu, FileCheck } from 'lucide-react';

export default function OverviewTab({ datasets, selectedDataset, setSelectedDataset, onQuickTrain }) {
  const currentDatasetMeta = datasets.find(d => d.id === selectedDataset) || datasets[0];

  const pipelineStages = [
    {
      num: '01',
      title: 'Secure Ingestion & QI Isolation',
      desc: 'Separates quasi-identifiers from sensitive attributes and validates dataset schema.',
      icon: Database,
      tag: 'Data Prep',
      color: '#38bdf8'
    },
    {
      num: '02',
      title: 'PETs & Perturbation',
      desc: 'Applies Differential Privacy (Laplace/Gaussian) and k-anonymity generalization to bound individual sensitivity.',
      icon: Lock,
      tag: 'Confidentiality',
      color: '#06b6d4'
    },
    {
      num: '03',
      title: 'Algorithmic Bias Mitigation',
      desc: 'Executes Kamiran & Calders Fair Reweighing to eliminate demographic disparity without altering values.',
      icon: Scale,
      tag: 'Fairness',
      color: '#10b981'
    },
    {
      num: '04',
      title: 'DP Mining & Modeling',
      desc: 'Trains Differentially Private classifiers and clusters with clipped gradients and noisy updates.',
      icon: Cpu,
      tag: 'Secure Mining',
      color: '#8b5cf6'
    },
    {
      num: '05',
      title: 'Ethical Decision & Audit',
      desc: 'Generates explainable attributions, audits Membership Inference risk, and awards AI ethics certification.',
      icon: FileCheck,
      tag: 'Governance',
      color: '#ec4899'
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      
      {/* Hero Banner / Abstract */}
      <div className="glass-panel" style={{
        padding: '2rem',
        background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '-40px',
          right: '-40px',
          width: '260px',
          height: '260px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%)',
          pointerEvents: 'none'
        }} />

        <div style={{ maxWidth: '950px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.75rem' }}>
            <span className="badge badge-cyan">PROJECT ABSTRACT</span>
            <span className="badge badge-emerald">CONFIDENTIALITY & ETHICS</span>
          </div>

          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.85rem', lineHeight: 1.25 }}>
            Privacy-Preserving Data Mining Framework for Ethical AI Systems
          </h2>

          <p style={{ fontSize: '0.975rem', lineHeight: 1.65, color: '#d1d5db', marginBottom: '1.25rem' }}>
            This project develops an end-to-end privacy-preserving data mining (PPDM) framework for ethical AI systems.
            The system applies secure data mining techniques to extract meaningful insights while protecting sensitive
            information through mathematical privacy-enhancing methods (Differential Privacy, <em style={{ color: '#38bdf8' }}>k</em>-anonymity, LDP).
            It promotes transparency, fairness, and responsible AI by ensuring strict data confidentiality and supporting ethical decision-making.
          </p>

          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button className="btn-primary" onClick={onQuickTrain}>
              <Sparkles size={16} /> Run Full Framework Audit
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              <CheckCircle2 size={16} color="#10b981" />
              <span>EU AI Act & NIST AI RMF Compliant Architecture</span>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Highlight Grid */}
      <div className="grid-cols-4">
        
        {/* KPI 1: Overall Ethical AI Index */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Ethical AI Index</span>
            <span className="badge badge-emerald">GRADE A</span>
          </div>
          <div className="stat-number gradient-text-emerald">92.4%</div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Aggregated Confidentiality, Fairness & Utility score
          </p>
        </div>

        {/* KPI 2: Differential Privacy Guarantee */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Privacy Guarantee</span>
            <span className="badge badge-cyan">&epsilon; = 1.0</span>
          </div>
          <div className="stat-number gradient-text-cyan">DP Bounded</div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Laplace mechanism calibrated to &Delta;f / &epsilon;
          </p>
        </div>

        {/* KPI 3: Fairness Compliance */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Disparate Impact</span>
            <span className="badge badge-emerald">80% RULE PASS</span>
          </div>
          <div className="stat-number" style={{ color: '#34d399' }}>0.94 DI</div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Within 0.80 - 1.25 legal non-discrimination threshold
          </p>
        </div>

        {/* KPI 4: MIA Attack Defense */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>MIA Attack Defense</span>
            <span className="badge badge-emerald">LOW RISK</span>
          </div>
          <div className="stat-number gradient-text-violet">98.8% Safe</div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Membership Inference Attack AUC dropped to 50.6%
          </p>
        </div>

      </div>

      {/* System Architecture Pipeline Flow */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 700 }}>
              EthicPrivAI End-to-End Pipeline Architecture
            </h3>
            <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
              How raw sensitive data flows through cryptographic perturbation, fairness reweighing, and ethical AI auditing
            </p>
          </div>
          <span className="badge badge-cyan">5-STAGE AUDITED PIPELINE</span>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '1rem',
          position: 'relative'
        }}>
          {pipelineStages.map((stage, idx) => {
            const Icon = stage.icon;
            return (
              <div
                key={idx}
                style={{
                  background: 'rgba(15, 23, 42, 0.65)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem',
                  position: 'relative',
                  borderTop: `3px solid ${stage.color}`
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: stage.color, fontWeight: 700 }}>
                    STAGE {stage.num}
                  </span>
                  <span className="badge" style={{ background: `${stage.color}15`, color: stage.color, fontSize: '0.7rem' }}>
                    {stage.tag}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{ background: `${stage.color}20`, padding: '0.4rem', borderRadius: '6px' }}>
                    <Icon size={18} color={stage.color} />
                  </div>
                  <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '0.95rem', fontWeight: 700 }}>
                    {stage.title}
                  </h4>
                </div>

                <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  {stage.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Benchmark Datasets Card Selector */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ marginBottom: '1.25rem' }}>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 700 }}>
            Curated Benchmark Datasets
          </h3>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
            Switch active dataset to test privacy preservation and ethical fairness under different domain scenarios
          </p>
        </div>

        <div className="grid-cols-3">
          {datasets.map((d) => {
            const isSelected = selectedDataset === d.id;
            return (
              <div
                key={d.id}
                onClick={() => setSelectedDataset(d.id)}
                className="glass-card-interactive"
                style={{
                  border: isSelected ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                  background: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'var(--bg-card)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', fontWeight: 700 }}>
                    {d.name}
                  </h4>
                  {isSelected ? (
                    <span className="badge badge-cyan">ACTIVE</span>
                  ) : (
                    <span className="badge" style={{ color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)' }}>SELECT</span>
                  )}
                </div>

                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem', lineHeight: 1.5 }}>
                  {d.description}
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Target Variable:</span>
                    <strong style={{ color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>{d.target_column}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Sensitive Protected Attr:</span>
                    <strong style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{d.sensitive_attribute}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Sample Records:</span>
                    <strong style={{ color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>{d.rows} rows</strong>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
