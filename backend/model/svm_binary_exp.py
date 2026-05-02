# SVM binary classifier experiments
# Evaluate the 3 model choices we chose

import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Binary classifier test
def binary_test(data):
    subject_data = data.groupby('Subject_ID').mean().reset_index()

    pairs = [
        ((0, 2), "Healthy vs AD"),
        ((0, 1), "Healthy vs FTD"),
        ((1, 2), "AD vs FTD")
    ]

    params = {
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto'],
        'kernel': ['rbf', 'linear']
    }

    for (i, j), name in pairs:
        pair_data = subject_data[subject_data['Group'].isin([i, j])].copy()
        features = pair_data.drop(columns=['Subject_ID', 'Group'])
        classes = (pair_data['Group'] == j).astype(int)

        groupKF = GroupKFold(n_splits=5)

        accuracy_fold = []
        precision_fold = []
        recall_fold = []
        f1_fold = []

        for train_i, test_i in groupKF.split(features, classes, groups=pair_data['Subject_ID']):
            X_train = features.iloc[train_i]
            Y_train = classes.iloc[train_i]
            X_test = features.iloc[test_i]
            Y_test = classes.iloc[test_i]

            imputer = SimpleImputer(strategy='mean')
            scaler = StandardScaler()

            X_train_clean = imputer.fit_transform(X_train)
            X_train_scale = scaler.fit_transform(X_train_clean)
            X_test_scale = scaler.transform(imputer.transform(X_test))

            search = GridSearchCV(SVC(class_weight='balanced'), params, cv=3)
            search.fit(X_train_scale, Y_train)
            y_predict = search.predict(X_test_scale)

            accuracy_fold.append(accuracy_score(Y_test, y_predict))
            precision_fold.append(precision_score(Y_test, y_predict, zero_division=0))
            f1_fold.append(f1_score(Y_test, y_predict))
            recall_fold.append(recall_score(Y_test, y_predict, zero_division=0))

        print(f"{name} (SVM CV)")
        print(f"Accuracy: {np.mean(accuracy_fold):.2%}")
        print(f"Precision: {np.mean(precision_fold):.2%}")
        print(f"Recall: {np.mean(recall_fold):.2%}")
        print(f"F1 Score: {np.mean(f1_fold):.2%}")

if __name__ == "__main__":
    data = pd.read_csv("Final_AD_Feature_Matrix.csv")
    mi_cols = [c for c in data.columns if "PHI_" in c or "Complexity" in c]
    data[mi_cols] = np.log1p(data[mi_cols].fillna(0))

    binary_test(data)


