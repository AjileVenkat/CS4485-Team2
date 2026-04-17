import { PREDICTION_LABELS } from '../constants/classStyles'

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
    const hintedClass = classFromLabel(predictionHint)
    if (!hintedClass) {
      return { AD: 0, HC: 0, FTD: 0 }
    }

    return {
      AD: hintedClass === 'AD' ? 1 : 0,
      HC: hintedClass === 'HC' ? 1 : 0,
      FTD: hintedClass === 'FTD' ? 1 : 0,
    }
  }

  return {
    AD: clamp(values.AD / total, 0, 1),
    HC: clamp(values.HC / total, 0, 1),
    FTD: clamp(values.FTD / total, 0, 1),
  }
}

const normalizeInsights = (insights) => {
  if (!Array.isArray(insights)) {
    return []
  }

  return insights
    .map((item) => {
      if (typeof item === 'string' && item.trim()) {
        return {
          feature: item.trim(),
          detail: 'Provided by the assessment service.',
          level: 'Info',
        }
      }

      if (!item || typeof item !== 'object') {
        return null
      }

      const feature = typeof item.feature === 'string' ? item.feature.trim() : ''
      const detail = typeof item.detail === 'string' ? item.detail.trim() : ''
      const level = typeof item.level === 'string' ? item.level.trim() : ''

      if (!feature || !detail) {
        return null
      }

      return {
        feature,
        detail,
        level: level || 'Info',
      }
    })
    .filter(Boolean)
    .slice(0, 8)
}

export const buildResult = (payload, fileName) => {
  const breakdown = normalizeBreakdown(payload?.all_probs, payload?.prediction)

  const prediction =
    classFromLabel(payload?.prediction) ??
    Object.entries(breakdown).sort((left, right) => right[1] - left[1])[0]?.[0] ??
    'AD'

  const confidence = breakdown[prediction]

  const numericRisk = Number(payload?.risk_score)
  const riskScore = Number.isFinite(numericRisk) ? clamp(numericRisk, 0, 100) : null

  return {
    id: `${Date.now()}-${Math.round(Math.random() * 10000)}`,
    createdAt: new Date().toISOString(),
    source: 'backend',
    fileName,
    prediction,
    predictionLabel: PREDICTION_LABELS[prediction],
    confidence,
    riskScore,
    breakdown,
    insights: normalizeInsights(payload?.insights),
  }
}
