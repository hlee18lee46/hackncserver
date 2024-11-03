import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load data
df = pd.read_csv('loan_sanction_train_processed.csv')

# Define features and target
X = df[['income', 'loan', 'duration']]
y = df['decision']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save the model
model_filename = 'loan_approval_model.joblib'
joblib.dump(model, model_filename)
print(f"Model saved as {model_filename}")

# Load the model
loaded_model = joblib.load(model_filename)

# Make predictions with the loaded model
y_pred = loaded_model.predict(X_test)

# Evaluate the loaded model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("Accuracy of loaded model:", accuracy)
print("Classification Report of loaded model:\n", report)
