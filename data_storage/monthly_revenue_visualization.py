import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
file_path = 'OnlineSalesData.csv'
df = pd.read_csv(file_path)

df['Date'] = pd.to_datetime(df['Date'])

df['Total Revenue'] = df['Total Revenue'].astype(float)

# Group by month and sum the total revenue
monthly_revenue = df.resample('M', on='Date').sum()['Total Revenue']

# Create a line plot for monthly revenue trends
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_revenue, marker='o')
plt.title('Monthly Revenue Trends', fontsize=16)
plt.xlabel('Month', fontsize=14)
plt.ylabel('Total Revenue ($)', fontsize=14)
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('monthly_revenue_trends.png')
plt.show()