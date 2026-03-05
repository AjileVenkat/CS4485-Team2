import mne
import matplotlib.pyplot as plt
import os
import pandas as pd

DATASET_DIR = "ds004504-download"
IMAGES_DIR  = "images"
DATA_DIR    = "data"

def create_channels_table(sample, subject_id, group):
    """Compute Welch PSD and return a per-channel band power DataFrame."""
    # Compute PSD for all channels using the Welch method (fmin=1, fmax=30 Hz)
    sample_psd = sample.compute_psd(method='welch', fmin=1, fmax=30, verbose=False)
    sample_data, freqs = sample_psd.get_data(return_freqs=True)

    raw_delta = (freqs >= 1)  & (freqs <= 4)   # Deep slow-wave activity
    raw_theta = (freqs >= 4)  & (freqs <= 8)   # Drowsiness / REM-adjacent
    raw_alpha = (freqs >= 8)  & (freqs <= 13)  # Relaxed eyes-closed rhythm
    raw_beta  = (freqs >= 13) & (freqs <= 30)  # Active / alert cognition

    rows = []
    for i, channel in enumerate(sample.ch_names):
        rows.append({
            'Subject':     subject_id,
            'Group':       group,
            'Channel':     channel,
            'Delta Power': sample_data[i, raw_delta].mean(),
            'Theta Power': sample_data[i, raw_theta].mean(),
            'Alpha Power': sample_data[i, raw_alpha].mean(),
            'Beta Power':  sample_data[i, raw_beta].mean(),
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(DATA_DIR,   exist_ok=True)

    # Load all AD and Control subjects from participants.tsv
    participants = pd.read_csv(
        os.path.join(DATASET_DIR, "participants.tsv"), sep="\t"
    )
    participants = participants[participants["Group"].isin(["A", "C"])].reset_index(drop=True)
    GROUP_LABEL  = {"A": "Alzheimer's Disease", "C": "Control"}

    total = len(participants)
    n_ad  = (participants["Group"] == "A").sum()
    n_ctrl = (participants["Group"] == "C").sum()
    print(f"Processing {total} subjects ({n_ad} AD, {n_ctrl} Control)...\n")

    # Build per-channel band-power table
    all_frames = []
    for i, (_, prow) in enumerate(participants.iterrows(), 1):
        sid   = prow["participant_id"]
        grp   = prow["Group"]
        path  = os.path.join(DATASET_DIR, sid, "eeg", f"{sid}_task-eyesclosed_eeg.set")
        if not os.path.exists(path):
            print(f"[{i:>3}/{total}] {sid} SKIPPED (file not found)")
            continue
        print(f"[{i:>3}/{total}] {sid}  ({GROUP_LABEL[grp]})", end="  ", flush=True)
        raw = mne.io.read_raw_eeglab(path, preload=True, verbose=False)
        df  = create_channels_table(raw, sid, GROUP_LABEL[grp])
        all_frames.append(df)
        print("OK")

    final_table = pd.concat(all_frames, ignore_index=True)

    final_table.to_csv(os.path.join(DATA_DIR, "Power_Comparison.csv"), index=False)
    print(f"\nSaved → {DATA_DIR}/Power_Comparison.csv  ({len(final_table)} rows)")

    # Per-channel table printout
    first_sub = final_table["Subject"].iloc[0]
    sample_df = final_table[final_table["Subject"] == first_sub]
    print("\n" + "="*75)
    print(f"  Sample: {first_sub} ({sample_df['Group'].iloc[0]})")
    print(f"{'Subject':<10} | {'Group':<21} | {'Channel':<7} | {'Delta':>10} | {'Theta':>10} | {'Alpha':>10} | {'Beta':>10}")
    print("-" * 75)
    for _, row in sample_df.iterrows():
        print(f"{row['Subject']:<10} | {row['Group']:<21} | {row['Channel']:<7} | "
              f"{row['Delta Power']:>10.3e} | {row['Theta Power']:>10.3e} | "
              f"{row['Alpha Power']:>10.3e} | {row['Beta Power']:>10.3e}")
    print("-" * 75)

    # Group-average comparison
    band_cols = ['Delta Power', 'Theta Power', 'Alpha Power', 'Beta Power']
    group_avg = final_table.groupby('Group')[band_cols].mean()
    print("\nGroup-Average Band Power:")
    print(group_avg.to_string())
    group_avg.to_csv(os.path.join(DATA_DIR, "Power_Comparison_GroupAvg.csv"))
    print(f"\nSaved → {DATA_DIR}/Power_Comparison_GroupAvg.csv\n")

    # Waveform plot: first AD vs first Control subject, channel P3
    target_channel = 'P3'
    start_time     = 10
    stop_time      = 20

    ad_subs   = participants[participants["Group"] == "A"]["participant_id"].tolist()
    ctrl_subs = participants[participants["Group"] == "C"]["participant_id"].tolist()
    ad_id     = ad_subs[0]
    ctrl_id   = ctrl_subs[0]

    ad_raw   = mne.io.read_raw_eeglab(
        os.path.join(DATASET_DIR, ad_id,   "eeg", f"{ad_id}_task-eyesclosed_eeg.set"),
        preload=True, verbose=False)
    ctrl_raw = mne.io.read_raw_eeglab(
        os.path.join(DATASET_DIR, ctrl_id, "eeg", f"{ctrl_id}_task-eyesclosed_eeg.set"),
        preload=True, verbose=False)

    sfreq = ad_raw.info['sfreq']
    ad_data,   times = ad_raw.get_data(picks=target_channel,
                                        start=int(start_time * sfreq),
                                        stop=int(stop_time * sfreq),
                                        return_times=True)
    ctrl_data, _     = ctrl_raw.get_data(picks=target_channel,
                                          start=int(start_time * sfreq),
                                          stop=int(stop_time * sfreq),
                                          return_times=True)

    figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(times, ad_data.T,   color="black")
    axes[0].set_title(f"Alzheimer's Disease ({ad_id}) — Channel {target_channel}")
    axes[0].set_ylabel("Amplitude (uV)")
    axes[1].plot(times, ctrl_data.T, color="red")
    axes[1].set_title(f"Control ({ctrl_id}) — Channel {target_channel}")
    axes[1].set_ylabel("Amplitude (uV)")
    axes[1].set_xlabel("Time (seconds)")

    plt.tight_layout()
    waveform_path = os.path.join(IMAGES_DIR, f"waveform_{target_channel}.png")
    plt.savefig(waveform_path, dpi=150)
    print(f"Saved → {waveform_path}")
    plt.show()
