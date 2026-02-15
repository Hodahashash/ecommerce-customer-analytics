import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# PCA for 2D visualization
pca = PCA(n_components=2)
rfm_pca = pca.fit_transform(rfm_scaled)

plt.figure(figsize=(12, 8))
scatter = plt.scatter(rfm_pca[:, 0], rfm_pca[:, 1], 
                     c=rfm['Cluster'], cmap='viridis', alpha=0.6)
plt.colorbar(scatter)
plt.title('Customer Segments (PCA Visualization)', fontsize=16)
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
plt.savefig('customer_segments.png', dpi=300, bbox_inches='tight')
plt.show()