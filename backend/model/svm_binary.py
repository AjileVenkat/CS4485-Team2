import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score

def test_binary_pairs_refined(df):
    # 1. SUBJECT-LEVEL AVERAGING (The "Speed Hack")
    # This turns 1,320 rows into 88 rows. It's much more stable!
    subject_df = df.groupby('Subject_ID').mean().reset_index()
    
    pairs = [
        ((0, 2), "Healthy vs AD"),
        ((0, 1), "Healthy vs FTD"),
        ((1, 2), "AD vs FTD")
    ]
    
    # Simpler grid = much faster execution
    parameters = {
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto'],
        'kernel': ['rbf', 'linear']
    }

    for (g1, g2), name in pairs:
        pair_df = subject_df[subject_df['Group'].isin([g1, g2])].copy()
        X = pair_df.drop(columns=['Subject_ID', 'Group'])
        y = (pair_df['Group'] == g2).astype(int) 
        
        # Since we averaged, we use standard KFold or Leave-One-Out
        # With only ~60 subjects per pair, 5-fold is perfect
        gkf = GroupKFold(n_splits=5)
        
        # Variables to store results
        fold_accs = []
        fold_f1s = []

        # We manually loop to ensure scaling happens correctly
        for train_idx, test_idx in gkf.split(X, y, groups=pair_df['Subject_ID']):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Scale inside the loop!
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Search and Fit
            search = GridSearchCV(SVC(class_weight='balanced'), parameters, cv=3)
            search.fit(X_train_scaled, y_train)
            
            y_pred = search.predict(X_test_scaled)
            fold_accs.append(accuracy_score(y_test, y_pred))
            fold_f1s.append(f1_score(y_test, y_pred))

        print(f"--- {name} (Valid Subject-Level CV) ---")
        print(f"Accuracy: {np.mean(fold_accs):.2%}")
        print(f"F1 Score: {np.mean(fold_f1s):.2%}")
        print("-" * 30 + "\n")

if __name__ == "__main__":
    data = pd.read_csv("AD_Feature_Matrix.csv")
    
    # Log transform helps normalize skewed EEG power data
    cols_to_log = [c for c in data.columns if "PHI_" in c or "Complexity" in c]
    data[cols_to_log] = np.log1p(data[cols_to_log])
    
    test_binary_pairs_refined(data)