# Calculate RFM metrics
reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
    'Invoice': 'nunique',  # Frequency
    'TotalAmount': 'sum'   # Monetary
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

# Remove outliers
rfm = rfm[rfm['Monetary'] > 0]

# Log transform for skewed data
rfm_log = rfm[['Recency', 'Frequency', 'Monetary']].apply(np.log1p)

# Standardize
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_log)

# K-Means clustering (optimal k=4 or 5)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# Cluster interpretation
cluster_summary = rfm.groupby('Cluster').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': ['mean', 'count']
}).round(2)

print(cluster_summary)