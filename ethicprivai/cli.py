"""
Command-Line Interface (CLI) for EthicPrivAI
============================================
Allows executing privacy-preserving training, fairness auditing,
and anonymization workflows directly from the terminal.
"""

import sys
import argparse
import json
from ethicprivai.datasets.loader import BenchmarkDatasets
from ethicprivai.privacy.differential_privacy import DPLogisticRegression, PrivacyBudgetTracker
from ethicprivai.privacy.anonymization import AnonymizationEngine
from ethicprivai.privacy.attacks import MembershipInferenceAttack
from ethicprivai.ethics.fairness_metrics import FairnessAudit
from ethicprivai.ethics.bias_mitigation import FairReweighing
from ethicprivai.audit.compliance import EthicalAICertifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score


def run_audit(args):
    print(f"\n=======================================================")
    print(f" EthicPrivAI: Auditing {args.dataset.upper()} Dataset")
    print(f" Privacy Budget Epsilon: {args.epsilon}")
    print(f" Bias Mitigation Active: {args.mitigate_bias}")
    print(f"=======================================================\n")

    if args.dataset == "adult":
        df, meta = BenchmarkDatasets.load_adult_census(seed=args.seed)
    elif args.dataset == "healthcare":
        df, meta = BenchmarkDatasets.load_healthcare(seed=args.seed)
    else:
        df, meta = BenchmarkDatasets.load_credit_risk(seed=args.seed)

    target_col = meta["target_column"]
    sensitive_attr = meta["sensitive_attribute"]
    features = [c for c in df.columns if c != target_col]

    X = df[features].values
    y = df[target_col].values
    prot = df[sensitive_attr].values

    X_train, X_test, y_train, y_test, p_train, p_test = train_test_split(
        X, y, prot, test_size=0.3, random_state=args.seed
    )

    sample_weights = None
    if args.mitigate_bias:
        sample_weights = FairReweighing.compute_weights(p_train, y_train)
        print("[*] Applied Kamiran & Calders Fair Reweighing.")

    # Train DP Model
    model = DPLogisticRegression(epsilon=args.epsilon, max_iter=200)
    model.fit(X_train, y_train, sample_weight=sample_weights)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    auc = float(roc_auc_score(y_test, y_proba))

    # Fairness Audit
    fairness = FairnessAudit.audit(
        y_true=y_test,
        y_pred=y_pred,
        protected_attr=p_test,
        privileged_val=meta["privileged_group"],
        unprivileged_val=meta["unprivileged_group"]
    )

    # Privacy Attack Evaluation (MIA)
    mia = MembershipInferenceAttack.evaluate(
        model=model,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test
    )

    # Holistic Certification
    privacy_metrics = {"epsilon": args.epsilon, "privacy_leakage_pct": mia["privacy_leakage_pct"]}
    utility_metrics = {"accuracy": acc, "roc_auc": auc}
    cert = EthicalAICertifier.audit_system(privacy_metrics, fairness, utility_metrics)

    print(f"--- Utility Results ---")
    print(f"  Test Accuracy:        {acc * 100:.2f}%")
    print(f"  Test ROC-AUC:         {auc:.4f}")
    print(f"\n--- Privacy Defense (MIA) ---")
    print(f"  Attack ROC-AUC:       {mia['attack_auc']:.4f}")
    print(f"  Privacy Leakage Risk: {mia['privacy_leakage_pct']:.1f}% ({mia['risk_level']})")
    print(f"\n--- Ethical Fairness Audit ---")
    print(f"  Disparate Impact:     {fairness['disparate_impact_ratio']} (80% Rule: {'PASSED' if fairness['four_fifths_compliant'] else 'FAILED'})")
    print(f"  Demographic Parity:   {fairness['demographic_parity_diff']:.4f}")
    print(f"  Equal Opportunity:    {fairness['equal_opportunity_diff']:.4f}")
    print(f"  Fairness Score:       {fairness['fairness_score_pct']} / 100")
    print(f"\n--- Responsible AI Certification ---")
    print(f"  Ethical AI Index:     {cert['overall_ethical_index']} / 100")
    print(f"  Certification Grade:  {cert['certification_grade']}")
    print(f"  Status:               {cert['certification_status']}\n")


def main():
    parser = argparse.ArgumentParser(description="EthicPrivAI CLI")
    subparsers = parser.add_subparsers(dest="command")

    audit_parser = subparsers.add_parser("audit", help="Run comprehensive ethical & privacy audit")
    audit_parser.add_argument("--dataset", choices=["adult", "healthcare", "credit"], default="adult")
    audit_parser.add_argument("--epsilon", type=float, default=1.0)
    audit_parser.add_argument("--mitigate-bias", action="store_true")
    audit_parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()
    if args.command == "audit":
        run_audit(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
