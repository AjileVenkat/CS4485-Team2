import Panel from '../ui/Panel'

const HeroSection = ({ backendStatus }) => {
  const statusCopy = {
    idle: {
      label: 'Idle',
      chipClass: 'border-slate-300 bg-slate-100 text-slate-700',
      message: 'Ready for a new EEG assessment.',
    },
    processing: {
      label: 'Processing',
      chipClass: 'border-cyan-200 bg-cyan-50 text-cyan-700',
      message: 'Analysis is in progress. Results will refresh when complete.',
    },
    ready: {
      label: 'Ready',
      chipClass: 'border-emerald-200 bg-emerald-50 text-emerald-700',
      message: 'Latest assessment is ready for review and export.',
    },
    error: {
      label: 'Error',
      chipClass: 'border-rose-200 bg-rose-50 text-rose-700',
      message: 'The run could not be completed. Please verify the file and retry.',
    },
  }

  const activeStatus = statusCopy[backendStatus] ?? statusCopy.idle

  return (
    <Panel className="relative overflow-hidden px-6 py-8 animate-lift-in md:px-10 md:py-10">
      <div className="absolute -left-20 -top-24 h-52 w-52 rounded-full bg-cyan-200/50 blur-3xl" />
      <div className="absolute -right-12 top-8 h-48 w-48 rounded-full bg-orange-200/60 blur-3xl" />

      <div className="relative grid gap-6 md:grid-cols-[1.2fr_0.8fr] md:items-start">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-cyan-700">
            CS4485 Team 2 | EEG Dementia Classifier
          </p>

          <h1 className="mt-3 max-w-4xl text-3xl font-semibold tracking-tight text-slate-900 md:text-5xl">
            Clinical EEG classification dashboard
          </h1>

          <p className="mt-4 max-w-3xl text-sm text-slate-700 md:text-base">
            Upload EEG files, run tri-class classification (AD, HC, FTD), review confidence and risk score, and keep
            a local history of recent assessments.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium uppercase tracking-[0.12em] text-slate-700">
            <span className="rounded-full border border-cyan-200 bg-cyan-100/80 px-3 py-1">
              Tri-Class: AD | HC | FTD
            </span>
            <span className="rounded-full border border-orange-200 bg-orange-100/80 px-3 py-1">
              Session History
            </span>
            <span className="rounded-full border border-slate-300 bg-white/80 px-3 py-1">
              JSON Report Export
            </span>
          </div>
        </div>

        <div className="flex h-full flex-col justify-center rounded-2xl border border-slate-200/80 bg-white/85 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-700">Session Status</p>
            <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${activeStatus.chipClass}`}>
              {activeStatus.label}
            </span>
          </div>

          <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50/80 p-3">
            <p className="text-sm text-slate-700">{activeStatus.message}</p>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-2 text-xs sm:grid-cols-3">
            <div className="rounded-lg border border-slate-200 bg-white p-2 text-center">
              <p className="font-mono text-slate-500">Submission</p>
              <p className="mt-1 font-semibold text-slate-800">EEG File Upload</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-2 text-center">
              <p className="font-mono text-slate-500">Results</p>
              <p className="mt-1 font-semibold text-slate-800">Class Probabilities</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-2 text-center">
              <p className="font-mono text-slate-500">Reporting</p>
              <p className="mt-1 font-semibold text-slate-800">JSON Summary Export</p>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  )
}

export default HeroSection
