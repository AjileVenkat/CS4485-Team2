import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

dFrame = pd.read_csv("AD_Feature_matrix.csv")

X = dFrame.drop(columns=['Subject_ID', 'Group'])
y = dFrame['Group']

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42)

X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

print(f"Training sie: {len(X_train)}")
print(f"Testing size: {len(X_test)}")

random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
random_forest.fit(X_train, y_train)

y_predict = random_forest.predict(X_test)
print(f"Accuracy Score: {accuracy_score(y_test, y_predict):.2%}")
print("\nClassification Report: ")
print(classification_report(y_test, y_predict, target_names=['Healthy', 'MCI', 'AD']))
joblib.dump(random_forest, "alzheimers_model.joblib")
print("Saved model")