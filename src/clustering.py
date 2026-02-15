"""
Customer clustering using K-Means and other unsupervised methods.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt


class CustomerClustering:
    """Perform K-Means clustering on customer RFM data."""
    
    def __init__(self, rfm_df):
        self.rfm = rfm_df.copy()
        self.features = ['Recency', 'Frequency', 'Monetary']
        self.scaled_features = None
        self.model = None
        self.labels = None
        
    def prepare_features(self, log_transform=True):
        """Prepare features for clustering."""
        feature_df = self.rfm[self.features].copy()
        
        if log_transform:
            # Log transform for skewed data
            feature_df = np.log1p(feature_df)
            
        self.scaler = StandardScaler()
        self.scaled_features = self.scaler.fit_transform(feature_df)
        
        return self.scaled_features
    
    def find_optimal_k(self, k_range=range(2, 11)):
        """Use elbow method and silhouette score to find optimal k."""
        inertias = []
        silhouettes = []
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(self.scaled_features)
            inertias.append(kmeans.inertia_)
            silhouettes.append(silhouette_score(self.scaled_features, kmeans.labels_))
            
        results = pd.DataFrame({
            'k': k_range,
            'inertia': inertias,
            'silhouette': silhouettes
        })
        
        return results
    
    def fit(self, n_clusters=4):
        """Fit K-Means model."""
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.labels = self.model.fit_predict(self.scaled_features)
        self.rfm['Cluster'] = self.labels
        
        # Calculate cluster centers in original scale
        centers_scaled = self.model.cluster_centers_
        self.centers = np.expm1(self.scaler.inverse_transform(centers_scaled))
        
        return self
    
    def get_cluster_summary(self):
        """Get summary statistics for each cluster."""
        summary = self.rfm.groupby('Cluster').agg({
            'CustomerID': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': ['mean', 'sum']
        }).round(2)
        
        summary.columns = ['Count', 'Avg_Recency', 'Avg_Frequency', 'Avg_Monetary', 'Total_Revenue']
        summary['Percentage'] = (summary['Count'] / len(self.rfm) * 100).round(1)
        summary['Revenue_Share'] = (summary['Total_Revenue'] / summary['Total_Revenue'].sum() * 100).round(1)
        
        return summary
    
    def visualize_clusters(self, save_path=None):
        """Create PCA visualization of clusters."""
        pca = PCA(n_components=2)
        pca_features = pca.fit_transform(self.scaled_features)
        
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(pca_features[:, 0], pca_features[:, 1], 
                            c=self.labels, cmap='viridis', alpha=0.6, s=50)
        plt.colorbar(scatter, label='Cluster')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        plt.title('Customer Clusters (PCA Visualization)')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return pca_features


def run_clustering_pipeline(rfm_df, n_clusters=4):
    """Complete clustering pipeline."""
    clusterer = CustomerClustering(rfm_df)
    clusterer.prepare_features(log_transform=True)
    
    # Find optimal k (optional)
    k_results = clusterer.find_optimal_k()
    print("K-Optimization Results:")
    print(k_results)
    
    # Fit model
    clusterer.fit(n_clusters=n_clusters)
    summary = clusterer.get_cluster_summary()
    
    return clusterer, summary, k_results


if __name__ == "__main__":
    rfm = pd.read_csv('../data/processed/rfm_data.csv')
    clusterer, summary, k_results = run_clustering_pipeline(rfm, n_clusters=4)
    print(summary)
    clusterer.rfm.to_csv('../data/processed/customer_clusters.csv', index=False)