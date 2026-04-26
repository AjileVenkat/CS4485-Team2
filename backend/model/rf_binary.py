import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# 1. Define the RF Pipeline
# Even though RF doesn't strictly need scaling, it's good to keep it 
# for a fair comparison with your SVM file.
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('rf', RandomForestClassifier(random_state=42, class_weight="balanced"))
])

# 2. Hyperparameters for Random Forest
# We focus on 'max_depth' to prevent the trees from "memorizing" the 88 subjects.
parameters = {
    'rf__n_estimators': [50, 100, 200],
    'rf__max_depth': [None, 5, 10], 
    'rf__min_samples_split': [2, 5],
    'rf__criterion': ['gini', 'entropy']
}

def test_binary_pairs_rf(df):
    pairs = [
        ((0, 2), "Healthy vs AD"),
        ((0, 1), "Healthy vs FTD"),
        ((1, 2), "AD vs FTD")
    ]
    
    for (g1, g2), name in pairs:
        pair_df = df[df['Group'].isin([g1, g2])].dropna()
        X_p = pair_df.drop(columns=['Subject_ID', 'Group'])
        y_p_mapped = (pair_df['Group'] == g2).astype(int) 

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        scoring = {
            'accuracy': 'accuracy',
            'f1': 'f1',
            'precision': 'precision',
            'recall': 'recall'
        }

        # Find the best forest configuration
        search = GridSearchCV(pipeline, param_grid=parameters, cv=skf, scoring='accuracy')
        search.fit(X_p, y_p_mapped)
        
        # Cross-validate the best forest
        cv_results = cross_validate(search.best_estimator_, X_p, y_p_mapped, cv=skf, scoring=scoring)

        print(f"--- {name} (Random Forest CV) ---")
        print(f"Best Params: {search.best_params_}")
        print(f"Accuracy:  {cv_results['test_accuracy'].mean():.2%} (+/- {cv_results['test_accuracy'].std():.2%})")
        print(f"F1 Score:  {cv_results['test_f1'].mean():.2%}")
        print(f"Precision: {cv_results['test_precision'].mean():.2%}")
        print(f"Recall:    {cv_results['test_recall'].mean():.2%}")
        

if __name__ == "__main__":
    data = pd.read_csv("AD_Feature_Matrix.csv")
    
    # Keep the Log-transform for consistency
    mi_cols = [c for c in data.columns if "Corr_" in c]
    data[mi_cols] = np.log1p(data[mi_cols])
    
    test_binary_pairs_rf(data)