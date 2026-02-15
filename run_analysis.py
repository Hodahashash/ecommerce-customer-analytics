"""
E-Commerce Customer Behavior Analysis - Master Pipeline
========================================================

This script runs the complete analysis pipeline:
1. Load and clean data
2. RFM analysis and customer segmentation
3. K-Means clustering
4. Cohort analysis
5. Generate visualizations and reports

Usage:
    python run_analysis.py

Requirements:
    - Excel file in data/raw/ folder
    - All dependencies installed (pip install -r requirements.txt)
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt


# Add src to path
sys.path.append('src')

from data_cleaning import DataLoader
from rfm_analysis import RFMAnalyzer
from clustering import CustomerClustering
from cohort_analysis import CohortAnalysis


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def ensure_directories():
    """Create necessary directories if they don't exist."""
    dirs = ['data/processed', 'dashboards', 'reports']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def load_and_clean_data(data_path):
    """Load and clean the raw data."""
    print_section("STEP 1: DATA LOADING & CLEANING")
    
    if not os.path.exists(data_path):
        print(f"\n❌ ERROR: Data file not found at: {data_path}")
        print("\nPlease place your Excel file in the data/raw/ folder.")
        print("Expected filename: online_retail_II.xlsx")
        print("\nOr update the data_path variable in this script.")
        sys.exit(1)
    
    loader = DataLoader(data_path)
    df = loader.load_data()
    df_clean = loader.clean_data()
    
    # Save cleaned data
    output_path = 'data/processed/online_retail_cleaned.csv'
    loader.save_clean_data(output_path)
    
    # Print summary statistics
    print(f"\n📊 Dataset Summary:")
    print(f"   • Date Range: {df_clean['InvoiceDate'].min()} to {df_clean['InvoiceDate'].max()}")
    print(f"   • Total Transactions: {len(df_clean):,}")
    print(f"   • Unique Customers: {df_clean['CustomerID'].nunique():,}")
    print(f"   • Unique Invoices: {df_clean['InvoiceNo'].nunique():,}")
    print(f"   • Total Revenue: ${df_clean['TotalAmount'].sum():,.2f}")
    print(f"   • Average Order Value: ${df_clean.groupby('InvoiceNo')['TotalAmount'].sum().mean():,.2f}")
    
    return df_clean


def run_rfm_analysis(df):
    """Perform RFM analysis and customer segmentation."""
    print_section("STEP 2: RFM ANALYSIS & SEGMENTATION")
    
    # Initialize analyzer
    analyzer = RFMAnalyzer(
        df, 
        customer_col='CustomerID',
        date_col='InvoiceDate',
        amount_col='TotalAmount',
        invoice_col='InvoiceNo'
    )
    
    # Calculate RFM metrics
    rfm = analyzer.calculate_rfm()
    
    # Score RFM
    rfm_scored = analyzer.score_rfm(rfm)
    
    # Segment customers
    rfm_final = analyzer.segment_customers(rfm_scored)
    
    # Get segment summary
    summary = analyzer.get_segment_summary(rfm_final)
    
    print(f"\n📈 RFM Segment Summary:")
    print(summary.to_string())
    
    # Save results
    rfm_final.to_csv('data/processed/rfm_analysis.csv', index=False)
    print(f"\n✅ Saved: data/processed/rfm_analysis.csv")
    
    return rfm_final, summary


def run_clustering(rfm_df):
    """Perform K-Means clustering on customer data."""
    print_section("STEP 3: CUSTOMER CLUSTERING (K-MEANS)")
    
    # Initialize clusterer
    clusterer = CustomerClustering(rfm_df)
    
    # Prepare features
    clusterer.prepare_features(log_transform=True)
    
    # Find optimal k
    print("\n🔍 Finding optimal number of clusters...")
    k_results = clusterer.find_optimal_k(k_range=range(2, 8))
    print(k_results.to_string(index=False))
    
    # Fit model with k=4
    print(f"\n🎯 Fitting model with k=4 clusters...")
    clusterer.fit(n_clusters=4)
    
    # Get cluster summary
    cluster_summary = clusterer.get_cluster_summary()
    
    print(f"\n📊 Cluster Summary:")
    print(cluster_summary.to_string())
    
    # Save results
    clusterer.rfm.to_csv('data/processed/customer_clusters.csv', index=False)
    print(f"\n✅ Saved: data/processed/customer_clusters.csv")
    
    return clusterer, cluster_summary, k_results


