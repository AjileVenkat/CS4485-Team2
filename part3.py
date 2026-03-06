import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from scipy import stats

def create_channels_table(sample, id):
    # Compute PSD for all 19 channels with the Welch method
    sample_psd = sample.compute_psd(method='welch', fmin=1, fmax=30, verbose=False)
    sample_data, freqs = sample_psd.get_data(return_freqs=True)
    
    raw_delta = (freqs >= 1) & (freqs <= 4)
    raw_theta = (freqs >= 4) & (freqs <= 8)
    raw_alpha = (freqs >= 8) & (freqs <= 13)
    raw_beta = (freqs >= 13) & (freqs <= 30)
    rows = []
    for i, channel in enumerate(sample.ch_names):
        rows.append({
            'Subject': id,
            'Channel': channel,
            'Alpha Power': sample_data[i, raw_alpha].mean(),
            'Theta Power': sample_data[i, raw_theta].mean(),
            'Delta Power': sample_data[i, raw_delta].mean(),
            'Beta Power': sample_data[i, raw_beta].mean(),
        })
    return pd.DataFrame(rows)

def ttest(ad, control, band):
    t_stat, p_val = stats.ttest_ind(ad, control)
    print(f"--- {band} Stats ---")
    print(f"Mean AD: {ad.mean():.4e}")
    print(f"Mean Control: {control.mean():.4e}")
    print(f"T-Stats: {t_stat:.4e}")
    print(f"P-Value: {p_val:.4e}")
    if p_val < 0.05:
        print("Result has significant difference.\n")
    else:
        print("Result: Result has no difference.\n")

if __name__ == "__main__":
    data_dir = "ds004504"
    ad_datas = []
    control_datas = []
    for id in sorted(os.listdir(data_dir)):
        if not id.startswith("sub-"):
            continue
        sub_id = int(id.split('-')[1])
        if 1 <= sub_id <= 65:
            path = os.path.join(data_dir, id, 'eeg', f"{id}_task-eyesclosed_eeg.set")
            raw_data = mne.io.read_raw_eeglab(path, preload=True, verbose=True)

            current_dframe = create_channels_table(raw_data, id)
            if (sub_id <= 36):
                ad_datas.append(current_dframe)
            else:
                control_datas.append(current_dframe)
    
    ad_grouped = pd.concat(ad_datas).drop(columns=['Subject']).groupby('Channel').mean().reset_index()
    control_grouped = pd.concat(control_datas).drop(columns=['Subject']).groupby('Channel').mean().reset_index()
    
    with open("Task2_table.txt","w") as f:
        f.write("Average Band Power Per Channel: AD vs Control\n")
        f.write("\n" + "="*70)
        f.write(f"\n{'Subject':<10} | {'Channel':<7} | {'Alpha Power':<11} | {'Theta Power':<11} | {'Delta Power':<11}\n")
        f.write("-" * 70 + "\n")
        
        for i in ad_grouped['Channel']:
            ad_row = ad_grouped[ad_grouped['Channel'] == i].iloc[0]
            control_row = control_grouped[control_grouped['Channel'] == i].iloc[0]
            f.write(f"{'AD':<10} | {i:<7} | {ad_row['Alpha Power']:<11.4e} | {ad_row['Theta Power']:<11.4e} | {ad_row['Delta Power']:<11.4e}\n")
            f.write(f"{'Control':<10} | {i:<7} | {control_row['Alpha Power']:<11.4e} | {control_row['Theta Power']:<11.4e} | {control_row['Delta Power']:<11.4e}\n")
            f.write("-" * 70 + "\n")

    ad_values = ad_grouped[['Delta Power', 'Theta Power', 'Alpha Power', 'Beta Power']].mean()
    control_values = control_grouped[['Delta Power', 'Theta Power', 'Alpha Power', 'Beta Power']].mean()

    categories = ['Delta', 'Theta', 'Alpha', 'Beta']

    plt.figure(figsize=(10, 6))
    x = range(len(categories))
    width = 0.35
    plt.bar([i - width/2 for i in x], ad_values, width, label = f'AD', color = 'black')
    plt.bar([i + width/2 for i in x], control_values, width, label = f'Control', color = 'red')
    
    plt.yscale('log')
    plt.ylabel('Mean Power')
    plt.title('Brain Power Comparison: AD vs Control')
    plt.xticks(x, categories)
    plt.legend()
    plt.grid(axis = 'y', linestyle='--', alpha=0.7)

    ad_subject_avg = [df[['Alpha Power', 'Theta Power', 'Delta Power', 'Beta Power']].mean() for df in ad_datas]
    control_subject_avg = [df[['Alpha Power', 'Theta Power', 'Delta Power', 'Beta Power']].mean() for df in control_datas]

    ad_subject_dframe = pd.DataFrame(ad_subject_avg)
    control_subject_dframe = pd.DataFrame(control_subject_avg)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    axes[0].boxplot([ad_subject_dframe['Alpha Power'], control_subject_dframe['Alpha Power']], labels=['AD', 'Control'])
    axes[0].set_title('Alpha Power Distribution')
    axes[0].set_ylabel('Absolute Power')
    axes[0].set_yscale('log')

    axes[1].boxplot([ad_subject_dframe['Theta Power'], control_subject_dframe['Theta Power']], labels=['AD', 'Control'])
    axes[1].set_title('Theta Power Distribution')
    axes[1].set_ylabel('Absolute Power')
    axes[1].set_yscale('log')

    plt.tight_layout()
    plt.show()

    ttest(ad_subject_dframe['Alpha Power'], control_subject_dframe['Alpha Power'], "Alpha")
    ttest(ad_subject_dframe['Theta Power'], control_subject_dframe['Theta Power'], "Theta")
