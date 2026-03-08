"""
Task 2: Frequency Analysis and Band Power (Authors' Preprocessed Derivatives)
- Computes PSD via Welch method for ALL AD and Control subjects
- Uses authors' preprocessed files (ASR + ICA cleaned) from derivatives/
- Extracts Delta (1-4), Theta (4-8), Alpha (8-13), Beta (13-30) band power
- Produces per-channel table and group-average comparison with bar chart

Task 3: Statistical Comparison Between Groups
- Computes mean band power per subject (one value per band per subject)
- Boxplots of Alpha and Theta power (AD vs Control)
- Independent t-test between AD and Control for each band
"""

import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.integrate import simpson
import os

mne.set_log_level('WARNING')

# Module-level constants
DATASET_DIR = "ds004504-download"
DERIV_DIR   = "ds004504-download/derivatives"   # authors' preprocessed files
IMAGES_DIR  = "images"
DATA_DIR    = "data"
CACHE_DIR   = "cache_authors"                   # authors' pipeline cache

GROUP_LABEL = {"A": "Alzheimer's Disease", "C": "Control"}

BANDS = {
    "Delta": (1,  4),
    "Theta": (4,  8),
    "Alpha": (8,  13),
    "Beta":  (13, 30),
}


def compute_band_power(subject_id: str, group: str) -> pd.DataFrame:
    """
    Load authors' preprocessed EEG for one subject, epoch, compute Welch PSD,
    return per-channel band-power DataFrame.

    Authors' preprocessing (already applied via ASR + ICA):
      1. Artifact Subspace Reconstruction (ASR) for transient artifact removal
      2. Independent Component Analysis (ICA) for ocular/muscle artifact removal
    My additions on top:
      3. Epoch into 2-second windows with 0.5s overlap
      4. Reject any remaining epochs exceeding 150 µV
      5. Welch PSD on clean epochs, averaged across epochs
      6. Band power = area under PSD curve (Simpson's rule)
    """
    eeg_path = os.path.join(
        DERIV_DIR, subject_id, "eeg",
        f"{subject_id}_task-eyesclosed_eeg.set"
    )
    if not os.path.exists(eeg_path):
        print(f"  [SKIP] not found: {eeg_path}")
        return pd.DataFrame()

    raw = mne.io.read_raw_eeglab(eeg_path, preload=True, verbose=False)

    cache_path = os.path.join(CACHE_DIR, f"{subject_id}_epo.fif")

    if os.path.exists(cache_path):
        # Cache hit: skip epoching on re-runs
        epochs = mne.read_epochs(cache_path, preload=True, verbose=False)
    else:
        # No filter or re-reference — authors' ASR + ICA already handled this
        # Epoch into fixed-length segments
        epochs = mne.make_fixed_length_epochs(
            raw, duration=2.0, overlap=0.5, preload=True, verbose=False
        )

        # Reject any remaining epochs that exceed amplitude threshold
        epochs.drop_bad(reject={'eeg': 150e-6}, verbose=False)

        # Save to cache so next run skips epoching for this subject
        epochs.save(cache_path, overwrite=True, verbose=False)

    if len(epochs) == 0:
        print(f"  [SKIP] all epochs rejected for {subject_id}")
        return pd.DataFrame()

    # Welch PSD on clean epochs
    psd        = epochs.compute_psd(method="welch", fmin=1, fmax=30, verbose=False)
    psd_data   = psd.get_data().mean(axis=0)   # average across epochs → (n_ch, n_freqs)
    freqs      = psd.freqs
    freq_res   = freqs[1] - freqs[0]

    rows = []
    for ch_idx, ch_name in enumerate(epochs.ch_names):
        row = {"Subject": subject_id, "Group": GROUP_LABEL[group], "Channel": ch_name}
        for band_name, (fmin, fmax) in BANDS.items():
            mask = (freqs >= fmin) & (freqs <= fmax)
            # Area under PSD curve (correct band power)
            row[f"{band_name} Power"] = simpson(psd_data[ch_idx, mask], dx=freq_res)
        rows.append(row)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(DATA_DIR,   exist_ok=True)
    os.makedirs(CACHE_DIR,  exist_ok=True)

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
    ax.set_title("Average EEG Band Power: Alzheimer's Disease vs Control\n(Authors' Preprocessing)",
                 fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(band_labels, fontsize=10)
    ax.legend(fontsize=10)
    ax.set_yscale("log")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    chart_path = os.path.join(IMAGES_DIR, "Group_Band_Power_Comparison_Authors.png")
    plt.savefig(chart_path, dpi=150)
    print(f"\nSaved → {chart_path}")
    plt.show()

    # TASK 3: Statistical Comparison Between Groups

    # 8. Compute mean band power per subject (average across all channels)
    subject_avg = (
        full_table
        .groupby(["Subject", "Group"])[band_cols]
        .mean()
        .reset_index()
    )
    subject_avg.to_csv(os.path.join(DATA_DIR, "Power_Comparison_SubjectAvg_Authors.csv"), index=False)
    print(f"\nSaved → {DATA_DIR}/Power_Comparison_SubjectAvg_Authors.csv  ({len(subject_avg)} rows)")

    print("\n" + "=" * 75)
    print("  Per-Subject Mean Band Power (averaged across all channels)")
    print("=" * 75)
    print(f"{'Subject':<10} | {'Group':<25} | {'Delta':>12} | {'Theta':>12} | {'Alpha':>12} | {'Beta':>12}")
    print("-" * 95)
    for _, r in subject_avg.iterrows():
        print(f"{r['Subject']:<10} | {r['Group']:<25} | {r['Delta Power']:>12.4e} | "
              f"{r['Theta Power']:>12.4e} | {r['Alpha Power']:>12.4e} | {r['Beta Power']:>12.4e}")
    print("-" * 95)

    # Split by group for statistical tests and boxplots
    ad_subjects   = subject_avg[subject_avg["Group"] == "Alzheimer's Disease"]
    ctrl_subjects = subject_avg[subject_avg["Group"] == "Control"]

    # 9. Boxplots: Alpha and Theta power (AD vs Control)
    for band_name in ["Alpha Power", "Theta Power"]:
        fig, ax = plt.subplots(figsize=(6, 5))
        bp_data = [
            ad_subjects[band_name].values,
            ctrl_subjects[band_name].values,
        ]
        bp = ax.boxplot(bp_data, tick_labels=["AD", "Control"], patch_artist=True,
                        widths=0.5, medianprops=dict(color="black", linewidth=1.5))
        bp["boxes"][0].set_facecolor("#E07070")
        bp["boxes"][1].set_facecolor("#6BAED6")
        ax.set_ylabel("Mean Power (V²/Hz)", fontsize=11)
        ax.set_title(f"{band_name}: Alzheimer's Disease vs Control\n(Authors' Preprocessing)",
                     fontsize=12, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        fname = band_name.replace(" ", "_") + "_Boxplot_Authors.png"
        fpath = os.path.join(IMAGES_DIR, fname)
        plt.savefig(fpath, dpi=150)
        print(f"Saved → {fpath}")
        plt.show()

    # 10. Statistical testing: independent t-test on log-transformed power
    #     Log transform applied because band power is log-normally distributed;
    #     this satisfies the normality assumption of the t-test and reduces
    #     the influence of outliers.
    print("\n" + "=" * 75)
    print("  Statistical Testing: Independent t-test on log(power) (AD vs Control)")
    print("=" * 75)
    print(f"{'Band':<14} | {'AD Mean':>13} | {'Ctrl Mean':>13} | {'Diff':>13} | {'t-stat':>10} | {'p-value':>12} | {'Significant?'}")
    print("-" * 105)

    for band in band_cols:
        ad_vals   = ad_subjects[band].values
        ctrl_vals = ctrl_subjects[band].values
        # Log-transform before t-test
        t_stat, p_val = stats.ttest_ind(np.log(ad_vals), np.log(ctrl_vals), equal_var=False)
        ad_mean   = ad_vals.mean()
        ctrl_mean = ctrl_vals.mean()
        diff      = ad_mean - ctrl_mean
        sig       = "Yes (p<0.05)" if p_val < 0.05 else "No"
        print(f"{band:<14} | {ad_mean:>13.4e} | {ctrl_mean:>13.4e} | {diff:>+13.4e} | {t_stat:>10.4f} | {p_val:>12.6f} | {sig}")
    print("-" * 105)