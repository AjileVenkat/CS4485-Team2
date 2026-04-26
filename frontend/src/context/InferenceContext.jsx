/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { INSIGHT_LIBRARY } from '../constants/insights'
import { ACCEPTED_EXTENSIONS, MAX_HISTORY_ITEMS } from '../constants/modelConfig'
import { requestLiveInference } from '../services/inferenceApi'
import {
  buildResult,
  generateMockResponse,
  sleep,
  stageFromProgress,
} from '../utils/inferenceHelpers'

const InferenceContext = createContext(null)

const STORAGE_KEYS = {
  mode: 'neuroscore.mode',
  history: 'neuroscore.history',
}

const readStoredMode = () => {
  if (typeof window === 'undefined') {
    return 'mock'
  }

  try {
    const storedMode = window.localStorage.getItem(STORAGE_KEYS.mode)
    if (storedMode === 'mock' || storedMode === 'live') {
      return storedMode
    }
  } catch {
    // Fall back to default mode when storage is blocked.
  }

  return 'mock'
}

const readStoredHistory = () => {
  if (typeof window === 'undefined') {
    return []
  }

  try {
    const rawHistory = window.localStorage.getItem(STORAGE_KEYS.history)
    const parsedHistory = JSON.parse(rawHistory ?? '[]')

    if (Array.isArray(parsedHistory)) {
      return parsedHistory.filter((item) => item && typeof item === 'object').slice(0, MAX_HISTORY_ITEMS)
    }
  } catch {
    // Ignore malformed or unavailable storage.
  }

  return []
}

export const InferenceProvider = ({ children }) => {
  const [mode, setMode] = useState(readStoredMode)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [warning, setWarning] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState(readStoredHistory)

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEYS.mode, mode)
    } catch {
      // Ignore storage write failures.
    }
  }, [mode])

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEYS.history, JSON.stringify(history))
    } catch {
      // Ignore storage write failures.
    }
  }, [history])

  const stageLabel = useMemo(() => {
    if (isRunning) {
      return stageFromProgress(progress)
    }

    if (result) {
      return 'Classification complete'
    }

    return 'Waiting for EEG upload'
  }, [isRunning, progress, result])

  const probabilityRows = useMemo(() => {
    const base = result?.breakdown ?? { AD: 0, HC: 0, FTD: 0 }

    return [
      { key: 'AD', value: base.AD },
      { key: 'HC', value: base.HC },
      { key: 'FTD', value: base.FTD },
    ]
  }, [result])

  const activeInsights = useMemo(() => {
    if (!result) {
      return []
    }

    return INSIGHT_LIBRARY[result.prediction] ?? []
  }, [result])

  const effectiveMode = result?.mode ?? mode

  const selectFile = useCallback((file) => {
    if (!file) {
      return
    }

    setSelectedFile(file)
    setResult(null)
    setWarning('')
    setError('')

    const normalizedName = file.name.toLowerCase()
    const isCommonEegFile = ACCEPTED_EXTENSIONS.some((extension) => normalizedName.endsWith(extension))

    if (!isCommonEegFile) {
      setWarning('This extension is uncommon for EEG data, but you can still run the demo pipeline.')
    }
  }, [])

  const clearSelection = useCallback(() => {
    setSelectedFile(null)
    setResult(null)
    setProgress(0)
    setWarning('')
    setError('')
  }, [])

  const clearHistory = useCallback(() => {
    setHistory([])
  }, [])

  const runClassification = useCallback(async (age, gender) => {
    if (!selectedFile || isRunning) {
      if (!selectedFile) {
        setError('Choose a file before running classification.')
      }
      return
    }

    setIsRunning(true)
    setProgress(4)
    setError('')
    setWarning('')
    setResult(null)

    const progressTimer = window.setInterval(() => {
      setProgress((current) => {
        if (current >= 92) {
          return current
        }

        return Math.min(92, current + Math.random() * 7 + 2)
      })
    }, 480)

    try {
      let outputMode = mode
      let payload

      if (mode === 'live') {
        try {
          payload = await requestLiveInference(selectedFile, age, gender)
        } catch {
          outputMode = 'mock-fallback'
          setWarning('Live backend is unavailable. Showing mock output so you can keep testing.')
          await sleep(1800)
          payload = generateMockResponse(selectedFile.name)
        }
      } else {
        await sleep(3600)
        payload = generateMockResponse(selectedFile.name)
      }

      setProgress(100)

      const normalized = buildResult(payload, selectedFile.name, outputMode)
      setResult(normalized)
      setHistory((previous) => [normalized, ...previous].slice(0, MAX_HISTORY_ITEMS))
    } catch (runError) {
      if (runError instanceof Error) {
        setError(runError.message)
      } else {
        setError('Inference failed. Please retry.')
      }
    } finally {
      window.clearInterval(progressTimer)
      setIsRunning(false)
    }
  }, [isRunning, mode, selectedFile])

  const value = useMemo(
    () => ({
      mode,
      effectiveMode,
      setMode,
      selectedFile,
      selectFile,
      clearSelection,
      clearHistory,
      runClassification,
      isRunning,
      progress,
      stageLabel,
      warning,
      error,
      result,
      history,
      probabilityRows,
      activeInsights,
    }),
    [
      activeInsights,
      clearHistory,
      clearSelection,
      effectiveMode,
      error,
      history,
      isRunning,
      mode,
      probabilityRows,
      progress,
      result,
      runClassification,
      selectFile,
      selectedFile,
      stageLabel,
      warning,
    ],
  )

  return <InferenceContext.Provider value={value}>{children}</InferenceContext.Provider>
}

export const useInference = () => {
  const context = useContext(InferenceContext)

  if (!context) {
    throw new Error('useInference must be used inside an InferenceProvider.')
  }

  return context
}
