const normalizeStem = (fileName) => {
  const stem = fileName.replace(/\.[^/.]+$/, '')
  const compact = stem.trim().replace(/\s+/g, '-').replace(/[^a-zA-Z0-9-_]/g, '')
  return compact || 'eeg-run'
}

export const makeReportFileName = (fileName) => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').replace('Z', '')
  return `${normalizeStem(fileName)}_report_${timestamp}.json`
}

export const buildRunReport = (result) => {
  return {
    schemaVersion: '1.0.0',
    generatedAt: new Date().toISOString(),
    run: {
      id: result.id,
      createdAt: result.createdAt,
      fileName: result.fileName,
      prediction: result.prediction,
      predictionLabel: result.predictionLabel,
      confidence: result.confidence,
      riskScore: result.riskScore,
      breakdown: result.breakdown,
    },
  }
}

export const downloadJsonFile = (payload, fileName) => {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)

  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()

  window.URL.revokeObjectURL(url)
}