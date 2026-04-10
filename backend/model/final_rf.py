# Model training from feature matrix
# Import libraries
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold, RepeatedStratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Load dataframe, drop id columns
dataframe = pd.read_csv("Final_AD_Feature_Matrix.csv")
dataframe.columns = dataframe.columns.str.strip()
X = dataframe.drop(columns =['Subject_ID', 'Group'])
y = dataframe['Group']

# 80/20 Train test split (preprocess data)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
pipeline = Pipeline([('selector', VarianceThreshold(threshold=0.0)), ('scaler', StandardScaler()), ('rf', RandomForestClassifier(random_state=42, class_weight="balanced_subsample"))])
parameters = {'rf__n_estimators': [100, 200], 'rf__max_depth': [5, 7, 10], 'rf__min_samples_leaf': [1, 2], 'rf__min_samples_split': [2, 5], 'rf__max_features': ['sqrt']}

# Perform k fold to better data train, fine tune parameters with grid search, Find the best model from parameter search
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
find_best_params = GridSearchCV(estimator=pipeline, param_grid=parameters, cv=cv, scoring='f1_macro', verbose=0, n_jobs=-1)
find_best_params.fit(X_train, y_train)
opt_model = find_best_params.best_estimator_
y_pred_final = opt_model.predict(X_test)

# Perform full cross validation and calculate score metrics
cv_final = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
cv_scores = cross_val_score(opt_model, X, y, cv=cv_final, scoring='f1_macro', n_jobs=-1)

# Save model for future use
joblib.dump(opt_model, "final_ad_model.joblib")

# Print sizes and metrics (we may add more to better evaluate)
print(f"Training size: {len(X_train)}")     # Should have 1000+ entries to account for epochs per subject
print(f"Test size:  {len(X_test)}")
print(f"\n Model Accuracy: {accuracy_score(y_test, y_pred_final):.2%}")
print(f"\n Best Parameters: {find_best_params.best_params_}")
print("\n Classification report: ")
print(classification_report(y_test, y_pred_final, zero_division=0))
print(f"Model F1 Macro: {cv_scores.mean():.4f}")
print(f"Model Standard Deviation: {cv_scores.std():.4f}")