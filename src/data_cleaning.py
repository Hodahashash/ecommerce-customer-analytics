import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_excel('online_retail_II.xlsx', sheet_name='Year 2010-2011')

# Data cleaning (industry standard approach [^5^])
df = df.dropna(subset=['Customer ID'])
df = df[~df['Invoice'].str.contains('C', na=False)]  # Remove cancellations
df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
df['TotalAmount'] = df['Quantity'] * df['Price']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])