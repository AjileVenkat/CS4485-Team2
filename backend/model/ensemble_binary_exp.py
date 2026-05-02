# Ensemble binary classifiers experiments
# Evaluate the 3 model choices we chose

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Binary Test function
def binary_test(data):
    subject_data = data.groupby('Subject_ID').mean().reset_index()
    pairs = [
        ((0,1), "Healthy vs FTD"),
        ((0,2), "Healthy vs AD"),
        ((1,2), "AD vs FTD")
    ]

    for (i, j), name in pairs:
        pair_data = subject_data[subject_data['Group'].isin([i, j])].copy()
        features = pair_data.drop(columns=['Subject_ID', 'Group'])
        classes = (pair_data['Group'] == j).astype(int)

        model_1 = RandomForestClassifier(n_estimators=200, max_depth=10, class_weight='balanced')
        model_2 = SVC(kernel='rbf', probability=True, class_weight='balanced')
        model_3 = GradientBoostingClassifier(n_estimators=200, learning_rate=0.05)

        ensemble = VotingClassifier(
            estimators=[('rf', model_1), ('svm', model_2), ('gb', model_3)],
            voting='soft'    
        )

        skfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        metric_folds = {'acc': [], 'prec': [], 'rec': [], 'f1': []}

        for train_i, test_i in skfold.split(features, classes):
            X_train = features.iloc[train_i]
            X_test = features.iloc[test_i]
            Y_train = classes.iloc[train_i]
            Y_test = classes.iloc[test_i]

            imputer = SimpleImputer(strategy='mean')
            scaler = StandardScaler()

            X_train_clean = imputer.fit_transform(X_train)
            X_train_scale = scaler.fit_transform(X_train_clean)
            X_test_scale = scaler.transform(imputer.transform(X_test))

            ensemble.fit(X_train_scale, Y_train)
            Y_predict = ensemble.predict(X_test_scale)

            metric_folds['acc'].append(accuracy_score(Y_test, Y_predict))
            metric_folds['prec'].append(precision_score(Y_test, Y_predict, zero_division=0))
            metric_folds['rec'].append(recall_score(Y_test, Y_predict, zero_division=0))
            metric_folds['f1'].append(f1_score(Y_test, Y_predict))

        print(f"{name} Ensemble")
        print(f"Accuracy: {np.mean(metric_folds['acc']):.2%}")
        print(f"Precision: {np.mean(metric_folds['prec']):.2%}")
        print(f"Recall: {np.mean(metric_folds['rec']):.2%}")
        print(f"F1 Score: {np.mean(metric_folds['f1']):.2%}")

if __name__ == "__main__":
    data = pd.read_csv("Final_AD_Feature_Matrix.csv")
    mi_cols = [c for c in data.columns if "PHI_" in c or "Complexity" in c]
    data[mi_cols] = np.log1p(data[mi_cols].fillna(0))
    binary_test(data)
