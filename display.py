import mne

eeg_file_raw = "ds004504-download/sub-001/eeg/sub-001_task-eyesclosed_eeg.set"

raw_eeg = mne.io.read_raw_eeglab(eeg_file_raw, preload=True)

print(raw_eeg .info)

raw_eeg .plot()
