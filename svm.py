import pandas as pd
import joblib
from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    StratifiedKFold,
    RepeatedStratifiedKFold,
    cross_val_score
)
from sklearn.svm import SVC # Swapped from RandomForest
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer # Add this import at the top

# Load feature matrix
dFrame = pd.read_csv("AD_Feature_Matrix2.csv")
dFrame.columns = dFrame.columns.str.strip()

# Features and target
X = dFrame.drop(columns=['Subject_ID', 'Group'])
y = dFrame['Group']

# Train/test split (Exact same as your friend's)
X_train, X_test, y_train, y_test = train_test_split(
    X, 
    y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y
)

# Pipeline - Swapping 'rf' for 'svc'
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')), # This fixes the NaN error automatically
    ('selector', VarianceThreshold(threshold=0.0)),
    ('scaler', StandardScaler()), 
    ('svc', SVC(random_state=42, class_weight='balanced', probability=True))
])

# Parameter grid - SVM specific settings
parameters = {
    'svc__C': [0.1, 1, 10, 100],          # Regularization (how much you penalize errors)
    'svc__gamma': ['scale', 'auto', 0.01], # Kernel coefficient (how "curvy" the boundary is)
    'svc__kernel': ['rbf', 'linear']       # The shape of the decision boundary
}

# Grid search (Exact same CV logic)
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

# Cross-validation
repeated_cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
cv_scores = cross_val_score(best_model, X, y, cv=repeated_cv, scoring='f1_macro', n_jobs=-1)

# Output
print(f"SVM Training size: {len(X_train)}")
print(f"Accuracy Score: {accuracy_score(y_test, y_predict):.2%}")
print(f"Optimal Parameters: {search.best_params_}")
print("\nClassification Report:")
print(classification_report(y_test, y_predict, zero_division=0))
print(f"Cross Validation Mean F1 Macro: {cv_scores.mean():.4f}")

joblib.dump(best_model, "alzheimers_svm_model.joblib")