import Panel from '../ui/Panel'

const HeroSection = () => {
  const signalTrend = [28, 34, 31, 42, 39, 47, 44, 56, 52, 60, 57, 66]
  const trendPoints = signalTrend
    .map((value, index) => {
      const x = (index / (signalTrend.length - 1)) * 100
      const y = 100 - value
      return `${x},${y}`
    })
    .join(' ')

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
            Upload EEG data, run tri-class inference, and visualize dementia risk breakdowns
          </h1>

          <p className="mt-4 max-w-3xl text-sm text-slate-700 md:text-base">
            Use this dashboard to run EEG classification, track recent runs, and export results.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium uppercase tracking-[0.12em] text-slate-700">
            <span className="rounded-full border border-cyan-200 bg-cyan-100/80 px-3 py-1">
              Tri-class: HC vs FTD vs AD
            </span>
            <span className="rounded-full border border-orange-200 bg-orange-100/80 px-3 py-1">
              Real-time Inference Feedback
            </span>
            <span className="rounded-full border border-slate-300 bg-white/80 px-3 py-1">
              Mock + Live Modes
            </span>
          </div>
        </div>

        <div className="flex h-full flex-col justify-center rounded-2xl border border-slate-200/80 bg-white/85 p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-700">Signal Chart</p>
            <span className="rounded-full border border-cyan-200 bg-cyan-50 px-2 py-0.5 text-[10px] font-semibold text-cyan-700">
              Mock Demo
            </span>
          </div>

          <div className="my-3 flex-1 flex flex-col justify-center">
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-2 flex flex-col justify-center">
              <svg viewBox="0 0 100 100" className="h-28 w-full" preserveAspectRatio="none" aria-label="signal trend">
                <polyline
                  fill="none"
                  stroke="#06b6d4"
                  strokeWidth="2.4"
                  strokeLinejoin="round"
                  strokeLinecap="round"
                  points={trendPoints}
                />
              </svg>
            </div>
          </div>

          <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
            <div className="rounded-lg border border-slate-200 bg-white p-2 text-center">
              <p className="font-mono text-slate-500">Epochs</p>
              <p className="mt-1 font-semibold text-slate-800">12</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-2 text-center">
              <p className="font-mono text-slate-500">Window</p>
              <p className="mt-1 font-semibold text-slate-800">2s</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-2 text-center">
              <p className="font-mono text-slate-500">Quality</p>
              <p className="mt-1 font-semibold text-slate-800">Stable</p>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  )
}

export default HeroSection
