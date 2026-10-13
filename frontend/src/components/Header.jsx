import React from 'react';
import { Shield, Sparkles, Database, Activity, RefreshCw } from 'lucide-react';

export default function Header({ 
  activeTab, 
  setActiveTab, 
  datasets, 
  selectedDataset, 
  setSelectedDataset,
  budgetStatus,
  apiConnected
}) {
  return (
    <header className="glass-panel" style={{ padding: '1rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%)',
            padding: '0.65rem',
            borderRadius: '12px',
            boxShadow: '0 0 16px rgba(6, 182, 212, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Shield size={26} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.45rem', fontWeight: 800, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              EthicPrivAI <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>v1.0 FRAMEWORK</span>
            </h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Privacy-Preserving Data Mining for Ethical AI Systems
            </p>
          </div>
        </div>

        {/* Dataset Selector & Budget Widget */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          
          {/* Active Dataset Picker */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={16} color="var(--cyan-primary)" />
            <select
              className="form-select"
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              style={{ width: 'auto', minWidth: '170px', padding: '0.45rem 0.75rem', fontSize: '0.85rem' }}
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name.split(' ')[0]} ({d.rows} rows)
                </option>
              ))}
            </select>
          </div>

          {/* Privacy Budget Pill */}
          {budgetStatus && (
            <div style={{
              background: 'rgba(15, 23, 42, 0.75)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '0.4rem 0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              fontSize: '0.8rem'
            }}>
              <span style={{ color: 'var(--text-muted)' }}>Budget (&epsilon;):</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#38bdf8' }}>
                {budgetStatus.remaining_epsilon} / {budgetStatus.total_epsilon}
              </span>
              <span className={`badge ${budgetStatus.utilization_pct > 80 ? 'badge-rose' : 'badge-emerald'}`}>
                {budgetStatus.utilization_pct}% Used
              </span>
            </div>
          )}

          {/* API Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem' }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: apiConnected ? '#10b981' : '#f43f5e',
              boxShadow: apiConnected ? '0 0 8px #10b981' : '0 0 8px #f43f5e'
            }} />
            <span style={{ color: 'var(--text-muted)' }}>{apiConnected ? 'Core Engine Online' : 'Engine Offline'}</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.4rem',
        overflowX: 'auto',
        borderTop: '1px solid var(--border-subtle)',
        paddingTop: '0.75rem'
      }}>
        <button
          className={`tab-pill ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Sparkles size={16} /> Architecture & Overview
        </button>
        <button
          className={`tab-pill ${activeTab === 'dp-sandbox' ? 'active' : ''}`}
          onClick={() => setActiveTab('dp-sandbox')}
        >
          <Shield size={16} /> Differential Privacy Sandbox
        </button>
        <button
          className={`tab-pill ${activeTab === 'anonymization' ? 'active' : ''}`}
          onClick={() => setActiveTab('anonymization')}
        >
          <Database size={16} /> k-Anonymity & Data Perturbation
        </button>
        <button
          className={`tab-pill ${activeTab === 'fairness' ? 'active' : ''}`}
          onClick={() => setActiveTab('fairness')}
        >
          <Activity size={16} /> Ethical AI & Fairness Audit
        </button>
        <button
          className={`tab-pill ${activeTab === 'arena' ? 'active' : ''}`}
          onClick={() => setActiveTab('arena')}
        >
          <RefreshCw size={16} /> Secure Mining & Model Arena
        </button>
        <button
          className={`tab-pill ${activeTab === 'cert' ? 'active' : ''}`}
          onClick={() => setActiveTab('cert')}
        >
          <Shield size={16} /> Compliance Certificate & Export
        </button>
      </div>
    </header>
  );
}
