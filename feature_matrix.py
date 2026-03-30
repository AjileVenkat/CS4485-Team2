import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_regression

def features_extraction(sample, id, md_row):
    # Compute PSD for all 19 channels with the Welch method
    sample_psd = sample.compute_psd(method='welch', fmin=1, fmax=30, verbose=False)
    sample_data, freqs = sample_psd.get_data(return_freqs=True)
    
    # Define power bands
    power_bands = {
        'Delta' : (freqs >= 1) & (freqs <= 4),
        'Theta' : (freqs >= 4) & (freqs <= 8),
        'Alpha' : (freqs >= 8) & (freqs <= 13),
        'Beta' : (freqs >= 13) & (freqs <= 30)
        }
    
    # Iterate through all electrodes and create a column name
    feature = {'Subject_ID': id}
    for i, channel in enumerate(sample.ch_names):
        total_channel_power = sample_data[i, :].sum()
        band_vals = {}
        for band, mask in power_bands.items():
            mean_power = sample_data[i, mask].mean()
            band_vals[band] = mean_power
            feature[f"{channel}_{band}_relative"] = mean_power / total_channel_power
        if band_vals['Alpha'] > 0:
            feature[f"{channel}_Theta_Alpha_Ratio"] = band_vals['Theta'] / band_vals['Alpha']
    
    connective_pairs = [('Fp1', 'Fp2'), ('Fp2', 'F4'), ('Fp2', 'F8'), ('Fp2', 'T4'), ('F3', 'F4'), 
                        ('T6', 'P4'), ('T4', 'P4'), ('T5', 'P3'), ('T4', 'T6'), ('T3', 'P3'), ('T3', 'T5'), ('O1', 'O2'), ('P3', 'P4')]
    
    
    
    for c1, c2 in connective_pairs:
        try:
            c1_data = sample.get_data(picks = c1)[0].reshape(-1, 1)
            c2_data = sample.get_data(picks = c2)[0]
            phi_value = mutual_info_regression(c1_data, c2_data, discrete_features=False, random_state=42)[0]
            feature[f"Corr_{c1}_{c2}"] = phi_value
        except ValueError:
            feature[f"Corr_{c1}_{c2}"] = 0
    
    if md_row is not None:
        feature['Age'] = md_row['Age']
        feature['Gender'] = 0 if md_row['Gender'] == 'M' else 1
    else:
        feature['Age'] = np.nan
        feature['Gender'] = np.nan
    return feature

if __name__ == "__main__":
    dir = "ds004504"
    rows = []
    md_df = pd.read_csv(os.path.join(dir, "participants.tsv"), sep='\t').set_index('participant_id')
    for i in sorted(os.listdir(dir)):
        if not i.startswith("sub-"):
            continue
        
        
        # Load .set files and create an entry per subject
        sub_num = int(i.split('-')[1])
        path = os.path.join(dir, i, 'eeg', f"{i}_task-eyesclosed_eeg.set")
        if os.path.exists(path):
            print(f"Extracting features for {i}...")
            raw_data = mne.io.read_raw_eeglab(path, preload=True, verbose=False)
            md_data = md_df.loc[i] if i in md_df.index else None
            sub_features = features_extraction(raw_data, i, md_data)

            # Group these entries into 3 groups
            if sub_num <= 36:
                sub_features['Group'] = 2
            elif 37 <= sub_num <= 65:
                sub_features['Group'] = 0
            else:
                sub_features['Group'] = 1
            
            rows.append(sub_features)
    
    # Create a csv file containing these separate band frequencies and groups
    feat_matrix = pd.DataFrame(rows)
    feat_matrix.to_csv("AD_Feature_Matrix.csv", index=False)
    print("Created feature matrix!")