import Panel from '../components/ui/Panel'
import { PROJECT_SECTIONS } from '../constants/proposal'

const ProjectPage = () => {
  return (
    <section className="space-y-6">
      <Panel className="animate-lift-in">
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-cyan-700">Research Context</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">Project Context</h1>
        <p className="mt-3 max-w-3xl text-sm text-slate-700 md:text-base">
          Short project summary for team demos and documentation.
        </p>
      </Panel>

      <div className="grid gap-4 md:grid-cols-2">
        {PROJECT_SECTIONS.map((section, index) => (
          <Panel
            key={section.title}
            className="animate-lift-in bg-gradient-to-br from-white/95 to-slate-50/75"
            style={{ animationDelay: `${index * 80 + 120}ms` }}
          >
            <h2 className="text-xl font-semibold text-slate-900">{section.title}</h2>
            <p className="mt-3 text-sm text-slate-700">{section.content}</p>
          </Panel>
        ))}
      </div>
    </section>
  )
}

export default ProjectPage
