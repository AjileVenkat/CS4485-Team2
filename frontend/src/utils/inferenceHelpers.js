import { PREDICTION_LABELS } from '../constants/classStyles'

export const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms))

export const clamp = (value, min, max) => Math.min(max, Math.max(min, value))

export const classFromLabel = (label) => {
  if (!label) {
    return null
  }

  const normalized = String(label).trim().toUpperCase()

  if (normalized === 'HEALTHY' || normalized === 'HC') {
    return 'HC'
  }

  if (normalized === 'AD' || normalized === 'ALZHEIMERS' || normalized === "ALZHEIMER'S") {
    return 'AD'
  }

  if (normalized === 'FTD' || normalized === 'FRONTOTEMPORAL DEMENTIA') {
    return 'FTD'
  }

  return null
}

export const stageFromProgress = (progress) => {
  if (progress < 20) {
    return 'Validating upload and channel map'
  }

  if (progress < 55) {
    return 'Extracting spectral and complexity features'
  }

  if (progress < 85) {
    return 'Running tri-class model inference'
  }

  if (progress < 100) {
    return 'Calibrating confidence and report cards'
  }

  return 'Classification complete'
}

export const normalizeBreakdown = (allProbs, predictionHint) => {
  const ad = Number(allProbs?.AD ?? allProbs?.ad ?? 0)
  const hc = Number(allProbs?.HC ?? allProbs?.hc ?? allProbs?.Healthy ?? allProbs?.healthy ?? 0)
  const ftd = Number(allProbs?.FTD ?? allProbs?.ftd ?? 0)

  let values = {
    AD: Number.isFinite(ad) && ad >= 0 ? ad : 0,
    HC: Number.isFinite(hc) && hc >= 0 ? hc : 0,
    FTD: Number.isFinite(ftd) && ftd >= 0 ? ftd : 0,
  }

  let total = values.AD + values.HC + values.FTD

  if (total <= 0) {
    const hintedClass = classFromLabel(predictionHint) ?? 'AD'
    values = { AD: 0.08, HC: 0.08, FTD: 0.08 }
    values[hintedClass] = 0.84
    total = 1
  }

  return {
    AD: clamp(values.AD / total, 0, 1),
    HC: clamp(values.HC / total, 0, 1),
    FTD: clamp(values.FTD / total, 0, 1),
  }
}

export const generateMockResponse = (fileName) => {
  const profiles = [
    { AD: 0.8, HC: 0.15, FTD: 0.05 },
    { AD: 0.2, HC: 0.7, FTD: 0.1 },
    { AD: 0.3, HC: 0.12, FTD: 0.58 },
    { AD: 0.62, HC: 0.24, FTD: 0.14 },
  ]

  const seed = [...fileName].reduce((accumulator, char) => accumulator + char.charCodeAt(0), 0)
  const base = profiles[seed % profiles.length]

  const jitterA = ((seed % 13) - 6) / 160
  const jitterB = ((seed % 11) - 5) / 180

  let ad = clamp(base.AD + jitterA, 0.03, 0.94)
  let hc = clamp(base.HC - jitterA + jitterB, 0.03, 0.94)
  let ftd = clamp(base.FTD - jitterB, 0.03, 0.94)

  const total = ad + hc + ftd
  ad /= total
  hc /= total
  ftd /= total

  const ranking = [
    ['AD', ad],
    ['HC', hc],
    ['FTD', ftd],
  ].sort((left, right) => right[1] - left[1])

  const topClass = ranking[0][0]

  return {
    status: 'success',
    prediction: topClass === 'HC' ? 'Healthy' : topClass,
    risk_score: Number((ranking[0][1] * 100).toFixed(2)),
    all_probs: {
      Healthy: hc,
      FTD: ftd,
      AD: ad,
    },
  }
}

export const buildResult = (payload, fileName, mode) => {
  const breakdown = normalizeBreakdown(payload?.all_probs, payload?.prediction)

  const prediction =
    classFromLabel(payload?.prediction) ??
    Object.entries(breakdown).sort((left, right) => right[1] - left[1])[0][0]

  const confidence = breakdown[prediction]

  const numericRisk = Number(payload?.risk_score)
  const riskScore = Number.isFinite(numericRisk) ? clamp(numericRisk, 0, 100) : null

  return {
    id: `${Date.now()}-${Math.round(Math.random() * 10000)}`,
    createdAt: new Date().toISOString(),
    mode,
    fileName,
    prediction,
    predictionLabel: PREDICTION_LABELS[prediction],
    confidence,
    riskScore,
    breakdown,
  }
}
