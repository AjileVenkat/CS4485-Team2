import { CLASS_STYLES } from '../../constants/classStyles'
import { SOURCE_LABELS } from '../../constants/modelConfig'
import { formatPercent, formatTime } from '../../utils/formatters'
import Panel from '../ui/Panel'

const HistoryPanel = ({ history, clearHistory }) => {
  return (
    <Panel className="animate-lift-in [animation-delay:620ms]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Recent Assessments</h3>
          <p className="mt-1 text-sm text-slate-600">Latest local run history</p>
        </div>

        <button
          type="button"
          onClick={clearHistory}
          disabled={history.length === 0}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition enabled:hover:border-slate-400 enabled:hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-45"
        >
          Clear History
        </button>
      </div>

      <div className="mt-4 max-h-[22.5rem] overflow-y-auto pr-1 flex flex-col space-y-3">
        {history.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600 w-full text-center">
              No assessments yet.
            </div>
          </div>
        ) : (
          history.map((item) => {
            const style = CLASS_STYLES[item.prediction] ?? CLASS_STYLES.AD
            return (
              <div key={item.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-slate-900">{item.fileName}</p>
                  <span className="font-mono text-xs text-slate-500">{formatTime(item.createdAt)}</span>
                </div>

                <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                  <span className={`rounded-full border px-2 py-1 font-semibold ${style.chip}`}>{item.prediction}</span>
                  <span className="rounded-full border border-slate-200 bg-white px-2 py-1 text-slate-600">
                    {SOURCE_LABELS[item.source ?? 'backend']}
                  </span>
                  <span className="rounded-full border border-slate-200 bg-white px-2 py-1 font-mono text-slate-700">
                    {formatPercent(item.confidence)} confidence
                  </span>
                </div>
              </div>
            )
          })
        )}
      </div>
    </Panel>
  )
}

export default HistoryPanel
