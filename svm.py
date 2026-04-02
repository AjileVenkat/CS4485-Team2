import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.decomposition import PCA
from sklearn.base import BaseEstimator, ClassifierMixin

class HierarchicalDementiaClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, C=1.0, gamma='scale', n_components=0.90):
        self.C = C
        self.gamma = gamma
        self.n_components = n_components
        
        # GATE 1: Healthy vs. All Dementia (Broad Net)
        self.gate1 = ImbPipeline([
            ('scaler', StandardScaler()),
            ('pca', PCA(n_components=self.n_components)),
            ('smote', SMOTE(random_state=42)),
            ('svm', SVC(C=self.C, kernel='rbf', gamma=self.gamma, class_weight='balanced'))
        ])
        
        # GATE 2: AD vs. FTD (The Specialist)
        self.gate2 = ImbPipeline([
            ('scaler', StandardScaler()),
            ('pca', PCA(n_components=self.n_components)),
            ('smote', SMOTE(random_state=42)),
            ('svm', SVC(C=self.C, kernel='rbf', gamma=self.gamma, class_weight='balanced'))
        ])

    def fit(self, X, y):
        # Training Gate 1: 0 is Healthy, 1 is Dementia (AD/FTD combined)
        y_binary = (y != 0).astype(int)
        self.gate1.fit(X, y_binary)
        
        # Training Gate 2: Only on Dementia subjects
        mask = (y != 0)
        self.gate2.fit(X[mask], y[mask])
        return self

    def predict(self, X):
        # Step 1: Is it dementia?
        is_dementia = self.gate1.predict(X)
        final_preds = np.zeros(len(X))
        
        for i in range(len(X)):
            if is_dementia[i] == 0:
                final_preds[i] = 0 # Classified as Healthy
            else:
                # Step 2: Which type?
                row = X.iloc[[i]]
                final_preds[i] = self.gate2.predict(row)[0]
        return final_preds

def run_final_test(df):
    X = df.drop(columns=['Subject_ID', 'Group'])
    y = df['Group']
    groups = df['Subject_ID']

    # Using the optimized parameters from your previous grid search
    model = HierarchicalDementiaClassifier(C=0.1, gamma=0.01, n_components=0.90)
    
    gkf = GroupKFold(n_splits=5)
    
    print("Executing Hierarchical Classification with Group-Wise splits...")
    y_pred = cross_val_predict(model, X, y, cv=gkf, groups=groups)

    print("\n--- Final Results (Filtered + Hierarchical) ---")
    print(classification_report(y, y_pred, target_names=['Healthy', 'FTD', 'AD']))
    print("Confusion Matrix:")
    print(confusion_matrix(y, y_pred))
    # Create a summary dataframe
    results_df = pd.DataFrame({'Subject_ID': groups, 'Actual': y, 'Predicted': y_pred})

# Group by Subject and take the most frequent prediction (Majority Vote)
    subject_results = results_df.groupby('Subject_ID').agg(lambda x: x.value_counts().index[0])

    print("\n--- SUBJECT-LEVEL RESULTS (Majority Vote) ---")
    print(classification_report(subject_results['Actual'], subject_results['Predicted'], 
                            target_names=['Healthy', 'FTD', 'AD']))

if __name__ == "__main__":
    data = pd.read_csv("AD_Feature_Matrix.csv")
    run_final_test(data)

    