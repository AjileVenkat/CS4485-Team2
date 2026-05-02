from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.model_selection import LeaveOneOut, GridSearchCV
from sklearn.preprocessing import PowerTransformer

# 1. Setup our "Council of Experts"
clf1 = SVC(kernel='linear', C=1, probability=True, class_weight='balanced')
clf2 = RandomForestClassifier(n_estimators=100, max_depth=5, class_weight='balanced')
clf3 = GradientBoostingClassifier(n_estimators=50, learning_rate=0.1, max_depth=3)

# 2. Create the Voting Ensemble
ensemble = VotingClassifier(
    estimators=[('svm', clf1), ('rf', clf2), ('gb', clf3)],
    voting='soft' # 'soft' uses weighted probabilities for better accuracy
)

# 3. The Loop (Same as before, just swapping the model)
all_preds = []
all_true = []

for train_idx, test_idx in loo.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    # Scale (Crucial for SVM, though RF doesn't strictly need it)
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    # Train the Ensemble
    ensemble.fit(X_train_s, y_train)
    
    all_preds.append(ensemble.predict(X_test_s)[0])
    all_true.append(y_test.values[0])

print(f"Ensemble Accuracy: {accuracy_score(all_true, all_preds):.2%}")