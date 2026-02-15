import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from operator import attrgetter


class CohortAnalysis:
    """Perform cohort analysis on customer data."""
    
    def __init__(self, df):
        self.df = df.copy()
        self.retention_data = None
        
    def create_cohort_matrix(self):
        """Generate cohort retention matrix."""
        # First purchase date per customer
        df = self.df.copy()
        df['OrderPeriod'] = df['InvoiceDate'].dt.to_period('M')
        df.set_index('CustomerID', inplace=True)
        df['CohortGroup'] = df.groupby(level=0)['InvoiceDate'].min().dt.to_period('M')
        df.reset_index(inplace=True)
        
        # Period number
        df['PeriodNumber'] = (df['OrderPeriod'] - df['CohortGroup']).apply(attrgetter('n'))
        
        # Cohort table
        cohort_data = df.groupby(['CohortGroup', 'PeriodNumber'])['CustomerID'].nunique().reset_index()
        cohort_counts = cohort_data.pivot(index='CohortGroup', columns='PeriodNumber', values='CustomerID')
        
        # Retention rates
        cohort_sizes = cohort_counts.iloc[:, 0]
        retention = cohort_counts.divide(cohort_sizes, axis=0)
        
        self.retention_data = retention
        return retention
    
    def visualize_cohort(self, save_path='dashboards/cohort_retention.png'):
        """Plot cohort retention heatmap."""
        if self.retention_data is None:
            self.create_cohort_matrix()
            
        plt.figure(figsize=(12, 8))
        sns.heatmap(self.retention_data, annot=True, fmt='.0%', cmap='YlOrRd')
        plt.title('Cohort Analysis: Customer Retention Rates', fontsize=16)
        plt.ylabel('Cohort Month')
        plt.xlabel('Periods Since First Purchase')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()