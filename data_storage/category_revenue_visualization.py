import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the sales data
data = pd.read_csv('OnlineSalesData.csv')

# Create a bar plot for total revenue by product category
plt.figure(figsize=(12, 6))
sns.barplot(x='Product Category', y='Total Revenue', data=data, palette='viridis')
plt.title('Total Revenue by Product Category')
plt.xlabel('Product Category')
plt.ylabel('Total Revenue')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the visualization
plt.savefig('total_revenue_by_product_category.png')
plt.show()