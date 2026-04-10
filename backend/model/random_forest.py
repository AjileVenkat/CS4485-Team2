import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Load feature matrix
dFrame = pd.read_csv("AD_Feature_matrix.csv")

# Select the features and target
X = dFrame.drop(columns=['Subject_ID', 'Group'])
y = dFrame['Group']

parameters = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10],
    'min_samples_leaf': [1, 2, 5],
    'max_features': ['sqrt', 'log2']
}

# Splitting train and temporary data (80/20), and split the temporary data into validation and test data (50/50)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training size: {len(X_train)}")
print(f"Testing size: {len(X_test)}")

# Initialize random forest model and fine tuning parameters with a grid search
random_forest = RandomForestClassifier(random_state=42)
search = GridSearchCV(estimator=random_forest, param_grid=parameters, cv=5, scoring='accuracy', verbose=1)
search.fit(X_train, y_train)

optimal_random_forest = search.best_estimator_
skf = StratifiedKFold(n_splits=5)
cv_scores = cross_val_score(optimal_random_forest, X, y, cv=skf)

print(f"Optimal Parametesr: {search.best_params_}")
# Display performance metrics (will add more metrics for further evaluation)
y_predict = optimal_random_forest.predict(X_test)
print(f"Accuracy Score: {accuracy_score(y_test, y_predict):.2%}")
print("\nClassification Report: ")
print(classification_report(y_test, y_predict, target_names=['Healthy', 'FTD', 'AD']))
print(f"Standard Deviation: {cv_scores.std():.2%}")

joblib.dump(optimal_random_forest, "alzheimers_model.joblib")
print("Saved model")