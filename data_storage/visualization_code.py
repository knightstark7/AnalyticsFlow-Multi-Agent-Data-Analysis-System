import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
file_path = 'OnlineSalesData.csv'
df = pd.read_csv(file_path)

# Group by product category and calculate total and mean revenue
revenue_summary = df.groupby('Product Category')['Total Revenue'].agg(['sum', 'mean']).reset_index()

# Rename columns for clarity
revenue_summary.columns = ['Product Category', 'Total Revenue', 'Mean Revenue']

# Set the style for seaborn
sns.set(style='whitegrid')

# Create a bar plot for total revenue
plt.figure(figsize=(12, 6))
sns.barplot(x='Total Revenue', y='Product Category', data=revenue_summary, palette='viridis')
plt.title('Total Revenue by Product Category')
plt.xlabel('Total Revenue ($)')
plt.ylabel('Product Category')
plt.savefig('total_revenue_by_product_category.png')
plt.close()

# Create a bar plot for mean revenue
plt.figure(figsize=(12, 6))
sns.barplot(x='Mean Revenue', y='Product Category', data=revenue_summary, palette='viridis')
plt.title('Mean Revenue by Product Category')
plt.xlabel('Mean Revenue ($)')
plt.ylabel('Product Category')
plt.savefig('mean_revenue_by_product_category.png')
plt.close()