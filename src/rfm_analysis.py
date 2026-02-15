"""
RFM (Recency, Frequency, Monetary) analysis module.
"""

import pandas as pd
import numpy as np
from datetime import timedelta


class RFMAnalyzer:
    """Calculate RFM scores and segments for customers."""
    
    def __init__(self, df, customer_col='Customer ID', 
                 date_col='InvoiceDate', amount_col='TotalAmount',
                 invoice_col='Invoice'):
        self.df = df
        self.customer_col = customer_col
        self.date_col = date_col
        self.amount_col = amount_col
        self.invoice_col = invoice_col
        self.rfm = None
        
    def calculate_rfm(self, reference_date=None):
        """Calculate Recency, Frequency, Monetary metrics."""
        
        if reference_date is None:
            reference_date = self.df[self.date_col].max() + timedelta(days=1)
            
        print(f"Reference date: {reference_date}")
        
        # Group by customer
        rfm = self.df.groupby(self.customer_col).agg({
            self.date_col: lambda x: (reference_date - x.max()).days,
            self.invoice_col: 'nunique',
            self.amount_col: ['sum', 'mean']
        }).reset_index()
        
        # Flatten columns
        rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'AvgOrderValue']
        
        # Filter valid customers
        rfm = rfm[(rfm['Monetary'] > 0) & (rfm['Frequency'] > 0)]
        
        self.rfm = rfm
        print(f"Calculated RFM for {len(rfm)} customers")
        return rfm
    
    def score_rfm(self, rfm_df=None):
        """Apply 1-5 scoring to RFM metrics using quintiles."""
        if rfm_df is None:
            rfm_df = self.rfm.copy()
            
        # Recency: lower is better (recent), so reverse scoring
        rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
        
        # Frequency: higher is better
        rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), 
                                    5, labels=[1,2,3,4,5]).astype(int)
        
        # Monetary: higher is better
        rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], 5, labels=[1,2,3,4,5]).astype(int)
        
        # Combined score
        rfm_df['RFM_Score'] = (rfm_df['R_Score'].astype(str) + 
                               rfm_df['F_Score'].astype(str) + 
                               rfm_df['M_Score'].astype(str))
        
        return rfm_df
    
    def segment_customers(self, rfm_df):
        """Apply business rules to segment customers."""
        
        def get_segment(row):
            r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
            
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            elif r >= 3 and f >= 3 and m >= 3:
                return 'Loyal Customers'
            elif r >= 4 and f <= 2:
                return 'New Customers'
            elif r >= 3 and f <= 2 and m >= 3:
                return 'Potential Loyalists'
            elif r <= 2 and f >= 3:
                return 'At Risk'
            elif r <= 2 and f <= 2 and m >= 3:
                return 'Cannot Lose Them'
            elif r <= 2 and f <= 2 and m <= 2:
                return 'Lost Customers'
            else:
                return 'Others'
        
        rfm_df['Segment'] = rfm_df.apply(get_segment, axis=1)
        return rfm_df
    
    def get_segment_summary(self, rfm_df):
        """Generate summary statistics by segment."""
        summary = rfm_df.groupby('Segment').agg({
            'CustomerID': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': ['mean', 'sum']
        }).round(2)
        
        summary.columns = ['Count', 'Avg_Recency', 'Avg_Frequency', 'Avg_Monetary', 'Total_Revenue']
        summary['Percentage'] = (summary['Count'] / len(rfm_df) * 100).round(1)
        summary['Revenue_Share'] = (summary['Total_Revenue'] / summary['Total_Revenue'].sum() * 100).round(1)
        
        return summary.sort_values('Total_Revenue', ascending=False)


def run_rfm_analysis(df):
    """Complete RFM pipeline."""
    analyzer = RFMAnalyzer(df)
    rfm = analyzer.calculate_rfm()
    rfm = analyzer.score_rfm(rfm)
    rfm = analyzer.segment_customers(rfm)
    summary = analyzer.get_segment_summary(rfm)
    return rfm, summary


if __name__ == "__main__":
    # Example
    df = pd.read_csv('../data/processed/online_retail_cleaned.csv')
    rfm, summary = run_rfm_analysis(df)
    print(summary)
    rfm.to_csv('../data/processed/rfm_data.csv', index=False)













# # Calculate RFM metrics
# reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

# rfm = df.groupby('Customer ID').agg({
#     'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
#     'Invoice': 'nunique',  # Frequency
#     'TotalAmount': 'sum'   # Monetary
# }).reset_index()

# rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

# # Remove outliers
# rfm = rfm[rfm['Monetary'] > 0]

# # Log transform for skewed data
# rfm_log = rfm[['Recency', 'Frequency', 'Monetary']].apply(np.log1p)

# # Standardize
# scaler = StandardScaler()
# rfm_scaled = scaler.fit_transform(rfm_log)

# # K-Means clustering (optimal k=4 or 5)
# kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
# rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# # Cluster interpretation
# cluster_summary = rfm.groupby('Cluster').agg({
#     'Recency': 'mean',
#     'Frequency': 'mean',
#     'Monetary': ['mean', 'count']
# }).round(2)

# print(cluster_summary)

