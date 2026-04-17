import { Link } from 'react-router-dom'
import Panel from '../components/ui/Panel'

const NotFoundPage = () => {
  return (
    <Panel className="text-center animate-lift-in">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-cyan-700">404</p>
      <h1 className="mt-2 text-3xl font-semibold text-slate-900">Page not found</h1>
      <p className="mt-3 text-sm text-slate-600">The page you requested is not available.</p>
      <Link
        to="/"
        className="mt-5 inline-flex rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
      >
        Return to Dashboard
      </Link>
    </Panel>
  )
}

export default NotFoundPage
