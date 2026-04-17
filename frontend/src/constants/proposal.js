export const PROJECT_SECTIONS = [
  {
    title: 'Idea',
    content:
      'This website accepts EEG files, runs tri-class classification, and returns class-level probabilities with a clear assessment summary.',
  },
  {
    title: 'Clinical Motivation',
    content:
      'Alzheimer disease progression is associated with neurodegenerative changes that can be reflected in EEG patterns. Early signal-driven assessment can support triage and monitoring workflows.',
  },
  {
    title: 'Literature Cues',
    content:
      'Prior studies often report higher delta and theta activity and lower alpha and beta activity in AD cohorts. This context helps interpret probability outputs.',
  },
  {
    title: 'Dataset Direction',
    content:
      'Model training uses OpenNeuro resting-state EEG data across AD, FTD, and healthy control groups in BIDS format.',
  },
  {
    title: 'Model Architecture',
    content:
      'The model returns tri-class probabilities across Healthy Control, Frontotemporal Dementia, and Alzheimer categories for clinician-guided review.',
  },
  {
    title: 'Operational Insight',
    content:
      'Consistency across repeated assessments is generally more informative than relying on a single run.',
  },
]
