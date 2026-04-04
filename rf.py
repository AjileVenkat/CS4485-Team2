import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    StratifiedKFold,
    RepeatedStratifiedKFold,
    cross_val_score
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import Pipeline

# Load feature matrix
dFrame = pd.read_csv("Final_AD_Feature_Matrix.csv")
dFrame.columns = dFrame.columns.str.strip()

# Features and target
X = dFrame.drop(columns=['Subject_ID', 'Group'])
y = dFrame['Group']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Pipeline
pipeline = Pipeline([
    ('selector', VarianceThreshold(threshold=0.0)),
    ('scaler', StandardScaler()),
    ('rf', RandomForestClassifier(
        random_state=42,
        class_weight="balanced_subsample"
    ))
])

# Parameter grid
parameters = {
    'rf__n_estimators': [100, 200],
    'rf__max_depth': [5, 7, 10],
    'rf__min_samples_leaf': [1, 2],
    'rf__min_samples_split': [2, 5],
    'rf__max_features': ['sqrt']
}

# Grid search
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

search = GridSearchCV(
    estimator=pipeline,
    param_grid=parameters,
    cv=cv,
    scoring='f1_macro',
    verbose=0,
    n_jobs=-1
)

search.fit(X_train, y_train)

best_model = search.best_estimator_

# Test prediction
y_predict = best_model.predict(X_test)

# Cross-validation on full dataset
repeated_cv = RepeatedStratifiedKFold(
    n_splits=5,
    n_repeats=10,
    random_state=42
)

cv_scores = cross_val_score(
    best_model,
    X,
    y,
    cv=repeated_cv,
    scoring='f1_macro',
    n_jobs=-1
)

# Clean output
print(f"Training size: {len(X_train)}")
print(f"Testing size: {len(X_test)}")

print(f"\nAccuracy Score: {accuracy_score(y_test, y_predict):.2%}")

print(f"\nOptimal Parameters: {search.best_params_}")

print("\nClassification Report:")
print(classification_report(y_test, y_predict, zero_division=0))

print(f"Cross Validation Mean F1 Macro: {cv_scores.mean():.4f}")
print(f"Cross Validation Std Dev: {cv_scores.std():.4f}")

# Save full pipeline
joblib.dump(best_model, "alzheimers_model.joblib")