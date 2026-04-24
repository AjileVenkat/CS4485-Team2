import { NavLink } from 'react-router-dom'
import { NAV_ITEMS } from '../../constants/navigation'
import { useInference } from '../../context/InferenceContext'
import { classList } from '../../utils/classList'

const TopNav = () => {
  const { backendStatus, isRunning } = useInference()

  const statusMap = {
    idle: {
      label: 'Standby',
      dotClass: 'bg-slate-400',
    },
    processing: {
      label: 'Processing',
      dotClass: 'animate-pulse bg-cyan-500',
    },
    ready: {
      label: 'Ready',
      dotClass: 'bg-emerald-500',
    },
    error: {
      label: 'Error',
      dotClass: 'bg-rose-500',
    },
  }

  const activeStatus = statusMap[backendStatus] ?? statusMap.idle

  return (
    <header className="fixed inset-x-0 top-0 z-[100] px-4 pt-3 md:px-8">
      <div className="mx-auto w-full max-w-6xl">
        <div className="panel px-5 py-4 backdrop-blur-xl md:px-7">
          <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] md:items-center">
            <div className="text-center md:text-left">
              <p className="font-mono text-xs uppercase tracking-[0.2em] text-cyan-700">NeuroScore Web</p>
              <p className="text-sm text-slate-600">Clinical EEG classification dashboard</p>
            </div>

            <nav className="flex flex-wrap items-center justify-center gap-2">
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

            <div className="mx-auto flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-xs md:ml-auto md:mr-0">
              <span className={classList('h-2 w-2 rounded-full', isRunning ? statusMap.processing.dotClass : activeStatus.dotClass)} />
              <span className="font-medium text-slate-600">System:</span>
              <span className="font-semibold uppercase tracking-[0.08em] text-slate-900">{activeStatus.label}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default TopNav
