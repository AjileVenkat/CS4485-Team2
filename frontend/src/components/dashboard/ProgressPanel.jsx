import Panel from '../ui/Panel'

const ProgressPanel = ({ progress, stageLabel, isRunning }) => {
  return (
    <Panel className="animate-lift-in [animation-delay:320ms]">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-slate-900">Run Progress</h3>
        <span className="font-mono text-sm text-slate-700">{Math.round(progress)}%</span>
      </div>

      <p className="mt-2 text-sm text-slate-600">{stageLabel}</p>

      <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-orange-500 transition-all duration-500 ${
            isRunning ? 'animate-pulse-line' : ''
          }`}
          style={{ width: `${Math.max(progress, 2)}%` }}
        />
      </div>

      <p className="mt-4 text-sm text-slate-600">
        {isRunning
          ? 'This panel tracks validation, feature extraction, and classification progress.'
          : 'Upload a file and start a run to monitor processing progress.'}
      </p>
    </Panel>
  )
}

export default ProgressPanel
