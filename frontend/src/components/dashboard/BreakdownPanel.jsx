import { CLASS_STYLES } from '../../constants/classStyles'
import { formatPercent } from '../../utils/formatters'
import Panel from '../ui/Panel'

const BreakdownPanel = ({ probabilityRows }) => {
  return (
    <Panel className="animate-lift-in [animation-delay:420ms]">
      <h3 className="text-lg font-semibold text-slate-900">Class Probability Breakdown</h3>
      <p className="mt-1 text-sm text-slate-600">AD vs HC vs FTD distribution</p>

      <div className="mt-5 space-y-4">
        {probabilityRows.map((entry) => {
          const style = CLASS_STYLES[entry.key] ?? CLASS_STYLES.AD

          return (
            <div key={entry.key}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${style.chip}`}>
                  {entry.key}
                </span>
                <span className="font-mono text-xs text-slate-700">{formatPercent(entry.value)}</span>
              </div>

              <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${style.bar} transition-all duration-700`}
                  style={{ width: `${Math.max(entry.value * 100, 2)}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <p className="mt-4 text-xs text-slate-500">Example output: 80% AD | 15% HC | 5% FTD</p>
    </Panel>
  )
}

export default BreakdownPanel
