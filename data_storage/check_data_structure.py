import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the sales data
data = pd.read_csv('OnlineSalesData.csv')

# Display the first few rows of the dataframe to understand its structure
print(data.head())