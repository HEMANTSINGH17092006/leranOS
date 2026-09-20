import sys
from pathlib import Path
import json

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from ml.preprocessing import load_raw_data, aggregate_learner_profiles
from ml.clustering import train_and_save_pipeline

def main():
    print("=" * 60)
    print("AI-BASED PERSONALISED LEARNING SYSTEM - ML TRAINING")
    print("=" * 60)
    
    csv_path = Config.LEARNING_DATA_PATH
    if not csv_path.exists():
        print(f"Error: Dataset not found at {csv_path}. Please run data/generate_data.py first.")
        sys.exit(1)
        
    print(f"\n[1/4] Loading dataset from: {csv_path}")
    raw_df = load_raw_data(csv_path)
    print(f"      Total Records Loaded: {len(raw_df)}")
    
    print("\n[2/4] Aggregating learner-level feature profiles...")
    profile_df = aggregate_learner_profiles(raw_df)
    print(f"      Distinct Learners Aggregated: {len(profile_df)}")
    print(f"      Feature Dimensions: {profile_df.shape[1] - 1} metrics")
    
    print("\n[3/4] Running K-Means multi-K candidate evaluation (K = 2, 3, 4, 5)...")
    result = train_and_save_pipeline(profile_df, Config.MODELS_DIR, k_range=[2, 3, 4, 5])
    
    print("\n" + "-" * 60)
    print("  K-EVALUATION RESULTS (Inertia & Silhouette Scores)")
    print("-" * 60)
    for k, metrics in result["k_evaluations"].items():
        is_selected = " [BEST K SELECTED]" if k == result["best_k"] else ""
        print(f"  K = {k:2d} | Silhouette Score = {metrics['silhouette_score']:.4f} | Inertia = {metrics['inertia']:10.2f} | Cluster Sizes = {metrics['cluster_sizes']}{is_selected}")
    print("-" * 60)
    
    print(f"\n[4/4] Optimal Cluster Model Selected:")
    print(f"      Selected Best K: {result['best_k']}")
    print(f"      Actual Silhouette Score: {result['silhouette_score']:.4f}")
    print(f"\n      Discovered Learner Segments:")
    for c_id, label in result["cluster_labels"].items():
        details = result["metadata"]["cluster_details"].get(str(c_id), {})
        print(f"      - Cluster {c_id}: {label}")
        print(f"        (Avg Accuracy: {details.get('accuracy', 0)}%, Consistency: {details.get('consistency', 0)}%, Avg Time: {details.get('avg_time_per_question', 0)}s)")
        
    print(f"\nModel artifacts successfully saved to:")
    print(f"  - Scaler:   {Config.SCALER_PATH}")
    print(f"  - KMeans:   {Config.KMEANS_PATH}")
    print(f"  - Metadata: {Config.METADATA_PATH}")
    print("=" * 60)
    print("ML TRAINING COMPLETE\n")

if __name__ == "__main__":
    main()
