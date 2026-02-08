def get_cohort_data(df):
    # First purchase date per customer
    df = df.copy()
    df['OrderPeriod'] = df['InvoiceDate'].dt.to_period('M')
    df.set_index('Customer ID', inplace=True)
    df['CohortGroup'] = df.groupby(level=0)['InvoiceDate'].min().dt.to_period('M')
    df.reset_index(inplace=True)
    
    # Period number
    df['PeriodNumber'] = (df['OrderPeriod'] - df['CohortGroup']).apply(attrgetter('n'))
    
    # Cohort table
    cohort_data = df.groupby(['CohortGroup', 'PeriodNumber'])['Customer ID'].nunique().reset_index()
    cohort_counts = cohort_data.pivot(index='CohortGroup', columns='PeriodNumber', values='Customer ID')
    
    # Retention rates
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    
    return retention

# Plot heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(retention_data, annot=True, fmt='.0%', cmap='YlOrRd')
plt.title('Cohort Analysis: Customer Retention Rates', fontsize=16)
plt.ylabel('Cohort Month')
plt.xlabel('Periods Since First Purchase')
plt.savefig('cohort_retention.png', dpi=300, bbox_inches='tight')