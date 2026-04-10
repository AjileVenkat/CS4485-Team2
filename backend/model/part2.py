import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

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

if __name__ == "__main__":
    data_dir = "ds004504"

    # Hold dataframes for AD and control groups
    ad_datas = []
    control_datas = []

    # Assign subject numbers to respective groups
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
    
    # Find the mean frequency per channel of each group
    ad_grouped = pd.concat(ad_datas).drop(columns=['Subject']).groupby('Channel').mean().reset_index()
    control_grouped = pd.concat(control_datas).drop(columns=['Subject']).groupby('Channel').mean().reset_index()
    
    # Record results in table
    with open("Task2_table.txt","w") as f:
        f.write("Average Band Power Per Channel: AD vs Control\n")
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

    # Record mean power per bands for all subjects in AD and control groups
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
    

    plt.tight_layout()
    plt.show()