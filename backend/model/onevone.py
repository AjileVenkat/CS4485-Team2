import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.multiclass import OneVsOneClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# 1. Load the "Final" Matrix
df = pd.read_csv("AD_Feature_Matrix.csv").dropna()
X = df.drop(columns=['Subject_ID', 'Group'])
y = df['Group'] # 0: Healthy, 1: FTD, 2: AD

# 2. Train/Test Split (Stratified to keep group balances equal)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 3. The Ultimate SVM Pipeline
# We use a 'linear' or 'poly' kernel sometimes if RBF overfits, 
# but for 15 features, RBF is usually the king.
ultimate_pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('ovo_svm', OneVsOneClassifier(SVC(kernel='rbf', C=10, class_weight='balanced')))
])

# 4. Fit and Predict
ultimate_pipe.fit(X_train, y_train)
y_pred = ultimate_pipe.predict(X_test)

# 5. The Moment of Truth
print("--- Ultimate 3-Class OvO Results ---")
print(f"Total Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print("\nDetailed Breakdown:")
print(classification_report(y_test, y_pred, target_names=['Healthy', 'FTD', 'AD']))