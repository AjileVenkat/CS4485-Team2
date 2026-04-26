"""
EEG Alzheimer's Disease Detection Backend
Flask REST API — EEG processing + Optimized ML classifier
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import numpy as np
import mne
import traceback

app = Flask(__name__)
CORS(app)
mne.set_log_level('WARNING')

SUBJECT_GROUPS = {
    'sub-001': 'AD', 'sub-002': 'AD', 'sub-003': 'AD', 'sub-004': 'AD',
    'sub-005': 'AD', 'sub-006': 'AD', 'sub-007': 'AD', 'sub-008': 'AD',
    'sub-009': 'AD', 'sub-010': 'AD', 'sub-011': 'AD', 'sub-012': 'AD',
    'sub-013': 'AD', 'sub-014': 'AD', 'sub-015': 'AD', 'sub-016': 'AD',
    'sub-017': 'AD', 'sub-018': 'AD', 'sub-019': 'AD', 'sub-020': 'AD',
    'sub-021': 'AD', 'sub-022': 'AD', 'sub-023': 'AD', 'sub-024': 'AD',
    'sub-025': 'AD', 'sub-026': 'AD', 'sub-027': 'AD', 'sub-028': 'AD',
    'sub-029': 'AD', 'sub-030': 'AD', 'sub-031': 'AD', 'sub-032': 'AD',
    'sub-033': 'AD', 'sub-034': 'AD', 'sub-035': 'AD', 'sub-036': 'AD',
    'sub-037': 'CN', 'sub-038': 'CN', 'sub-039': 'CN', 'sub-040': 'CN',
    'sub-041': 'CN', 'sub-042': 'CN', 'sub-043': 'CN', 'sub-044': 'CN',
    'sub-045': 'CN', 'sub-046': 'CN', 'sub-047': 'CN', 'sub-048': 'CN',
    'sub-049': 'CN', 'sub-050': 'CN', 'sub-051': 'CN', 'sub-052': 'CN',
    'sub-053': 'CN', 'sub-054': 'CN', 'sub-055': 'CN', 'sub-056': 'CN',
    'sub-057': 'CN', 'sub-058': 'CN', 'sub-059': 'CN', 'sub-060': 'CN',
    'sub-061': 'CN', 'sub-062': 'CN', 'sub-063': 'CN', 'sub-064': 'CN',
    'sub-065': 'CN', 'sub-066': 'FTD', 'sub-067': 'FTD', 'sub-068': 'FTD',
    'sub-069': 'FTD', 'sub-070': 'FTD', 'sub-071': 'FTD', 'sub-072': 'FTD',
    'sub-073': 'FTD', 'sub-074': 'FTD', 'sub-075': 'FTD', 'sub-076': 'FTD',
    'sub-077': 'FTD', 'sub-078': 'FTD', 'sub-079': 'FTD', 'sub-080': 'FTD',
    'sub-081': 'FTD', 'sub-082': 'FTD', 'sub-083': 'FTD', 'sub-084': 'FTD',
    'sub-085': 'FTD', 'sub-086': 'FTD', 'sub-087': 'FTD', 'sub-088': 'FTD',
}

CHANNEL_REGIONS = {
    'frontal':   ['Fp1','Fp2','F7','F3','Fz','F4','F8'],
    'temporal':  ['T3','T4','T5','T6'],
    'central':   ['C3','Cz','C4'],
    'parietal':  ['P3','Pz','P4'],
    'occipital': ['O1','O2'],
}

DATASET_ROOT = os.environ.get("DATASET_ROOT", "ds004504")
_model_cache = None
_model_results_cache = None

# ── EEG helpers ──────────────────────────────────────────────────────────────

def find_eeg_file(subject_id, preprocessed=True):
    fname = f"{subject_id}_task-eyesclosed_eeg.set"
    if preprocessed:
        p = os.path.join(DATASET_ROOT, "derivatives", subject_id, "eeg", fname)
        if os.path.exists(p): return p
    p = os.path.join(DATASET_ROOT, subject_id, "eeg", fname)
    return p if os.path.exists(p) else None

def load_raw(subject_id, preprocessed=True):
    path = find_eeg_file(subject_id, preprocessed)
    if not path:
        raise FileNotFoundError(f"Subject {subject_id} not found. DATASET_ROOT={DATASET_ROOT}")
    raw = mne.io.read_raw_eeglab(path, preload=True, verbose=False)
    raw.filter(1.0, 40.0, verbose=False)
    return raw

def compute_band_powers(raw):
    psd = raw.compute_psd(method='welch', fmin=1, fmax=40, verbose=False)
    data, freqs = psd.get_data(return_freqs=True)
    bands = {
        'delta':  (freqs >= 1)    & (freqs <= 4),
        'theta':  (freqs >= 4)    & (freqs <= 8),
        'alpha':  (freqs >= 8)    & (freqs <= 13),
        'alpha2': (freqs >= 8)    & (freqs <= 10.5),
        'alpha3': (freqs >= 10.5) & (freqs <= 13),
        'beta':   (freqs >= 13)   & (freqs <= 30),
    }
    per_channel = {ch: {b: float(data[i, m].mean()) for b, m in bands.items()}
                   for i, ch in enumerate(raw.ch_names)}
    averages = {b: float(data[:, m].mean()) for b, m in bands.items()}
    return {'per_channel': per_channel, 'averages': averages}

def compute_risk_scores(averages):
    d, t, a = averages['delta'], averages['theta'], averages['alpha']
    a2, a3, b = averages['alpha2'], averages['alpha3'], averages['beta']
    theta_alpha = t / a   if a  > 0 else 0
    delta_alpha = d / a   if a  > 0 else 0
    brain_score = (d + t) / (a + b) if (a + b) > 0 else 0
    alpha32     = a3 / a2 if a2 > 0 else 0
    if   theta_alpha < 0.8: level, pct = "low",      20
    elif theta_alpha < 1.5: level, pct = "moderate",  45
    elif theta_alpha < 2.5: level, pct = "elevated",  70
    else:                   level, pct = "high",       90
    return {
        'theta_alpha_ratio':     round(theta_alpha, 4),
        'delta_alpha_ratio':     round(delta_alpha, 4),
        'brain_cognitive_score': round(brain_score, 4),
        'alpha3_alpha2_ratio':   round(alpha32, 4),
        'risk_level':   level,
        'risk_percent': pct,
    }

def regional_averages(per_channel):
    return {
        region: {band: float(np.mean([per_channel[ch][band]
                 for ch in channels if ch in per_channel]))
                 for band in ['delta','theta','alpha','beta']}
        for region, channels in CHANNEL_REGIONS.items()
        if any(ch in per_channel for ch in channels)
    }

# ── Feature engineering ──────────────────────────────────────────────────────

def extract_features(averages, per_channel):
    d  = averages['delta']
    t  = averages['theta']
    a  = averages['alpha']
    a2 = averages['alpha2']
    a3 = averages['alpha3']
    b  = averages['beta']
    total = d + t + a + b + 1e-30

    features = [
        d, t, a, a2, a3, b,
        t/(a+1e-30), d/(a+1e-30), (d+t)/(a+b+1e-30),
        a3/(a2+1e-30), b/(a+1e-30), t/(b+1e-30),
        (d+t+b)/(a+1e-30),
        d/total, t/total, a/total, b/total,
    ]

    for region, channels in CHANNEL_REGIONS.items():
        present = [ch for ch in channels if ch in per_channel]
        if present:
            for band in ['delta','theta','alpha','beta']:
                features.append(np.mean([per_channel[ch][band] for ch in present]))
        else:
            features.extend([0,0,0,0])

    for region, channels in CHANNEL_REGIONS.items():
        present = [ch for ch in channels if ch in per_channel]
        if present:
            rt = np.mean([per_channel[ch]['theta'] for ch in present])
            ra = np.mean([per_channel[ch]['alpha'] for ch in present])
            features.append(rt/(ra+1e-30))
        else:
            features.append(0)

    pairs = [('F3','F4'),('C3','C4'),('P3','P4'),('O1','O2'),('T3','T4')]
    for l, r in pairs:
        if l in per_channel and r in per_channel:
            for band in ['alpha','theta']:
                lv, rv = per_channel[l][band], per_channel[r][band]
                features.append((lv-rv)/(lv+rv+1e-30))
        else:
            features.extend([0,0])

    key_channels = ['P3','P4','Pz','O1','O2','F3','F4','Fz','C3','C4']
    for ch in key_channels:
        if ch in per_channel:
            p = per_channel[ch]
            features.append(p['theta']/(p['alpha']+1e-30))
            features.append(p['delta']/(p['alpha']+1e-30))
            features.append(p['alpha3']/(p['alpha2']+1e-30))
        else:
            features.extend([0,0,0])

    return np.array(features, dtype=np.float64)


# ── ML Training with LOOCV + SMOTE ───────────────────────────────────────────

def train_model():
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import LeaveOneOut, StratifiedKFold, cross_val_predict
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, balanced_accuracy_score
    from sklearn.svm import SVC
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.neural_network import MLPClassifier

    print("Loading all subjects...")
    X, y, subject_ids = [], [], []

    for sid, grp in SUBJECT_GROUPS.items():
        try:
            raw  = load_raw(sid)
            bp   = compute_band_powers(raw)
            feat = extract_features(bp['averages'], bp['per_channel'])
            X.append(feat)
            y.append(grp)
            subject_ids.append(sid)
            print(f"  Loaded {sid} ({grp})")
        except Exception as e:
            print(f"  Skipped {sid}: {e}")

    X = np.array(X)
    y = np.array(y)
    classes = sorted(set(y))

    le = LabelEncoder()
    le.fit(classes)
    y_enc = le.transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── LOOCV: maximizes training data with 88 subjects ──────────────────
    loo = LeaveOneOut()
    y_pred_all = np.zeros(len(y), dtype=int)

    for i, (train_idx, test_idx) in enumerate(loo.split(X_scaled)):
        X_tr, X_te = X_scaled[train_idx], X_scaled[test_idx]
        y_tr = y_enc[train_idx]

        # SMOTE-like: augment minority class with small noise
        # Count classes in training
        from collections import Counter
        counts = Counter(y_tr)
        max_count = max(counts.values())
        X_aug_list = [X_tr]
        y_aug_list = [y_tr]
        for cls_idx in range(len(classes)):
            cls_samples = X_tr[y_tr == cls_idx]
            n_needed = max_count - len(cls_samples)
            if n_needed > 0 and len(cls_samples) > 0:
                idxs = np.random.choice(len(cls_samples), n_needed, replace=True)
                noise = np.random.normal(0, 0.05, cls_samples[idxs].shape)
                X_aug_list.append(cls_samples[idxs] + noise * np.std(X_tr, axis=0))
                y_aug_list.append(np.full(n_needed, cls_idx))

        X_bal = np.vstack(X_aug_list)
        y_bal = np.concatenate(y_aug_list)

        # SVM — best for small datasets
        svm = SVC(kernel='rbf', C=100, gamma='scale',
                  class_weight='balanced', probability=True, random_state=42)
        svm.fit(X_bal, y_bal)
        svm_pred = svm.predict(X_te)[0]

        # RF
        rf = RandomForestClassifier(n_estimators=300, max_features='sqrt',
                                     class_weight='balanced', random_state=42, n_jobs=-1)
        rf.fit(X_bal, y_bal)
        rf_pred = rf.predict(X_te)[0]

        # GB
        gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1,
                                         max_depth=3, random_state=42)
        gb.fit(X_bal, y_bal)
        gb_pred = gb.predict(X_te)[0]

        # Weighted majority vote: SVM has highest weight for small datasets
        votes = np.zeros(len(classes))
        votes[svm_pred] += 2   # SVM weight = 2
        votes[rf_pred]  += 1
        votes[gb_pred]  += 1
        y_pred_all[test_idx[0]] = np.argmax(votes)

        if i % 10 == 0:
            print(f"  LOOCV {i+1}/{len(X)}")

    y_pred_labels = le.inverse_transform(y_pred_all)

    acc     = accuracy_score(y, y_pred_labels)
    bal_acc = balanced_accuracy_score(y, y_pred_labels)
    report  = classification_report(y, y_pred_labels, output_dict=True)
    cm      = confusion_matrix(y, y_pred_labels, labels=classes).tolist()

    per_subject = [
        {'subject_id': sid, 'true': tl, 'predicted': pl, 'correct': tl == pl}
        for sid, tl, pl in zip(subject_ids, y, y_pred_labels)
    ]

    # ── Train final models on ALL data ───────────────────────────────────
    # Balance all classes
    from collections import Counter
    counts = Counter(y_enc)
    max_count = max(counts.values())
    X_aug_list = [X_scaled]
    y_aug_list = [y_enc]
    for cls_idx in range(len(classes)):
        cls_samples = X_scaled[y_enc == cls_idx]
        n_needed = max_count - len(cls_samples)
        if n_needed > 0 and len(cls_samples) > 0:
            idxs = np.random.choice(len(cls_samples), n_needed, replace=True)
            noise = np.random.normal(0, 0.05, cls_samples[idxs].shape)
            X_aug_list.append(cls_samples[idxs] + noise * np.std(X_scaled, axis=0))
            y_aug_list.append(np.full(n_needed, cls_idx))

    X_final = np.vstack(X_aug_list)
    y_final = np.concatenate(y_aug_list)

    final_svm = SVC(kernel='rbf', C=100, gamma='scale',
                    class_weight='balanced', probability=True, random_state=42)
    final_svm.fit(X_final, y_final)

    final_rf = RandomForestClassifier(n_estimators=500, max_features='sqrt',
                                       class_weight='balanced', random_state=42, n_jobs=-1)
    final_rf.fit(X_final, y_final)

    final_gb = GradientBoostingClassifier(n_estimators=200, learning_rate=0.05,
                                           max_depth=4, random_state=42)
    final_gb.fit(X_final, y_final)

    importances = final_rf.feature_importances_
    feat_names = (
        ['delta','theta','alpha','alpha2','alpha3','beta',
         'theta_alpha','delta_alpha','brain_score','alpha3_alpha2',
         'beta_alpha','theta_beta','slow_fast','rel_delta','rel_theta','rel_alpha','rel_beta'] +
        [f'{r}_{b}' for r in CHANNEL_REGIONS for b in ['delta','theta','alpha','beta']] +
        [f'{r}_thetaalpha' for r in CHANNEL_REGIONS] +
        [f'asym_{l}{r}_{b}' for l,r in [('F3','F4'),('C3','C4'),('P3','P4'),('O1','O2'),('T3','T4')] for b in ['alpha','theta']] +
        [f'{ch}_{m}' for ch in ['P3','P4','Pz','O1','O2','F3','F4','Fz','C3','C4'] for m in ['ta','da','a32']]
    )
    feat_importance = sorted(
        [{'feature': n, 'importance': round(float(v), 4)}
         for n, v in zip(feat_names[:len(importances)], importances)],
        key=lambda x: x['importance'], reverse=True
    )[:15]

    results = {
        'accuracy':              round(acc, 4),
        'balanced_accuracy':     round(bal_acc, 4),
        'n_subjects':            len(X),
        'classes':               classes,
        'confusion_matrix':      cm,
        'classification_report': report,
        'feature_importances':   feat_importance,
        'per_subject':           per_subject,
        'cv_folds':              len(X),  # LOOCV
        'model_type':            'SVM + RF + GB Ensemble with LOOCV & Class Balancing',
    }

    return (final_svm, final_rf, final_gb, scaler, le), results


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'dataset_root': DATASET_ROOT})

@app.route('/api/subjects')
def list_subjects():
    return jsonify([
        {'id': sid, 'group': grp, 'available': find_eeg_file(sid) is not None}
        for sid, grp in SUBJECT_GROUPS.items()
    ])

@app.route('/api/analyze/<subject_id>')
def analyze_subject(subject_id):
    try:
        preprocessed = request.args.get('preprocessed', 'true').lower() == 'true'
        raw     = load_raw(subject_id, preprocessed)
        bp      = compute_band_powers(raw)
        scores  = compute_risk_scores(bp['averages'])
        regions = regional_averages(bp['per_channel'])

        ml_prediction = None
        if _model_cache is not None:
            svm, rf, gb, scaler, le = _model_cache
            feat = extract_features(bp['averages'], bp['per_channel']).reshape(1, -1)
            feat_s = scaler.transform(feat)
            from collections import Counter
            votes = np.zeros(len(le.classes_))
            votes[svm.predict(feat_s)[0]] += 2
            votes[rf.predict(feat_s)[0]]  += 1
            votes[gb.predict(feat_s)[0]]  += 1
            pred_label = le.inverse_transform([int(np.argmax(votes))])[0]
            proba = rf.predict_proba(feat_s)[0]
            ml_prediction = {
                'predicted_group': pred_label,
                'probabilities': {cls: round(float(p), 3)
                                  for cls, p in zip(le.classes_, proba)},
                'correct': pred_label == SUBJECT_GROUPS.get(subject_id, ''),
            }

        return jsonify({
            'subject_id':       subject_id,
            'group':            SUBJECT_GROUPS.get(subject_id, 'Unknown'),
            'duration_seconds': round(raw.times[-1], 1),
            'sampling_rate_hz': raw.info['sfreq'],
            'n_channels':       len(raw.ch_names),
            'channels':         raw.ch_names,
            'band_powers':      bp,
            'risk_scores':      scores,
            'regional_powers':  regions,
            'ml_prediction':    ml_prediction,
        })
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/compare', methods=['POST'])
def compare_subjects():
    sids = request.get_json().get('subjects', [])
    if len(sids) < 2:
        return jsonify({'error': 'Need at least 2 subjects'}), 400
    results = []
    for sid in sids[:6]:
        try:
            raw = load_raw(sid)
            bp  = compute_band_powers(raw)
            results.append({'subject_id': sid, 'group': SUBJECT_GROUPS.get(sid,'Unknown'),
                             'band_powers': bp['averages'],
                             'risk_scores': compute_risk_scores(bp['averages'])})
        except Exception as e:
            results.append({'subject_id': sid, 'error': str(e)})
    return jsonify({'comparisons': results})

@app.route('/api/batch', methods=['POST'])
def batch_analyze():
    body    = request.get_json()
    gfilter = body.get('group', 'all').upper()
    maxn    = body.get('max_subjects', 10)
    targets = [(s, g) for s, g in SUBJECT_GROUPS.items()
               if gfilter == 'ALL' or g == gfilter][:maxn]
    results = []
    for sid, grp in targets:
        try:
            raw = load_raw(sid)
            bp  = compute_band_powers(raw)
            sc  = compute_risk_scores(bp['averages'])
            results.append({'subject_id': sid, 'group': grp, **bp['averages'], **sc})
        except Exception:
            continue
    if not results:
        return jsonify({'error': 'No subjects loaded'}), 404
    import pandas as pd
    df  = pd.DataFrame(results)
    num = [c for c in ['delta','theta','alpha','beta','theta_alpha_ratio',
                        'delta_alpha_ratio','brain_cognitive_score','alpha3_alpha2_ratio']
           if c in df.columns]
    agg = df[['group']+num].groupby('group').agg(['mean','std']).round(4)
    agg.columns = ['_'.join(c) for c in agg.columns]
    return jsonify({'group': gfilter, 'n_subjects': len(results),
                    'subjects': results, 'aggregates': agg.to_dict(orient='index')})

@app.route('/api/waveform/<subject_id>')
def get_waveform(subject_id):
    ch    = request.args.get('channel', 'P3')
    start = float(request.args.get('start', 10))
    stop  = float(request.args.get('stop',  20))
    try:
        raw   = load_raw(subject_id)
        sfreq = raw.info['sfreq']
        data, times = raw.get_data(picks=ch, start=int(start*sfreq),
                                   stop=int(stop*sfreq), return_times=True)
        step = max(1, len(times)//2000)
        return jsonify({'subject_id': subject_id, 'channel': ch,
                        'times': times[::step].tolist(),
                        'amplitudes': (data[0][::step]*1e6).tolist(), 'unit': 'µV'})
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/train', methods=['POST'])
def ml_train():
    global _model_cache, _model_results_cache
    try:
        model_tuple, results = train_model()
        _model_cache = model_tuple
        _model_results_cache = results
        return jsonify({'status': 'trained', **results})
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/ml/results')
def ml_results():
    if _model_results_cache is None:
        return jsonify({'error': 'Model not trained yet'}), 404
    return jsonify(_model_results_cache)

@app.route('/api/ml/predict/<subject_id>')
def ml_predict(subject_id):
    if _model_cache is None:
        return jsonify({'error': 'Model not trained yet'}), 404
    try:
        raw  = load_raw(subject_id)
        bp   = compute_band_powers(raw)
        feat = extract_features(bp['averages'], bp['per_channel']).reshape(1, -1)
        svm, rf, gb, scaler, le = _model_cache
        feat_s = scaler.transform(feat)
        votes = np.zeros(len(le.classes_))
        votes[svm.predict(feat_s)[0]] += 2
        votes[rf.predict(feat_s)[0]]  += 1
        votes[gb.predict(feat_s)[0]]  += 1
        pred_label = le.inverse_transform([int(np.argmax(votes))])[0]
        proba = rf.predict_proba(feat_s)[0]
        true_label = SUBJECT_GROUPS.get(subject_id, 'Unknown')
        return jsonify({
            'subject_id':      subject_id,
            'true_group':      true_label,
            'predicted_group': pred_label,
            'correct':         pred_label == true_label,
            'probabilities':   {cls: round(float(p), 3)
                                for cls, p in zip(le.classes_, proba)},
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)