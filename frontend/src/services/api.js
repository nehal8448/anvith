/**
 * EthicPrivAI API Client Service
 */

const API_BASE = "http://localhost:8000/api";

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  async getDatasets() {
    const res = await fetch(`${API_BASE}/datasets`);
    return res.json();
  },

  async getDatasetDetails(datasetId) {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}`);
    return res.json();
  },

  async simulateMechanism(params) {
    const res = await fetch(`${API_BASE}/privacy/mechanisms/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  async perturbDataset(params) {
    const res = await fetch(`${API_BASE}/privacy/perturb`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  async runAnonymization(params) {
    const res = await fetch(`${API_BASE}/privacy/anonymize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  async getBudgetStatus() {
    const res = await fetch(`${API_BASE}/privacy/budget/status`, {
      method: "POST",
    });
    return res.json();
  },

  async resetBudget() {
    const res = await fetch(`${API_BASE}/privacy/budget/reset`, {
      method: "POST",
    });
    return res.json();
  },

  async runDPClustering(params) {
    const res = await fetch(`${API_BASE}/mining/dp-clustering`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  async runDPRules(params) {
    const res = await fetch(`${API_BASE}/mining/dp-rules`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  async trainModelArena(params) {
    const res = await fetch(`${API_BASE}/train-models`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  async getTradeoffFrontier(params) {
    const res = await fetch(`${API_BASE}/tradeoff-analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },
};
