# Feature extraction code ( Team 2 EEG Dementia Project )
# Import libraries
import os
import pandas as pd
import numpy as np
import mne
from sklearn.feature_selection import mutual_info_regression
from mne.time_frequency import psd_array_welch

# Petrosian Fractal Dimension (PFD) to condense EEG signals
def calc_complexity(data):
    # Find first derivatives
    diff = np.diff(data)
    num = len(data)

    # Count sign changes in derivative
    num_zeros = np.sum(diff[:-1] * diff[1:] < 0)
    if num_zeros == 0:
        return 0
    
    # Return PFD
    return np.log10(num) / (np.log10(num) + np.log10(num / (num + 0.4 * num_zeros)))

# Feature extraction function with epoch data
# Attempt at preprocessing the data even further, hoping to improve performance metrics
def feature_extraction(e_data, id, md_row, sfreq):
    # Rounding data to reduce micro noise
    rounded = np.round(e_data / 1e-5) * 1e-5
    feats = {'Subject_ID': id}

    # Convert data to power spectral density (PSD)
    psds, freqs = psd_array_welch(rounded, sfreq = sfreq, fmin = 1, fmax = 40, verbose = False)
    
    # Variables to find relative power per band
    total_powers = psds[:, (freqs >= 1) & (freqs <= 40)].sum(axis=1)
    theta = (freqs >= 4) & (freqs <= 8)
    alpha = (freqs >= 8) & (freqs <= 13)
    beta = (freqs >= 13) & (freqs <= 30)
    gamma = (freqs >= 30) & (freqs <= 45)

    # All 19 channels in a list
    channels = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 
                'P3', 'P4', 'O1', 'O2', 'F7', 'F8',
                'T3', 'T4', 'T5', 'T6', 'Fz', 'Cz', 'Pz']
    
    # Channel pairs for mutual info between 2 brain regions
    connective_pairs = [('Fp1', 'Fp2'), ('Fp2', 'F4'), ('F3', 'F4'), ('Fp2', 'F8'), 
                        ('Fp2', 'T4'), ('F7', 'F8'), ('T5', 'P3'), ('T3', 'P3'), 
                        ('O1', 'O2'), ('T3', 'T5'), ('T4', 'T6'), ('T4', 'P4'), ('T6', 'P4')]
    
    # Focus on finding relative power for every band in each important channel (FTD vs AD focused)
    for channel in ['Fp1', 'Fp2', 'F3', 'F4', 'T3', 'T4', 'P3', 'P4']:
        ind = channels.index(channel)
        denom = total_powers[ind]
        if np.isfinite(denom) and abs(denom) > 1e-12:
            inv_denom = 1.0 / denom
        else:
            inv_denom = 0.0
        feats[f'Theta_{channel}'] = psds[ind, theta].sum() * inv_denom
        feats[f'Alpha_{channel}'] = psds[ind, alpha].sum() * inv_denom
        feats[f'Beta_{channel}'] = psds[ind, beta].sum() * inv_denom
        feats[f'Gamma_{channel}'] = psds[ind, gamma].sum() * inv_denom
        feats[f'Complexity_{channel}'] = calc_complexity(rounded[ind])
 
    # For each pair, find the mutual info to capture non linear relationships
    for i, (c1, c2) in enumerate(connective_pairs):
        try:
            c1_ind = channels.index(c1)
            c2_ind = channels.index(c2)
            c1_data = rounded[c1_ind].reshape(-1, 1)
            c2_data = rounded[c2_ind]
            phi_val = mutual_info_regression(c1_data, c2_data, discrete_features=False, random_state = 42)[0]
            feats[f"PHI_{c1}_{c2}"] = phi_val
        except:
            feats[f"PHI_{c1}_{c2}"] = 0

    # Include gender and age in feature (this might help)
    if md_row is not None:
        feats['Age'] = md_row['Age']
        if md_row['Gender'] == 'M':
            feats['Gender'] = 0
        else:
            feats['Gender'] = 1
    else:
        feats['Age'] = 63
        feats['Gender'] = 0
    return feats

