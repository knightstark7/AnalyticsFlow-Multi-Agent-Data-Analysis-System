import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Load the data
data = pd.read_csv('OnlineSalesData.csv')

# Define preprocessing steps
numerical_features = ['Units Sold', 'Unit Price', 'Total Revenue']
categorical_features = ['Product Category', 'Region', 'Payment Method']

# Create transformers
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine transformers into a single ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Preprocess the data
preprocessed_data = preprocessor.fit_transform(data)

# Convert the preprocessed data back to a DataFrame
preprocessed_df = pd.DataFrame(preprocessed_data)

preprocessed_df.head()