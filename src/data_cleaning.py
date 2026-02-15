"""
Data loading and cleaning utilities for e-commerce analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime


class DataLoader:
    """Handle loading and cleaning of online retail data."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        
    def load_data(self):
        """Load raw data from CSV or Excel."""
        if self.filepath.endswith('.csv'):
            self.df = pd.read_csv(self.filepath)
        elif self.filepath.endswith(('.xlsx', '.xls')):
            self.df = pd.read_excel(self.filepath)
        else:
            raise ValueError("File must be .csv or .xlsx")
        
        print(f"Loaded {len(self.df)} rows")
        print(f"Columns: {list(self.df.columns)}")
        
        # Standardize column names
        self.standardize_columns()
        
        return self.df
    
    def standardize_columns(self):
        """Standardize column names to consistent format."""
        # Create mapping for common variations
        column_mapping = {
            # Invoice variations
            'Invoice': 'InvoiceNo',
            'invoice': 'InvoiceNo',
            'invoice_no': 'InvoiceNo',
            'InvoiceNumber': 'InvoiceNo',
            
            # Customer ID variations
            'Customer ID': 'CustomerID',
            'customer id': 'CustomerID',
            'customer_id': 'CustomerID',
            'CustomerId': 'CustomerID',
            
            # Price variations
            'Price': 'UnitPrice',
            'price': 'UnitPrice',
            'unit_price': 'UnitPrice',
            'Unit Price': 'UnitPrice',
            
            # Stock code variations
            'StockCode': 'StockCode',
            'stock_code': 'StockCode',
            'Stock Code': 'StockCode',
            
            # Quantity variations
            'quantity': 'Quantity',
            'qty': 'Quantity',
            'Qty': 'Quantity',
            
            # Description variations
            'description': 'Description',
            'desc': 'Description',
            'Desc': 'Description',
            
            # Date variations
            'InvoiceDate': 'InvoiceDate',
            'invoice_date': 'InvoiceDate',
            'Invoice Date': 'InvoiceDate',
            'Date': 'InvoiceDate',
            
            # Country variations
            'country': 'Country',
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in self.df.columns and old_name != new_name:
                self.df.rename(columns={old_name: new_name}, inplace=True)
                print(f"  Renamed: '{old_name}' → '{new_name}'")
        
        return self.df
    
    def clean_data(self):
        """Apply standard cleaning pipeline."""
        if self.df is None:
            raise ValueError("Load data first!")
            
        df = self.df.copy()
        
        # Remove rows with missing Customer ID
        initial_rows = len(df)
        df = df.dropna(subset=['CustomerID'])
        print(f"Removed {initial_rows - len(df)} rows with missing CustomerID")
        
        # Remove cancelled orders (Invoice starting with 'C')
        df = df[~df['InvoiceNo'].astype(str).str.contains('C', na=False)]
        
        # Remove negative quantities and prices
        df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
        
        # Calculate total amount
        df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
        
        # Convert date
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        # Remove outliers (optional - adjust thresholds)
        df = df[df['TotalAmount'] < 10000]  # Remove extreme outliers
        
        self.df = df
        print(f"Final clean dataset: {len(df)} rows, {df['CustomerID'].nunique()} customers")
        return df
    
    def save_clean_data(self, output_path):
        """Save cleaned data to CSV."""
        if self.df is not None:
            self.df.to_csv(output_path, index=False)
            print(f"Saved to {output_path}")
        else:
            raise ValueError("No data to save!")


def load_and_clean(filepath, output_path=None):
    """Convenience function to load and clean in one step."""
    loader = DataLoader(filepath)
    loader.load_data()
    loader.clean_data()
    if output_path:
        loader.save_clean_data(output_path)
    return loader.df


if __name__ == "__main__":
    df = load_and_clean(
        '../data/raw/online_retail.csv',
        '../data/processed/online_retail_cleaned.csv'
    )