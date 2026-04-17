import { useMemo, useState } from 'react'
import { CLASS_STYLES } from '../../constants/classStyles'
import { SOURCE_LABELS } from '../../constants/modelConfig'
import { classList } from '../../utils/classList'
import { formatPercent, formatTime } from '../../utils/formatters'
import { buildRunReport, downloadJsonFile, makeReportFileName } from '../../utils/reporting'
import Panel from '../ui/Panel'

const SummaryPanel = ({ result }) => {
  const [copyMessage, setCopyMessage] = useState('')
  const selectedSource = SOURCE_LABELS[result?.source ?? 'backend']
  const predictionTone = CLASS_STYLES[result?.prediction]?.tone ?? CLASS_STYLES.AD.tone
  const reportPayload = useMemo(() => (result ? buildRunReport(result) : null), [result])

  const handleDownloadReport = () => {
    if (!reportPayload || !result) {
      return
    }

    downloadJsonFile(reportPayload, makeReportFileName(result.fileName))
  }

  const handleCopyReport = async () => {
    if (!reportPayload) {
      return
    }

    if (!navigator?.clipboard?.writeText) {
      setCopyMessage('Clipboard unavailable in this browser')
      window.setTimeout(() => setCopyMessage(''), 1800)
      return
    }

    try {
      await navigator.clipboard.writeText(JSON.stringify(reportPayload, null, 2))
      setCopyMessage('Report copied')
    } catch {
      setCopyMessage('Copy failed')
    }

    window.setTimeout(() => setCopyMessage(''), 1800)
  }

  return (
    <Panel className="animate-lift-in [animation-delay:220ms]">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-slate-900">Assessment Summary</h2>
        <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">
          {selectedSource}
        </span>
      </div>

      {!result ? (
        <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600">
          Run classification to view predicted class, confidence, and risk score.
        </div>
      ) : (
        <>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Predicted Class</p>
              <p className={classList('mt-2 text-3xl font-semibold', predictionTone)}>{result.prediction}</p>
              <p className="mt-1 text-sm text-slate-600">{result.predictionLabel}</p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Risk Score</p>
              {result.riskScore === null ? (
                <>
                  <p className="mt-2 text-2xl font-semibold text-slate-800">Pending</p>
                  <p className="mt-1 text-sm text-slate-500">No calibrated score returned yet</p>
                </>
              ) : (
                <>
                  <p className="mt-2 text-3xl font-semibold text-slate-900">{result.riskScore.toFixed(1)}</p>
                  <p className="mt-1 text-sm text-slate-600">out of 100</p>
                </>
              )}
            </div>
          </div>

          <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between text-sm text-slate-600">
              <span>Top-class confidence</span>
              <span className="font-semibold text-slate-800">{formatPercent(result.confidence)}</span>
            </div>

            <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-orange-500 transition-all duration-700"
                style={{ width: `${Math.max(result.confidence * 100, 3)}%` }}
              />
            </div>

            <p className="mt-3 font-mono text-xs text-slate-500">
              {formatTime(result.createdAt)} | {result.fileName}
            </p>

            <div className="mt-4 flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={handleDownloadReport}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
              >
                Download Report
              </button>

              <button
                type="button"
                onClick={handleCopyReport}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
              >
                Copy JSON
              </button>

              {copyMessage ? <span className="text-xs text-slate-500">{copyMessage}</span> : null}
            </div>
          </div>
        </>
      )}
    </Panel>
  )
}

export default SummaryPanel
