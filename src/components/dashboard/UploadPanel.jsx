import { useRef, useState } from 'react'
import { ACCEPTED_EXTENSIONS } from '../../constants/modelConfig'
import { formatFileSize } from '../../utils/formatters'
import { classList } from '../../utils/classList'
import Panel from '../ui/Panel'

const UploadPanel = ({
  mode,
  setMode,
  selectedFile,
  selectFile,
  runClassification,
  clearSelection,
  isRunning,
  warning,
  error,
  apiUrl,
}) => {
  const fileInputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)
  const [age, setAge] = useState('')
  const [gender, setGender] = useState('')

  const acceptedLabel = '.set, .edf, .fif'

  const handleDrop = (event) => {
    event.preventDefault()
    setDragActive(false)

    if (event.dataTransfer.files.length > 0) {
      selectFile(event.dataTransfer.files[0])
    }
  }

  return (
    <Panel className="animate-lift-in [animation-delay:120ms]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">EEG Upload</h2>
          <p className="mt-1 text-sm text-slate-600">Drop a file or browse manually.</p>
        </div>

        <div className="inline-flex rounded-xl border border-slate-200 bg-white p-1 text-xs font-medium">
          <button
            type="button"
            onClick={() => setMode('mock')}
            className={classList(
              'rounded-lg px-3 py-1.5 transition',
              mode === 'mock' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:text-slate-900',
            )}
          >
            Mock Demo
          </button>

          <button
            type="button"
            onClick={() => setMode('live')}
            className={classList(
              'rounded-lg px-3 py-1.5 transition',
              mode === 'live' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:text-slate-900',
            )}
          >
            Live API
          </button>
        </div>
      </div>

      <div
        className={classList(
          'mt-5 rounded-2xl border-2 border-dashed p-6 transition',
          dragActive
            ? 'border-cyan-400 bg-cyan-50'
            : 'border-slate-300 bg-white/70 hover:border-slate-400 hover:bg-white',
        )}
        onDragOver={(event) => {
          event.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={(event) => {
          event.preventDefault()
          setDragActive(false)
        }}
        onDrop={handleDrop}
      >
        <p className="text-sm font-medium text-slate-700">Accepted Files: {acceptedLabel}</p>

        <p className="mt-2 text-sm text-slate-600">
          {selectedFile ? `${selectedFile.name} (${formatFileSize(selectedFile.size)})` : 'No file selected yet'}
        </p>

        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          className="hidden"
          onChange={(event) => selectFile(event.target.files?.[0])}
        />

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-sm font-medium text-slate-700">Age</label>
            <input
              type="number"
              min="1"
              max="120"
              value={age}
              onChange={(event) => setAge(event.target.value)}
              placeholder="Enter age"
              className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none transition focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Gender</label>
            <select
              value={gender}
              onChange={(event) => setGender(event.target.value)}
              className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none transition focus:border-cyan-500"
            >
              <option value="">Select gender</option>
              <option value="1">Female</option>
              <option value="0">Male</option>
            </select>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Choose File
          </button>

          <button
            type="button"
            onClick={() => runClassification(age, gender)}
            disabled={!selectedFile || !age || !gender || isRunning}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition enabled:hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-45"
          >
            {isRunning ? 'Processing...' : 'Run Classification'}
          </button>

          <button
            type="button"
            onClick={clearSelection}
            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
          >
            Reset
          </button>
        </div>
      </div>

      {warning ? (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {warning}
        </div>
      ) : null}

      {error ? (
        <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}
    </Panel>
  )
}

export default UploadPanel