# Backwards compatibility for older imports.
features_extraction = feature_extraction

if __name__ == "__main__":
    # Define paths for the used data and participants.tsv
    candidate_dirs = [
        "ds004504_annex",
        "ds004504",
        os.path.join(os.path.dirname(__file__), "..", "ds004504_annex"),
        os.path.join(os.path.dirname(__file__), "..", "ds004504"),
    ]

    root_dir = None
    for candidate in candidate_dirs:
        derivatives_candidate = os.path.join(candidate, "derivatives")
        participants_candidate = os.path.join(candidate, "participants.tsv")
        if os.path.isdir(derivatives_candidate) and os.path.isfile(participants_candidate):
            root_dir = candidate
            break

    if root_dir is None:
        raise FileNotFoundError("Dataset folder not found. Expected ds004504 or ds004504_annex")

    derivatives_dir = os.path.join(root_dir, "derivatives")
    participants_dir = os.path.join(root_dir, "participants.tsv")
    rows = []

    md_dataframe = pd.read_csv(participants_dir, sep='\t').set_index('participant_id')
    for i in sorted(os.listdir(derivatives_dir)):
        if not i.startswith("sub-"):
            continue

        sub_num = int(i.split('-')[1])
        path = os.path.join(derivatives_dir, i, 'eeg', f"{i}_task-eyesclosed_eeg.set")
        fallback_path = os.path.join(root_dir, i, 'eeg', f"{i}_task-eyesclosed_eeg.set")
        if not os.path.exists(path) and not os.path.exists(fallback_path):
            print(f"Skipping {i}: EEG file not found in derivatives or root EEG folder")
            continue

        print(f"{i}: Extract and epoch.")

        try:
            # Prefer derivatives, but fall back to root EEG if derivatives are unreadable.
            read_path = path if os.path.exists(path) else fallback_path
            try:
                raw_data = mne.io.read_raw_eeglab(read_path, preload=True, verbose=False)
            except Exception as exc:
                if read_path != fallback_path and os.path.exists(fallback_path):
                    print(f"{i}: derivatives unreadable ({exc}). Falling back to root EEG file.")
                    raw_data = mne.io.read_raw_eeglab(fallback_path, preload=True, verbose=False)
                else:
                    raise

            # Perform average referencing, bandpass filter, and resample to further clean data
            raw_data.set_eeg_reference(ref_channels='average', verbose=False)
            raw_data.filter(l_freq=0.5, h_freq=45, method='iir', iir_params=dict(order=2, ftype='butter'), phase='zero', verbose=False)
            raw_data.resample(128, verbose=False)
            md_data = md_dataframe.loc[i] if i in md_dataframe.index else None

            # Define 15 4 sec epochs per subject for better training (because the data set is so little)
            duration = 60
            step = 4
            
            for start in range(0, duration - step + 1, step):
                stop = start + step
                raw_data_ep = raw_data.copy().crop(tmin=start, tmax=stop - 1/128, verbose=False)
                data_ep = raw_data_ep.get_data()

                # FOr every epochs, extract features
                subject_feats = feature_extraction(data_ep, i, md_data, 128)

                # Group subjects into groups (0=Healthy, 1=FTD, 2=AD), add to rows
                if sub_num <= 36:
                    subject_feats['Group'] = 2
                elif 37 <= sub_num <= 65:
                    subject_feats['Group'] = 0
                else:
                    subject_feats['Group'] = 1
                rows.append(subject_feats)
        except Exception as exc:
            print(f"Skipping {i}: {exc}")
            continue
    
    # Form matrix with rows
    feature_matrix = pd.DataFrame(rows)
    feature_matrix.to_csv("Final_AD_Feature_Matrix.csv", index=False)
    print("Created feature matrix.")