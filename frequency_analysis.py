"""
Task 2: Frequency Analysis and Band Power
- Computes PSD via Welch method for ALL AD and Control subjects
- Extracts Delta (1-4), Theta (4-8), Alpha (8-13), Beta (13-30) band power
- Produces per-channel table and group-average comparison with bar chart
"""

import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Module-level constants
DATASET_DIR = "ds004504-download"
IMAGES_DIR  = "images"
DATA_DIR    = "data"

GROUP_LABEL = {"A": "Alzheimer's Disease", "C": "Control"}

BANDS = {
    "Delta": (1,  4),
    "Theta": (4,  8),
    "Alpha": (8,  13),
    "Beta":  (13, 30),
}


def compute_band_power(subject_id: str, group: str) -> pd.DataFrame:
    """
    Load EEG for one subject, compute Welch PSD, return per-channel band-power DataFrame.
    Welch method:
      1. Splits signal into overlapping Hann-windowed segments
      2. FFT each segment
      3. Averages power across segments → stable spectral estimate
    """
    eeg_path = os.path.join(
        DATASET_DIR, subject_id, "eeg",
        f"{subject_id}_task-eyesclosed_eeg.set"
    )
    if not os.path.exists(eeg_path):
        print(f"  [SKIP] not found: {eeg_path}")
        return pd.DataFrame()

    raw = mne.io.read_raw_eeglab(eeg_path, preload=True, verbose=False)

    # Welch PSD
    psd = raw.compute_psd(method="welch", fmin=1, fmax=30, verbose=False)
    psd_data, freqs = psd.get_data(return_freqs=True)  # shape

    rows = []
    for ch_idx, ch_name in enumerate(raw.ch_names):
        row = {"Subject": subject_id, "Group": GROUP_LABEL[group], "Channel": ch_name}
        for band_name, (fmin, fmax) in BANDS.items():
            mask = (freqs >= fmin) & (freqs <= fmax)
            row[f"{band_name} Power"] = psd_data[ch_idx, mask].mean()
        rows.append(row)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(DATA_DIR,   exist_ok=True)

    # 1. Load participant group labels
    participants = pd.read_csv(
        os.path.join(DATASET_DIR, "participants.tsv"), sep="\t"
    )
    participants = participants[participants["Group"].isin(["A", "C"])].reset_index(drop=True)

    n_ad   = (participants["Group"] == "A").sum()
    n_ctrl = (participants["Group"] == "C").sum()
    total  = len(participants)
    print(f"Processing {total} subjects ({n_ad} AD, {n_ctrl} Control)...\n")

    # 2. Process every subject
    all_rows = []
    for i, (_, row) in enumerate(participants.iterrows(), 1):
        sid   = row["participant_id"]
        grp   = row["Group"]
        print(f"[{i:>3}/{total}] {sid}  ({GROUP_LABEL[grp]})", end="  ", flush=True)
        df = compute_band_power(sid, grp)
        if not df.empty:
            all_rows.append(df)
            print("OK")
        else:
            print("SKIPPED")

    # 3. Build per-channel table
    full_table = pd.concat(all_rows, ignore_index=True)
    col_order  = ["Subject", "Group", "Channel",
                  "Delta Power", "Theta Power", "Alpha Power", "Beta Power"]
    full_table = full_table[col_order]

    full_table.to_csv(os.path.join(DATA_DIR, "Power_Comparison_All.csv"), index=False)
    print(f"\nSaved → {DATA_DIR}/Power_Comparison_All.csv  ({len(full_table)} rows)\n")

    # 4. Print sample table
    first_sub = full_table["Subject"].iloc[0]
    sample_df = full_table[full_table["Subject"] == first_sub]
    print("=" * 75)
    print(f"  Per-Channel Band Power  —  {first_sub} ({sample_df['Group'].iloc[0]})")
    print("=" * 75)
    print(f"{'Channel':<7} | {'Delta Power':>13} | {'Theta Power':>13} | {'Alpha Power':>13} | {'Beta Power':>13}")
    print("-" * 75)
    for _, r in sample_df.iterrows():
        print(f"{r['Channel']:<7} | {r['Delta Power']:>13.4e} | {r['Theta Power']:>13.4e} | "
              f"{r['Alpha Power']:>13.4e} | {r['Beta Power']:>13.4e}")
    print("-" * 75)

    # 5. Group-average comparison
    band_cols = ["Delta Power", "Theta Power", "Alpha Power", "Beta Power"]
    group_avg = (
        full_table
        .groupby("Group")[band_cols]
        .mean()
        .reset_index()
    )

    group_avg.to_csv(os.path.join(DATA_DIR, "Group_Band_Power_Comparison.csv"), index=False)
    print(f"\nSaved → {DATA_DIR}/Group_Band_Power_Comparison.csv\n")

    print("=" * 75)
    print("  Group-Average Band Power: Alzheimer's Disease vs Control")
    print("=" * 75)
    print(f"{'Group':<25} | {'Delta Power':>13} | {'Theta Power':>13} | {'Alpha Power':>13} | {'Beta Power':>13}")
    print("-" * 75)
    for _, r in group_avg.iterrows():
        print(f"{r['Group']:<25} | {r['Delta Power']:>13.4e} | {r['Theta Power']:>13.4e} | "
              f"{r['Alpha Power']:>13.4e} | {r['Beta Power']:>13.4e}")
    print("-" * 75)

    # 6. Percent change AD vs Control
    ad_row   = group_avg[group_avg["Group"] == "Alzheimer's Disease"].iloc[0]
    ctrl_row = group_avg[group_avg["Group"] == "Control"].iloc[0]
    print("\nPercent change (AD vs Control):")
    for band in band_cols:
        pct = (ad_row[band] - ctrl_row[band]) / ctrl_row[band] * 100
        direction = "HIGHER" if pct > 0 else "LOWER"
        print(f"  {band:<14}: AD is {abs(pct):5.1f}% {direction} than Control")

    # 7. Bar chart
    band_labels = ["Delta\n(1-4 Hz)", "Theta\n(4-8 Hz)", "Alpha\n(8-13 Hz)", "Beta\n(13-30 Hz)"]
    ad_vals   = [ad_row[b]   for b in band_cols]
    ctrl_vals = [ctrl_row[b] for b in band_cols]

    x     = np.arange(len(band_cols))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width/2, ad_vals,   width, label="Alzheimer's Disease", color="#E07070")
    ax.bar(x + width/2, ctrl_vals, width, label="Control",             color="#6BAED6")

    ax.set_ylabel("Average Power (V\u00b2/Hz)", fontsize=11)
    ax.set_title("Average EEG Band Power: Alzheimer's Disease vs Control",
                 fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(band_labels, fontsize=10)
    ax.legend(fontsize=10)
    ax.set_yscale("log")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    chart_path = os.path.join(IMAGES_DIR, "Group_Band_Power_Comparison.png")
    plt.savefig(chart_path, dpi=150)
    print(f"\nSaved → {chart_path}")
    plt.show()
