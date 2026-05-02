# Random forest binary classifiers experiments
# Evaluate the 3 model choices we chose

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

#  Random forest pipeline
pl = Pipeline([
    ('scaler', StandardScaler()), ('rf', RandomForestClassifier(random_state=42, class_weight="balanced"))
])

# Hyper parameters
params = {
    'rf__n_estimators': [50, 100, 200],
    'rf__max_depth': [None, 5, 10],
    'rf__min_samples_split': [2, 5],
    'rf__criterion': ['gini', 'entropy']
}

# Metric training function
def binary_test(df):
    pairs = [
        ((0, 1), "Healthy vs FTD"),
        ((0, 2), "Healthy vs AD"),
        ((1, 2), "AD vs FTD")
    ]

    for (i, j), name in pairs:
        pair_data = df[df['Group'].isin([i, j])].dropna()
        features = pair_data.drop(columns=['Subject_ID', 'Group'])
        classes = (pair_data['Group'] == j).astype(int)

        skfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = {
            'accuracy': 'accuracy',
            'f1': 'f1',
            'precision': 'precision',
            'recall': 'recall'
        }

        search = GridSearchCV(pl, param_grid=params, cv=skfold, scoring='accuracy')
        search.fit(features, classes)

        results = cross_validate(search.best_estimator_, features, classes, cv=skfold, scoring=scoring)
        print(f"{name} (Random Forest CV)")
        print(f"Best Params: {search.best_params_}")
        print(f"Accuracy: {results['test_accuracy'].mean():.2%}")
        print(f"Precision: {results['test_precision'].mean():.2%}")
        print(f"Recall: {results['test_recall'].mean():.2%}")
        print(f"F1 Score: {results['test_f1'].mean():.2%}")

# Print the results
if __name__ == "__main__":
    data = pd.read_csv("Final_AD_Feature_Matrix.csv")
    mi_cols = [c for c in data.columns if "Corr_" in c]
    data[mi_cols] = np.log1p(data[mi_cols])
    binary_test(data)