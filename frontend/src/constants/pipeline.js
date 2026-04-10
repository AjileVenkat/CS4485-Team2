export const PIPELINE_STEPS = [
  {
    id: '01',
    title: 'EEG Upload And Validation',
    detail: 'Accept EEG input files and validate channel coverage, duration, and structure before processing.',
    output: 'Validated input bundle',
  },
  {
    id: '02',
    title: 'Feature Extraction',
    detail: 'Compute spectral power, complexity, and connectivity features from the incoming EEG epochs.',
    output: 'Feature vector matrix',
  },
  {
    id: '03',
    title: 'Tri-Class Model Inference',
    detail: 'Run the trained classifier across Healthy Control, Frontotemporal Dementia, and Alzheimer classes.',
    output: 'Class probabilities',
  },
  {
    id: '04',
    title: 'Metric Packaging',
    detail: 'Assemble risk and confidence metrics for dashboard rendering and downstream reporting.',
    output: 'Prediction report payload',
  },
]

export const METRIC_DEFINITIONS = [
  {
    name: 'Class Probability Breakdown',
    description: 'Relative confidence distribution across AD, HC, and FTD outcomes.',
  },
  {
    name: 'Top-Class Confidence',
    description: 'Highest probability among all classes and a practical signal quality indicator.',
  },
  {
    name: 'Risk Score',
    description: 'Optional calibrated score from backend, displayed as pending when not provided.',
  },
]
