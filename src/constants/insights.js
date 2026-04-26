export const INSIGHT_LIBRARY = {
  AD: [
    {
      feature: 'Theta-Alpha imbalance',
      detail: 'Elevated slow-wave activity in frontal channels',
      level: 'High impact',
    },
    {
      feature: 'Connectivity drift',
      detail: 'PHI coupling reduced across temporal pairs',
      level: 'Medium impact',
    },
    {
      feature: 'Complexity drop',
      detail: 'Lower fractal complexity in parietal leads',
      level: 'Medium impact',
    },
  ],
  HC: [
    {
      feature: 'Balanced band profile',
      detail: 'Alpha and beta power remain stable per channel',
      level: 'Protective signal',
    },
    {
      feature: 'Connectivity consistency',
      detail: 'Mutual information pairings are within expected ranges',
      level: 'Protective signal',
    },
    {
      feature: 'Normal complexity',
      detail: 'Fractal descriptors align with healthy controls',
      level: 'Low concern',
    },
  ],
  FTD: [
    {
      feature: 'Frontal asymmetry',
      detail: 'Fronto-temporal bands deviate from baseline pattern',
      level: 'High impact',
    },
    {
      feature: 'Selective connectivity loss',
      detail: 'Reduced coupling in frontal-temporal links',
      level: 'Medium impact',
    },
    {
      feature: 'Regional complexity shift',
      detail: 'Complexity variance concentrated in anterior channels',
      level: 'Medium impact',
    },
  ],
}
