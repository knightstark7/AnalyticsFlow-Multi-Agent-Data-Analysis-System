import pandas as pd

# Load the dataset
file_path = 'OnlineSalesData.csv'
data = pd.read_csv(file_path)

# Display basic information about the dataset
print('Data Overview:')
print(data.info())

# Check for missing values
print('\nMissing Values:')
print(data.isnull().sum())

# Group data by Product Category and calculate total revenue for each category
grouped_data = data.groupby('Product Category')['Total Revenue'].sum().reset_index()

# Display the grouped data
print('\nTotal Revenue by Product Category:')
print(grouped_data)

# Perform a basic statistical analysis
# Calculate mean revenue for each category
mean_revenue = data.groupby('Product Category')['Total Revenue'].mean().reset_index()

# Display the mean revenue by category
print('\nMean Revenue by Product Category:')
print(mean_revenue)

# Identify categories with significantly higher mean revenue
# For simplicity, we'll consider categories with mean revenue > overall mean as significant
overall_mean_revenue = data['Total Revenue'].mean()
significant_categories = mean_revenue[mean_revenue['Total Revenue'] > overall_mean_revenue]

# Display significant categories
print('\nSignificant Categories (Mean Revenue > Overall Mean):')
print(significant_categories)