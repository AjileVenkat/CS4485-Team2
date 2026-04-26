import { NavLink } from 'react-router-dom'
import { MODE_LABELS } from '../../constants/modelConfig'
import { NAV_ITEMS } from '../../constants/navigation'
import { useInference } from '../../context/InferenceContext'
import { classList } from '../../utils/classList'

const TopNav = () => {
  const { effectiveMode, isRunning } = useInference()

  return (
    <header className="panel sticky top-3 z-20 px-5 py-4 backdrop-blur-xl md:px-7">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-cyan-700">NeuroScore Web</p>
          <p className="text-sm text-slate-600">EEG classification workspace</p>
        </div>

        <nav className="flex flex-wrap items-center gap-2">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                classList(
                  'rounded-xl border px-3 py-1.5 text-sm font-semibold transition',
                  isActive
                    ? 'border-slate-900 bg-slate-900 text-white'
                    : 'border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:text-slate-900',
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-xs">
          <span className={classList('h-2 w-2 rounded-full', isRunning ? 'animate-pulse bg-cyan-500' : 'bg-slate-400')} />
          <span className="font-medium text-slate-600">Mode:</span>
          <span className="font-semibold uppercase tracking-[0.08em] text-slate-900">{MODE_LABELS[effectiveMode]}</span>
        </div>
      </div>
    </header>
  )
}

export default TopNav
