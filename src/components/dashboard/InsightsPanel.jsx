import Panel from '../ui/Panel'

const InsightsPanel = ({ activeInsights }) => {
  return (
    <Panel className="animate-lift-in [animation-delay:520ms]">
      <h3 className="text-lg font-semibold text-slate-900">Signal Insights</h3>
      <p className="mt-1 text-sm text-slate-600">
        Feature cues that mirror your extraction pipeline categories.
      </p>

      <div className="mt-4 max-h-[22.5rem] overflow-y-auto pr-1 flex flex-col space-y-3">
        {activeInsights.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600 w-full text-center">
              Run a classification to preview likely EEG feature contributors.
            </div>
          </div>
        ) : (
          activeInsights.map((item) => (
            <div key={item.feature} className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-slate-900">{item.feature}</p>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                  {item.level}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-600">{item.detail}</p>
            </div>
          ))
        )}
      </div>
    </Panel>
  )
}

export default InsightsPanel
