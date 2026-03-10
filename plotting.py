import mne
import matplotlib.pyplot as plt
import os
import pandas as pd
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
            'Beta Power': sample_data[i, raw_beta].mean(),
            'Theta Power': sample_data[i, raw_theta].mean(),
            'Delta Power': sample_data[i, raw_delta].mean(),
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    # Get one AD and one control sample
    #ad_sample = mne.io.read_raw_eeglab("ds004504/sub-001/eeg/sub-001_task-eyesclosed_eeg.set", preload=True)
    #control_sample = mne.io.read_raw_eeglab("ds004504/sub-065/eeg/sub-065_task-eyesclosed_eeg.set", preload=True)
    samples = []
    paths = []
    ids = []
    dataframes = []
    for i in range(1,89):
        num = str(i).zfill(3)
        sample = mne.io.read_raw_eeglab("ds004504/sub-" + num + "/eeg/sub-" + num + "_task-eyesclosed_eeg.set", preload=True)
        samples.append(sample)
        path = "ds004504/sub-" + num + "/eeg/sub-" + num + "_task-eyesclosed_eeg.set"
        paths.append(path)
        id = os.path.basename(path).split('_')[0]
        ids.append(id)
        dataframes.append(create_channels_table(sample, id))
    
    # Paths to display ID in graphs
    #ad_path = "ds004504/sub-001/eeg/sub-001_task-eyesclosed_eeg.set"
    #control_path = "ds004504/sub-065/eeg/sub-065_task-eyesclosed_eeg.set"

    #ad_id = os.path.basename(ad_path).split('_')[0]
    #control_id = os.path.basename(control_path).split('_')[0]

    # Get channel name and frequency
    #channels = ad_sample.ch_names
    #freqs = ad_sample.info['sfreq']

    # Set target channel and time range to create graphs
    # target_channel = 'P3'
    # start_time = 10
    # stop_time = 20

    # Create 2 graphs, get data according to the time range and frequencies
    #figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex = True)

    #ad_data, times = ad_sample.get_data(picks = target_channel, start = int(start_time * freqs), stop = int(stop_time * freqs), return_times=True)
    #control_data, times  = control_sample.get_data(picks = target_channel, start = int(start_time * freqs), stop = int(stop_time * freqs), return_times=True)
    
    #ad_dataframe = create_channels_table(ad_sample, ad_id)
    #control_dataframe = create_channels_table(control_sample, control_id)

    final_table = pd.concat(dataframes)
    mean_power = final_table.groupby('Subject').agg({
        'Alpha Power': 'mean',
        'Beta Power': 'mean',
        'Theta Power': 'mean',
        'Delta Power': 'mean'
    })
    statuses = []
    for i in range(1,89):
        if i >= 1 and i <= 36:
            statuses.append('A')
        elif i >= 37 and i <= 65:
            statuses.append('C')
        else:
            statuses.append('F')
    mean_power['Status'] = statuses

    alpha_power = mean_power.loc[mean_power['Status'] != 'F', ['Alpha Power','Status']]
    theta_power = mean_power.loc[mean_power['Status'] != 'F', ['Theta Power','Status']]
    # comp_table = final_table.pivot(index='Channel', columns='Subject', values=['Alpha Power', 'Theta Power', 'Delta Power'])

    #final_table.to_csv("Power_Comparison.csv", index=False)
    #mean_power.to_csv("Statistics.csv", index=False)
    alpha_power.to_csv("Alpha_Powers.csv", index=False)
    theta_power.to_csv("Theta_Powers.csv", index=False)

    alpha_power.boxplot(column='Alpha Power', by='Status', vert=False)
    
    t_statistic, p_value = stats.ttest_ind(alpha_power.loc[alpha_power['Status'] == 'A', ['Alpha Power']], alpha_power.loc[alpha_power['Status'] == 'C', ['Alpha Power']])
    
    print(f"T-statistic: {t_statistic}")
    print(f"P-value: {p_value}")
    #theta_power.boxplot(column='Theta Power', by='Status', vert=False)
    plt.show()
    # print("\n" + "="*75)
    # print(f"{'Subject':<10} | {'Channel':<7} | {'Alpha Power':<11} | {'Beta Power':<11} | {'Theta Power':<11} | {'Delta Power':<11}")
    # print("-" * 75)

    # for i, row in final_table.head(38).iterrows():
    #     print(f"{row['Subject']:<10} | {row['Channel']:<7} | {row['Alpha Power']:<11.4e} | {row['Beta Power']:<11.4e} | {row['Theta Power']:<11.4e} | {row['Delta Power']:<11.4e}")
    # print("-" * 75 + "\n")

    # Build graphs
    # axes[0].plot(times, ad_data.T, color="black")
    # axes[0].set_title(f"Alzheimer's Disease Sample ({ad_id}) - Channel {target_channel}")
    # axes[0].set_ylabel("Amplitude (uV)")
    # axes[1].plot(times, control_data.T, color="red")
    # axes[1].set_title(f"Control Healthy Sample ({control_id}) - Channel {target_channel}")
    # axes[1].set_ylabel("Amplitude (uV)")
    # axes[1].set_xlabel("Time (seconds)")

    #plt.tight_layout()
    #plt.show()

    