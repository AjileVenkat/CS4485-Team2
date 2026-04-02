import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_regression
from mne_connectivity import spectral_connectivity_epochs
from mne.time_frequency import psd_array_welch

def find_complexity(data):
    diff = np.diff(data)
    n = len(data)
    nz = np.sum(diff[:-1] * diff[1:] < 0)

    if nz == 0:
        return 0
    return np.log10(n) / (np.log10(n) + np.log10(n / (n + 0.4 * nz)))

def features_extraction(epoch_data, id, md_row, sfreq):
    rounded_data = np.round(epoch_data / 1e-5) * 1e-5

    feature = {'Subject_ID': id}

    psds, freqs = psd_array_welch(rounded_data, sfreq=sfreq, fmin = 1, fmax= 40, verbose=False)

    total_power = psds[:, (freqs >= 1) & (freqs <= 40)].sum(axis=1)
    theta_band = (freqs >= 4) & (freqs <= 8)
    alpha_band = (freqs >= 8) & (freqs <= 13)
    beta_band = (freqs >= 13) & (freqs <= 30)
    gamma_band = (freqs >= 30) & (freqs <= 45)

    ch_names = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'Fz', 'Cz', 'Pz']

    for ch_name in ['Fp1', 'Fp2', 'F3', 'F4', 'T3', 'T4', 'P3', 'P4']:
        ch_i = ch_names.index(ch_name)
        feature[f'Theta_{ch_name}'] = psds[ch_i, theta_band].sum() / total_power[ch_i]
        feature[f'Alpha_{ch_name}'] = psds[ch_i, alpha_band].sum() / total_power[ch_i]
        feature[f'Beta_{ch_name}'] = psds[ch_i, beta_band].sum() / total_power[ch_i]
        feature[f'Gamma_{ch_name}'] = psds[ch_i, gamma_band].sum() / total_power[ch_i]
        feature[f'Complexity_{ch_name}'] = find_complexity(rounded_data[ch_i])

    connective_pairs = [('Fp1', 'Fp2'), ('Fp2', 'F4'), ('F3', 'F4'), ('Fp2', 'F8'), 
                        ('Fp2', 'T4'), ('F7', 'F8'), ('T5', 'P3'), ('T3', 'P3'), 
                        ('O1', 'O2'), ('T3', 'T5'), ('T4', 'T6'), ('T4', 'P4'), ('T6', 'P4')]
    

    for i, (c1, c2) in enumerate(connective_pairs):
        try:
            c1_index = ch_names.index(c1)
            c2_index = ch_names.index(c2)

            c1_data = rounded_data[c1_index].reshape(-1, 1)
            c2_data = rounded_data[c2_index]
            phi_value = mutual_info_regression(c1_data, c2_data, discrete_features=False, random_state=42)[0]
            feature[f"PHI_{c1}_{c2}"] = phi_value
        except:
            feature[f"PHI_{c1}_{c2}"] = 0
    
    if md_row is not None:
        feature['Age'] = md_row['Age']
        feature['Gender'] = 0 if md_row['Gender'] == 'M' else 1
    else:
        feature['Age'] = 63
        feature['Gender'] = 0
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
            print(f"Epoching {i}...")
            print(f"Extracting features for {i}...")
            raw_data = mne.io.read_raw_eeglab(path, preload=True, verbose=False)
            
            raw_data.set_eeg_reference(ref_channels='average', verbose=False)

            raw_data.filter(l_freq=0.5, h_freq=45, method='iir', iir_params=dict(order=2, ftype='butter'), phase='zero', verbose=False)

            raw_data.resample(128, verbose=False)
            md_data = md_df.loc[i] if i in md_df.index else None

            duration = 60
            step = 4

            for start in range(0, duration - step + 1, step):
                stop = start + step
                raw_data_epoch = raw_data.copy().crop(tmin=start, tmax=stop - 1/128, verbose=False)
                data_epoch = raw_data_epoch.get_data()

                sub_features = features_extraction(data_epoch, i, md_data, 128)

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