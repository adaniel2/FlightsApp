# train_model.py
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load prepared data
df = pd.read_csv('prepared_data.csv')

# Split your dataset into features and target variable
X = df.drop(['FlightDate', 'ArrDelayMinutes', 'DepDelayMinutes'], axis=1)
y = df['ArrDelayMinutes']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize and train the decision tree classifier
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)

# Save the trained model
joblib.dump(clf, 'flight_delay_predictor.joblib')

if __name__ == '__main__':
    print("Model training complete.")
