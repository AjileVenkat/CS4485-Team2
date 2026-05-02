import mne

# 1. Load one file
raw = mne.io.read_raw_eeglab("ds004504/derivatives/sub-001/eeg/sub-001_task-eyesclosed_eeg.set", preload=True)
raw.filter(0.5, 45)

# 2. Run ICA
# We use 15 components because you have 19 channels
ica = mne.preprocessing.ICA(n_components=15, random_state=42, method='fastica')
ica.fit(raw)

# 3. Visualize the components
# This will pop up a window showing the 'topographies'
ica.plot_components()