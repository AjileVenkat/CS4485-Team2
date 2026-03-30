import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import make_scorer, accuracy_score, f1_score, precision_score, recall_score

# 1. Setup remain the same
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(probability=True, random_state=42, class_weight="balanced"))
])

parameters = {
    'svm__C': [0.1, 1, 10, 100],
    'svm__kernel': ['rbf', 'poly', 'sigmoid', 'linear'],
    'svm__gamma': ['scale', 'auto']
}

def test_binary_pairs(df):
    pairs = [
        ((0, 2), "Healthy vs AD"),
        ((0, 1), "Healthy vs FTD"),
        ((1, 2), "AD vs FTD")
    ]
    
    for (g1, g2), name in pairs:
        pair_df = df[df['Group'].isin([g1, g2])].dropna()
        X_p = pair_df.drop(columns=['Subject_ID', 'Group'])
        y_p = pair_df['Group']
        
        # We need to map y_p to 0 and 1 for the scorers to work correctly
        y_p_mapped = (y_p == g2).astype(int) 

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        # Define the scoring dictionary for CV
        scoring = {
            'accuracy': 'accuracy',
            'f1': 'f1',
            'precision': 'precision',
            'recall': 'recall'
        }

        # Run GridSearch to find best params on the whole set
        search = GridSearchCV(pipeline, param_grid=parameters, cv=skf, scoring='accuracy')
        search.fit(X_p, y_p_mapped)
        
        # 2. THE KEY CHANGE: Run Cross-Validation on the best model
        cv_results = cross_validate(search.best_estimator_, X_p, y_p_mapped, cv=skf, scoring=scoring)

        print(f"--- {name} (5-Fold CV Averages) ---")
        print(f"Best Params: {search.best_params_}")
        print(f"Accuracy:  {cv_results['test_accuracy'].mean():.2%} (+/- {cv_results['test_accuracy'].std():.2%})")
        print(f"F1 Score:  {cv_results['test_f1'].mean():.2%}")
        print(f"Precision: {cv_results['test_precision'].mean():.2%}")
        print(f"Recall:    {cv_results['test_recall'].mean():.2%}")
        print("-" * 30 + "\n")

# 3. Load and Run
if __name__ == "__main__":
    data = pd.read_csv("AD_Feature_Matrix.csv")
    mi_cols = [c for c in data.columns if "Corr_" in c]
    data[mi_cols] = np.log1p(data[mi_cols])
    
    test_binary_pairs(data)