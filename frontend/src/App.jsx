import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import OverviewTab from './components/OverviewTab';
import DPSandboxTab from './components/DPSandboxTab';
import AnonymizationTab from './components/AnonymizationTab';
import FairnessTab from './components/FairnessTab';
import MiningArenaTab from './components/MiningArenaTab';
import ComplianceCertTab from './components/ComplianceCertTab';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('adult');
  const [budgetStatus, setBudgetStatus] = useState(null);
  const [arenaResults, setArenaResults] = useState(null);
  const [loadingArena, setLoadingArena] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);

  // Initialize data
  useEffect(() => {
    async function init() {
      try {
        const health = await api.getHealth();
        if (health && health.status === 'ok') {
          setApiConnected(true);
        }

        const ds = await api.getDatasets();
        setDatasets(ds);

        const bStatus = await api.getBudgetStatus();
        setBudgetStatus(bStatus);

        // Pre-run arena training so metrics populate immediately
        setLoadingArena(true);
        const arena = await api.trainModelArena({
          dataset_id: 'adult',
          epsilon: 1.0,
          test_size: 0.3,
          mitigate_bias: true,
          seed: 42
        });
        setArenaResults(arena);
      } catch (err) {
        console.error('Initialization error:', err);
        setApiConnected(false);
      } finally {
        setLoadingArena(false);
      }
    }
    init();
  }, []);

  const refreshBudget = async () => {
    try {
      const b = await api.getBudgetStatus();
      setBudgetStatus(b);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRunArena = async () => {
    setLoadingArena(true);
    try {
      const arena = await api.trainModelArena({
        dataset_id: selectedDataset,
        epsilon: 1.0,
        test_size: 0.3,
        mitigate_bias: true,
        seed: 42
      });
      setArenaResults(arena);
      await refreshBudget();
    } catch (err) {
      console.error('Error running arena:', err);
    } finally {
      setLoadingArena(false);
    }
  };

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        datasets={datasets}
        selectedDataset={selectedDataset}
        setSelectedDataset={(ds) => {
          setSelectedDataset(ds);
          // Auto-trigger re-evaluation on dataset change
          setTimeout(() => handleRunArena(), 100);
        }}
        budgetStatus={budgetStatus}
        apiConnected={apiConnected}
      />

      {/* Main Tab Content */}
      <main>
        {activeTab === 'overview' && (
          <OverviewTab
            datasets={datasets}
            selectedDataset={selectedDataset}
            setSelectedDataset={setSelectedDataset}
            onQuickTrain={() => {
              setActiveTab('arena');
              handleRunArena();
            }}
          />
        )}

        {activeTab === 'dp-sandbox' && (
          <DPSandboxTab
            budgetStatus={budgetStatus}
            onRefreshBudget={refreshBudget}
          />
        )}

        {activeTab === 'anonymization' && (
          <AnonymizationTab
            datasets={datasets}
            selectedDataset={selectedDataset}
            onRefreshBudget={refreshBudget}
          />
        )}

        {activeTab === 'fairness' && (
          <FairnessTab
            arenaResults={arenaResults}
            onRunArena={handleRunArena}
          />
        )}

        {activeTab === 'arena' && (
          <MiningArenaTab
            selectedDataset={selectedDataset}
            arenaResults={arenaResults}
            onRunArena={handleRunArena}
            loadingArena={loadingArena}
            onRefreshBudget={refreshBudget}
          />
        )}

        {activeTab === 'cert' && (
          <ComplianceCertTab
            arenaResults={arenaResults}
            selectedDataset={selectedDataset}
          />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: '2rem',
        padding: '1.5rem',
        textAlign: 'center',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: '0.8rem',
        color: 'var(--text-dim)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.5rem'
      }}>
        <span>EthicPrivAI Framework &bull; Privacy-Preserving Data Mining for Ethical AI Systems</span>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <span>Differential Privacy &epsilon;-Guarantees</span>
          <span>&bull;</span>
          <span>Four-Fifths Rule Fairness</span>
          <span>&bull;</span>
          <span>EU AI Act &amp; NIST Aligned</span>
        </div>
      </footer>
    </div>
  );
}
