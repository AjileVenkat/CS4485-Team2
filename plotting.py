import mne
import matplotlib.pyplot as plt
import os
import pandas as pd

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
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    # Get one AD and one control sample
    ad_sample = mne.io.read_raw_eeglab("ds004504/sub-001/eeg/sub-001_task-eyesclosed_eeg.set", preload=True)
    control_sample = mne.io.read_raw_eeglab("ds004504/sub-065/eeg/sub-065_task-eyesclosed_eeg.set", preload=True)
    
    

    # Paths to display ID in graphs
    ad_path = "ds004504/sub-001/eeg/sub-001_task-eyesclosed_eeg.set"
    control_path = "ds004504/sub-065/eeg/sub-065_task-eyesclosed_eeg.set"

    ad_id = os.path.basename(ad_path).split('_')[0]
    control_id = os.path.basename(control_path).split('_')[0]

    # Get channel name and frequency
    channels = ad_sample.ch_names
    freqs = ad_sample.info['sfreq']

    # Set target channel and time range to create graphs
    target_channel = 'P3'
    start_time = 10
    stop_time = 20

    # Create 2 graphs, get data according to the time range and frequencies
    figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex = True)

    ad_data, times = ad_sample.get_data(picks = target_channel, start = int(start_time * freqs), stop = int(stop_time * freqs), return_times=True)
    control_data, times  = control_sample.get_data(picks = target_channel, start = int(start_time * freqs), stop = int(stop_time * freqs), return_times=True)
    
    ad_dataframe = create_channels_table(ad_sample, ad_id)
    control_dataframe = create_channels_table(control_sample, control_id)

    final_table = pd.concat([ad_dataframe, control_dataframe]) 
    # comp_table = final_table.pivot(index='Channel', columns='Subject', values=['Alpha Power', 'Theta Power', 'Delta Power'])

    final_table.to_csv("Power_Comparison.csv", index=False)

    print("\n" + "="*60)
    print(f"{'Subject':<10} | {'Channel':<7} | {'Alpha Power':<11} | {'Theta Power':<11} | {'Delta Power':<11}")
    print("-" * 60)

    for i, row in final_table.head(38).iterrows():
        print(f"{row['Subject']:<10} | {row['Channel']:<7} | {row['Alpha Power']:<11.4e} | {row['Theta Power']:<11.4e} | {row['Delta Power']:<11.4e}")
    print("-" * 60 + "\n")

    # Build graphs
    axes[0].plot(times, ad_data.T, color="black")
    axes[0].set_title(f"Alzheimer's Disease Sample ({ad_id}) - Channel {target_channel}")
    axes[0].set_ylabel("Amplitude (uV)")
    axes[1].plot(times, control_data.T, color="red")
    axes[1].set_title(f"Control Healthy Sample ({control_id}) - Channel {target_channel}")
    axes[1].set_ylabel("Amplitude (uV)")
    axes[1].set_xlabel("Time (seconds)")

    plt.tight_layout()
    plt.show()

    