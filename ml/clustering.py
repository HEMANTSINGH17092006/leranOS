import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib

from ml.preprocessing import FEATURE_COLUMNS

def evaluate_k_candidates(X_scaled, k_range=[2, 3, 4, 5], random_state=42):
    """
    Evaluates KMeans clustering across multiple K values using Inertia and Silhouette Score.
    """
    results = {}
    best_k = k_range[0]
    best_silhouette = -1.0
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        sil_score = float(silhouette_score(X_scaled, labels))
        inertia = float(kmeans.inertia_)
        
        results[k] = {
            "k": k,
            "silhouette_score": round(sil_score, 4),
            "inertia": round(inertia, 2),
            "cluster_sizes": [int(np.sum(labels == i)) for i in range(k)]
        }
        
        if sil_score > best_silhouette:
            best_silhouette = sil_score
            best_k = k
            
    return results, best_k, best_silhouette

def interpret_clusters(kmeans, scaler, feature_names):
    """
    Interprets clusters based on actual centroid statistics in original feature space.
    Generates dynamic, meaningful cluster labels.
    """
    unscaled_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    centers_df = pd.DataFrame(unscaled_centers, columns=feature_names)
    
    cluster_labels = {}
    cluster_details = {}
    
    # Analyze centroids
    for c_id in range(len(centers_df)):
        c_row = centers_df.iloc[c_id]
        avg_score = c_row["avg_quiz_score"]
        accuracy = c_row["quiz_accuracy"]
        consistency = c_row["consistency_score"]
        avg_time = c_row["avg_time_per_question"]
        study_time = c_row["total_study_time"]
        
        # Dynamic label derivation based on statistical properties
        if accuracy >= 80.0 and consistency >= 75.0:
            label = "Strong Performer"
            desc = "High accuracy, strong consistency and steady problem-solving pace."
        elif accuracy >= 62.0 and consistency >= 60.0:
            label = "Developing Learner"
            desc = "Good conceptual understanding with high potential for mastery through targeted practice."
        elif avg_time < 50.0 and accuracy >= 60.0:
            label = "Fast Learner"
            desc = "High solving speed; benefit from focusing on advanced accuracy and edge cases."
        elif consistency >= 70.0 and accuracy < 65.0:
            label = "Consistent Learner"
            desc = "High dedication and consistency; requires foundational concept reinforcement."
        else:
            label = "Needs Support"
            desc = "Requires guided revision in core topics and focused practice on time management."
            
        cluster_info = {
            "cluster_id": c_id,
            "label": label,
            "description": desc,
            "avg_score": round(float(avg_score), 1),
            "accuracy": round(float(accuracy), 1),
            "consistency": round(float(consistency), 1),
            "avg_time_per_question": round(float(avg_time), 1),
            "total_study_time": round(float(study_time), 1)
        }
        cluster_labels[str(c_id)] = label
        cluster_details[str(c_id)] = cluster_info
        
    return cluster_labels, cluster_details

def train_and_save_pipeline(profile_df, models_dir, k_range=[2, 3, 4, 5]):
    """
    Executes full ML training pipeline:
    1. Extracts feature matrix
    2. Scales features with StandardScaler
    3. Evaluates multiple K values
    4. Trains optimal KMeans
    5. Interprets clusters
    6. Saves scaler, model and metadata
    """
    os.makedirs(models_dir, exist_ok=True)
    models_dir = Path(models_dir)
    
    X = profile_df[FEATURE_COLUMNS].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    k_eval_results, best_k, best_silhouette = evaluate_k_candidates(X_scaled, k_range=k_range)
    
    # Fit final KMeans on selected best_k
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    
    cluster_labels, cluster_details = interpret_clusters(kmeans, scaler, FEATURE_COLUMNS)
    
    # Save artifacts
    scaler_path = models_dir / "scaler.pkl"
    kmeans_path = models_dir / "kmeans.pkl"
    metadata_path = models_dir / "model_metadata.json"
    
    joblib.dump(scaler, scaler_path)
    joblib.dump(kmeans, kmeans_path)
    
    metadata = {
        "best_k": best_k,
        "silhouette_score": round(best_silhouette, 4),
        "inertia": round(float(kmeans.inertia_), 2),
        "k_evaluations": k_eval_results,
        "total_learners_trained": len(profile_df),
        "cluster_labels": cluster_labels,
        "cluster_details": cluster_details,
        "feature_columns": FEATURE_COLUMNS
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    return {
        "scaler": scaler,
        "kmeans": kmeans,
        "metadata": metadata,
        "best_k": best_k,
        "silhouette_score": best_silhouette,
        "k_evaluations": k_eval_results,
        "cluster_labels": cluster_labels
    }

def predict_single_learner(learner_features_dict, models_dir):
    """
    Predicts cluster and computes confidence score for a single learner feature dictionary.
    """
    models_dir = Path(models_dir)
    scaler = joblib.load(models_dir / "scaler.pkl")
    kmeans = joblib.load(models_dir / "kmeans.pkl")
    with open(models_dir / "model_metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    # Build vector in exact order
    feat_vec = [learner_features_dict.get(col, 0.0) for col in FEATURE_COLUMNS]
    vec_scaled = scaler.transform([feat_vec])
    
    cluster_id = int(kmeans.predict(vec_scaled)[0])
    
    # Compute confidence based on distance to centroid vs distance to other centroids
    distances = np.linalg.norm(kmeans.cluster_centers_ - vec_scaled, axis=1)
    min_dist = distances[cluster_id]
    
    # Softmax-style or inverse distance confidence mapping (clamped between 75% and 96%)
    exp_neg_dist = np.exp(-distances)
    prob = exp_neg_dist[cluster_id] / np.sum(exp_neg_dist)
    confidence = float(np.clip(prob * 100, 75.0, 96.0))
    
    # Lookup cluster label
    cluster_label = metadata["cluster_labels"].get(str(cluster_id), metadata["cluster_labels"].get(cluster_id, f"Cluster {cluster_id}"))
    
    return {
        "cluster_id": cluster_id,
        "cluster_label": cluster_label,
        "confidence_score": round(confidence, 1),
        "metadata": metadata
    }
