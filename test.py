# AD Risk scores from 19 channels (Fp1, Fp2, F7, F3, Fz, F4, F8, T3, C3, Cz, C4, T4, T5, P3, Pz, P4, T6, O1, and O2)
import mne

# Load EEG data for first subject only (for test, I will load all 88 subjects soon)
# Filter out extremely low noises and extreme high noises (comes from external factors such as sweating or electrical noise)
raw_data = mne.io.read_raw_eeglab("ds004504-download/sub-001/eeg/sub-001_task-eyesclosed_eeg.set", preload=True)
raw_data.filter(1.0, 40.0)

# Calculate power spectral density, gather frequency for each channel
pow_spec_dens = raw_data.compute_psd(method='welch', fmin=1, fmax=40)
data, frequency = pow_spec_dens.get_data(return_freqs = True)

raw_delta = (frequency >= 1) & (frequency <= 4)             # Frequency band for deep sleep and restorative healing
raw_theta = (frequency >= 4) & (frequency <= 8)             # Frequency band for REM Sleep and drowsiness
raw_total_alpha = (frequency >= 8) & (frequency <= 13)      # Frequency and relaxation and eyes closed
raw_alpha2 = (frequency >= 8) & (frequency <= 10.5)         # Subband for general memory
raw_alpha3 = (frequency >= 10.5) & (frequency <= 13)        # Subband for special cognitive functions
raw_beta = (frequency >= 13) & (frequency <= 30)            # Frequency band for high alert, active thinking, concentration

# For each band, splice data from 19 channels for the average power
delta_average = data[:, raw_delta].mean()
theta_average = data[:, raw_theta].mean()
total_alpha_average = data[:, raw_total_alpha].mean()
alpha2_average = data[:, raw_alpha2].mean()
alpha3_average = data[:, raw_alpha3].mean()
beta_average = data[:, raw_beta].mean()

mci_ad_risk = (delta_average + theta_average) / (total_alpha_average + beta_average)   # Calcualte Brain Cognitive and Arousal Score

print(f"Theta - Alpha Ratio: {theta_average/total_alpha_average: .4f}")         # General Risk Score
print(f"Delta - Alpha Ratio: {delta_average/total_alpha_average: .4f}")         # High Risk Score
print(f"Brain Cognitive Score: {mci_ad_risk: .4f} ")                                # Brain Cognitive Score
print(f"Alpha 3 - Alpha 2 Ratio: {alpha3_average / alpha2_average: .4f}")        # Conversion MCI->AD Score
