import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, cross_val_predict
from sklearn.ensemble import RandomForestClassifier

data = pd.read_csv("AD_Feature_Matrix.csv")
mi_columns = [c for c in data.columns if "PHI_" in c]
data[mi_columns] = np.log1p(data[mi_columns])

X = data.drop(columns = ['Subject_ID', 'Group']).dropna()
y = data.loc[X.index, 'Group']

pipeline_rf = Pipeline([
    ('scaler', StandardScaler()),
    ('rf', RandomForestClassifier(random_state=42, class_weight="balanced"))
])
parameters_rf = {
    'rf__n_estimators': [100, 200],
    'rf__max_depth': [None, 10],
    'rf__min_samples_split': [2, 5]
}
skfold = StratifiedKFold(n_splits=5, shuffle = True, random_state=42)
search_rf = GridSearchCV(pipeline_rf, param_grid=parameters_rf, cv=skfold, scoring='accuracy')
search_rf.fit(X,y)

cv_results_rf = cross_validate(search_rf.best_estimator_, X, y, cv=skfold, scoring = ['accuracy', 'f1_macro'])

print("3-Class Random Forest Metrics:")
print(f"Overall Accuracy: {cv_results_rf['test_accuracy'].mean():.2%}")
print(f"F1 (Macro): {cv_results_rf['test_f1_macro'].mean():.2%}")
y_pred = cross_val_predict(search_rf.best_estimator_, X, y, cv=skfold)
cm = confusion_matrix(y, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Healthy', 'FTD', 'AD'])
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()