def run_cohort_analysis(df):
    """Perform cohort retention analysis."""
    print_section("STEP 4: COHORT RETENTION ANALYSIS")
    
    try:
        cohort_analyzer = CohortAnalysis(df)
        cohort_matrix = cohort_analyzer.create_cohort_matrix()
        
        # Save results
        cohort_matrix.to_csv('data/processed/cohort_analysis.csv')
        print(f"\n✅ Saved: data/processed/cohort_analysis.csv")
        
        # Print first few cohorts
        print(f"\n📊 Cohort Retention Matrix (first 5 cohorts):")
        print(cohort_matrix.head().to_string())
        
        return cohort_matrix
    except Exception as e:
        print(f"\n⚠️  Cohort analysis encountered an issue: {str(e)}")
        print("Continuing with other analyses...")
        return None


def generate_visualizations(df, rfm_df, clusterer):
    """Generate all analysis visualizations."""
    print_section("STEP 5: GENERATING VISUALIZATIONS")
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    
    # 1. RFM Distributions
    print("\n📊 Creating RFM distribution plots...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('RFM Analysis - Distribution Overview', fontsize=16, fontweight='bold')
    
    # Recency
    axes[0, 0].hist(rfm_df['Recency'], bins=50, edgecolor='black', alpha=0.7, color='skyblue')
    axes[0, 0].set_title('Recency Distribution', fontweight='bold')
    axes[0, 0].set_xlabel('Days Since Last Purchase')
    axes[0, 0].set_ylabel('Number of Customers')
    
    # Frequency
    axes[0, 1].hist(rfm_df['Frequency'], bins=30, edgecolor='black', alpha=0.7, color='lightcoral')
    axes[0, 1].set_title('Frequency Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('Number of Purchases')
    axes[0, 1].set_ylabel('Number of Customers')
    
    # Monetary
    axes[1, 0].hist(rfm_df['Monetary'], bins=50, edgecolor='black', alpha=0.7, color='lightgreen')
    axes[1, 0].set_title('Monetary Distribution', fontweight='bold')
    axes[1, 0].set_xlabel('Total Spend ($)')
    axes[1, 0].set_ylabel('Number of Customers')
    
    # Segments
    segment_counts = rfm_df['Segment'].value_counts()
    axes[1, 1].bar(range(len(segment_counts)), segment_counts.values, 
                   edgecolor='black', alpha=0.7, color='plum')
    axes[1, 1].set_xticks(range(len(segment_counts)))
    axes[1, 1].set_xticklabels(segment_counts.index, rotation=45, ha='right')
    axes[1, 1].set_title('Customer Segments', fontweight='bold')
    axes[1, 1].set_ylabel('Number of Customers')
    
    plt.tight_layout()
    plt.savefig('dashboards/rfm_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ rfm_distributions.png")
    
    # 2. Cluster Visualization
    print("\n📊 Creating cluster visualization (PCA)...")
    clusterer.visualize_clusters(save_path='dashboards/customer_clusters_pca.png')
    print("   ✓ customer_clusters_pca.png")
    
    # 3. Revenue by Segment
    print("\n📊 Creating segment revenue chart...")
    segment_revenue = rfm_df.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(14, 7))
    bars = plt.bar(range(len(segment_revenue)), segment_revenue.values, 
                   edgecolor='black', alpha=0.7, color='teal')
    plt.xticks(range(len(segment_revenue)), segment_revenue.index, rotation=45, ha='right')
    plt.title('Total Revenue by Customer Segment', fontsize=14, fontweight='bold', pad=20)
    plt.ylabel('Revenue ($)', fontsize=12)
    plt.xlabel('Customer Segment', fontsize=12)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, segment_revenue.values)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('dashboards/segment_revenue.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ segment_revenue.png")
    
    # 4. Monthly Revenue Trend
    print("\n📊 Creating monthly revenue trend...")
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    monthly_sales = df.groupby('YearMonth')['TotalAmount'].sum()
    
    plt.figure(figsize=(16, 7))
    plt.plot(monthly_sales.index.astype(str), monthly_sales.values, 
            marker='o', linewidth=2, markersize=8, color='darkblue')
    plt.title('Monthly Revenue Trend', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Revenue ($)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig('dashboards/monthly_revenue_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ monthly_revenue_trend.png")
    
    # 5. Customer Lifetime Value Distribution
    print("\n📊 Creating CLV distribution...")
    plt.figure(figsize=(12, 6))
    plt.hist(rfm_df['Monetary'], bins=100, edgecolor='black', alpha=0.7, color='orange')
    plt.axvline(rfm_df['Monetary'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f"Mean: ${rfm_df['Monetary'].mean():,.2f}")
    plt.axvline(rfm_df['Monetary'].median(), color='green', linestyle='--', 
                linewidth=2, label=f"Median: ${rfm_df['Monetary'].median():,.2f}")
    plt.title('Customer Lifetime Value Distribution', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Total Customer Value ($)', fontsize=12)
    plt.ylabel('Number of Customers', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig('dashboards/clv_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ clv_distribution.png")
    
    print(f"\n✅ All visualizations saved to dashboards/")


def generate_summary_report(df, rfm_summary, cluster_summary):
    """Generate a summary report with key metrics."""
    print_section("STEP 6: GENERATING SUMMARY REPORT")
    
    report = f"""
# E-COMMERCE CUSTOMER BEHAVIOR ANALYSIS
## Summary Report

### Dataset Overview
- **Analysis Period**: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}
- **Total Transactions**: {len(df):,}
- **Unique Customers**: {df['CustomerID'].nunique():,}
- **Total Revenue**: ${df['TotalAmount'].sum():,.2f}
- **Average Order Value**: ${df.groupby('InvoiceNo')['TotalAmount'].sum().mean():,.2f}

### RFM Segmentation Results

{rfm_summary.to_markdown()}

### Customer Clustering Results

{cluster_summary.to_markdown()}

### Key Insights

1. **Customer Distribution**:
   - {rfm_summary.loc[rfm_summary.index[0], 'Count']} customers ({rfm_summary.loc[rfm_summary.index[0], 'Percentage']}%) in the "{rfm_summary.index[0]}" segment
   - This segment contributes {rfm_summary.loc[rfm_summary.index[0], 'Revenue_Share']}% of total revenue

2. **Revenue Concentration**:
   - Top segment generates ${rfm_summary.loc[rfm_summary.index[0], 'Total_Revenue']:,.2f}
   - Average monetary value per customer: ${rfm_summary['Avg_Monetary'].mean():,.2f}

3. **Clustering Insights**:
   - {len(cluster_summary)} distinct customer clusters identified
   - Cluster sizes range from {cluster_summary['Count'].min()} to {cluster_summary['Count'].max()} customers

### Recommendations

1. **Focus on At-Risk Customers**: Implement win-back campaigns
2. **Nurture Champions**: Create loyalty programs and VIP benefits
3. **Convert New Customers**: Strengthen onboarding processes
4. **Optimize Inventory**: Plan based on seasonal trends identified

---

*Generated by: E-Commerce Analytics Pipeline*
*Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    # Save report
    with open('reports/ANALYSIS_SUMMARY.md', 'w') as f:
        f.write(report)
    
    print(f"\n✅ Saved: reports/ANALYSIS_SUMMARY.md")
    
    return report


def main():
    """Run the complete analysis pipeline."""
    
    print("\n" + "=" * 70)
    print("  E-COMMERCE CUSTOMER BEHAVIOR ANALYSIS PIPELINE")
    print("=" * 70)
    print("\n🚀 Starting analysis...")
    
    # Ensure directories exist
    ensure_directories()
    
    # Define data path (UPDATE THIS if your file has a different name or location)
    data_path = 'data/raw/online_retail_II.xlsx'
    
    try:
        # Step 1: Load and clean data
        df_clean = load_and_clean_data(data_path)
        
        # Step 2: RFM Analysis
        rfm_final, rfm_summary = run_rfm_analysis(df_clean)
        
        # Step 3: Customer Clustering
        clusterer, cluster_summary, k_results = run_clustering(rfm_final)
        
        # Step 4: Cohort Analysis
        cohort_matrix = run_cohort_analysis(df_clean)
        
        # Step 5: Generate Visualizations
        generate_visualizations(df_clean, rfm_final, clusterer)
        
        # Step 6: Generate Summary Report
        report = generate_summary_report(df_clean, rfm_summary, cluster_summary)
        
        # Final Summary
        print_section("ANALYSIS COMPLETE!")
        print("\n📁 Generated Files:")
        print("   ✓ data/processed/online_retail_cleaned.csv")
        print("   ✓ data/processed/rfm_analysis.csv")
        print("   ✓ data/processed/customer_clusters.csv")
        print("   ✓ data/processed/cohort_analysis.csv")
        print("   ✓ dashboards/rfm_distributions.png")
        print("   ✓ dashboards/customer_clusters_pca.png")
        print("   ✓ dashboards/segment_revenue.png")
        print("   ✓ dashboards/monthly_revenue_trend.png")
        print("   ✓ dashboards/clv_distribution.png")
        print("   ✓ reports/ANALYSIS_SUMMARY.md")
        
        print("\n📊 Next Steps:")
        print("   1. Review the summary report in reports/ANALYSIS_SUMMARY.md")
        print("   2. Explore visualizations in dashboards/")
        print("   3. Open notebooks/ for detailed interactive analysis")
        print("   4. Share results with stakeholders")
        
        print("\n" + "=" * 70)
        print("  ✅ SUCCESS! All analyses completed successfully")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        print("\nPlease check:")
        print("  1. Data file exists in data/raw/")
        print("  2. All dependencies are installed (pip install -r requirements.txt)")
        print("  3. File format and column names are correct")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
