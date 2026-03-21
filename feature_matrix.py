import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

def features_extraction(sample, id):
    # Compute PSD for all 19 channels with the Welch method
    sample_psd = sample.compute_psd(method='welch', fmin=1, fmax=30, verbose=False)
    sample_data, freqs = sample_psd.get_data(return_freqs=True)
    
    power_bands = {
        'Delta' : (freqs >= 1) & (freqs <= 4),
        'Theta' : (freqs >= 4) & (freqs <= 8),
        'Alpha' : (freqs >= 8) & (freqs <= 13),
        'Beta' : (freqs >= 13) & (freqs <= 30)
        }
        
    feature = {'Subject_ID': id}
    for i, channel in enumerate(sample.ch_names):
        for band, mask in power_bands.items():
            col = f"{channel}_{band}"
            feature[col] = sample_data[i, mask].mean()
    
    return feature

if __name__ == "__main__":
    dir = "ds004504"
    rows = []
    for i in sorted(os.listdir(dir)):
        if not i.startswith("sub-"):
            continue
        
        sub_num = int(i.split('-')[1])
        path = os.path.join(dir, i, 'eeg', f"{i}_task-eyesclosed_eeg.set")
        if os.path.exists(path):
            print(f"Extracting features for {i}...")
            raw_data = mne.io.read_raw_eeglab(path, preload=True, verbose=False)

            sub_features = features_extraction(raw_data, i)

            if sub_num <= 36:
                sub_features['Group'] = 2
            elif 37 <= sub_num <= 65:
                sub_features['Group'] = 0
            else:
                sub_features['Group'] = 1
            
            rows.append(sub_features)
    
    feat_matrix = pd.DataFrame(rows)
    feat_matrix.to_csv("AD_Feature_Matrix.csv", index=False)
    print("Created feature matrix!")