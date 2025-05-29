import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load preprocessed data
# Assuming 'preprocessed_df' is available from the previous script
# For demonstration, let's simulate a small part of it
np.random.seed(0)
preprocessed_df = pd.DataFrame(np.random.rand(100, 10), columns=[f'feature_{i}' for i in range(10)])

# Simulate a binary target variable for classification
preprocessed_df['target'] = np.random.choice([0, 1], size=100)

# Split the data into training and testing sets
X = preprocessed_df.drop('target', axis=1)
y = preprocessed_df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and fit a logistic regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

accuracy, report