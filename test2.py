import os
import pandas as pd
import mne

def features_extraction(raw_data, subject_id):
    raw_data.filter(1.0, 40.0, verbose=False)
    psd = raw_data.compute_psd(method="welch", fmin=1, fmax=40, verbose=False)
    data, freqs = psd.get_data(return_freqs=True)

    delta = (freqs >= 1) & (freqs < 4)
    theta = (freqs >= 4) & (freqs < 8)
    alpha = (freqs >= 8) & (freqs < 13)
    beta = (freqs >= 13) & (freqs < 30)

    delta_power = data[:, delta].mean(axis=1)
    theta_power = data[:, theta].mean(axis=1)
    alpha_power = data[:, alpha].mean(axis=1)
    beta_power = data[:, beta].mean(axis=1)

    theta_alpha = theta_power / (alpha_power + 1e-6)
    delta_alpha = delta_power / (alpha_power + 1e-6)

    row = {"Subject_ID": subject_id}

    for ch_idx in range(len(delta_power)):
        row[f"delta_ch{ch_idx}"] = float(delta_power[ch_idx])
        row[f"theta_ch{ch_idx}"] = float(theta_power[ch_idx])
        row[f"alpha_ch{ch_idx}"] = float(alpha_power[ch_idx])
        row[f"beta_ch{ch_idx}"] = float(beta_power[ch_idx])
        row[f"theta_alpha_ch{ch_idx}"] = float(theta_alpha[ch_idx])
        row[f"delta_alpha_ch{ch_idx}"] = float(delta_alpha[ch_idx])

    row["delta_mean"] = float(delta_power.mean())
    row["theta_mean"] = float(theta_power.mean())
    row["alpha_mean"] = float(alpha_power.mean())
    row["beta_mean"] = float(beta_power.mean())

    return row


if __name__ == "__main__":
    dir = "ds004504"
    rows = []

    labels_df = pd.read_csv(os.path.join(dir, "participants.tsv"), sep="\t")
    labels_df = labels_df.set_index("participant_id")

    label_map = {"C": 0, "F": 1, "A": 2}

    for i in sorted(os.listdir(dir)):
        if not i.startswith("sub-"):
            continue

        if i not in labels_df.index:
            continue

        path = os.path.join(dir, i, "eeg", f"{i}_task-eyesclosed_eeg.set")

        if os.path.exists(path):
            print(f"Extracting features for {i}...")
            raw_data = mne.io.read_raw_eeglab(path, preload=True, verbose=False)

            sub_features = features_extraction(raw_data, i)

            true_label = labels_df.loc[i, "Group"]
            sub_features["Group"] = label_map[true_label]

            rows.append(sub_features)

    feat_matrix = pd.DataFrame(rows)
    feat_matrix.to_csv("AD_Feature_Matrix.csv", index=False)
    print("Created feature matrix!")
    print("Shape:", feat_matrix.shape)
    print(feat_matrix["Group"].value_counts().sort_index())
