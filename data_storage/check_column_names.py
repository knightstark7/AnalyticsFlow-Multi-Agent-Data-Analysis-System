import pandas as pd

# Load the sales data
data = pd.read_csv('OnlineSalesData.csv')

# Display the column names of the dataframe
print(data.columns)