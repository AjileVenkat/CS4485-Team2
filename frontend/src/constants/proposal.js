export const PROJECT_SECTIONS = [
  {
    title: 'Idea',
    content:
      'This app accepts patient EEG data, runs it through a tri-class ML pipeline, and returns a cognitive progression assessment with transparent class metrics.',
  },
  {
    title: 'Clinical Motivation',
    content:
      'Alzheimer disease progression is associated with amyloid-beta and tau pathology and leads to neurodegeneration, especially affecting memory pathways. Early, signal-driven screening can help triage and monitoring workflows.',
  },
  {
    title: 'Literature Cues',
    content:
      'Many studies report higher delta and theta activity and lower alpha and beta activity in AD groups. We use this pattern as context when reading outputs.',
  },
  {
    title: 'Dataset Direction',
    content:
      'Model training uses OpenNeuro resting-state EEG data across AD, FTD, and healthy control groups in BIDS format.',
  },
  {
    title: 'Model Architecture',
    content:
      'Classifier strategy targets Healthy vs MCI-like patterns vs Alzheimer progression behavior through tri-class probability outputs that can be integrated with clinician review.',
  },
  {
    title: 'Operational Insight',
    content:
      'Checking consistency across repeated runs is usually more useful than relying on one prediction.',
  },
]
