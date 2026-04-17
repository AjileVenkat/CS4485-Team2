import Panel from '../components/ui/Panel'
import { METRIC_DEFINITIONS, PIPELINE_STEPS } from '../constants/pipeline'

const PipelinePage = () => {
	return (
		<section className="space-y-6">
			<Panel className="animate-lift-in">
				<p className="font-mono text-[11px] uppercase tracking-[0.18em] text-cyan-700">Model Workflow</p>
				<h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">Inference Pipeline</h1>
				<p className="mt-3 max-w-3xl text-sm text-slate-700 md:text-base">
					End-to-end processing flow from EEG intake to class probability reporting and clinical-facing summary metrics.
				</p>
			</Panel>

			<div className="grid gap-4">
				{PIPELINE_STEPS.map((step, index) => (
					<Panel
						key={step.id}
						className="animate-lift-in bg-gradient-to-br from-white/95 to-slate-50/75"
						style={{ animationDelay: `${index * 90 + 120}ms` }}
					>
						<div className="flex flex-wrap items-center justify-between gap-3">
							<p className="font-mono text-xs uppercase tracking-[0.15em] text-cyan-700">Step {step.id}</p>
							<span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600">
								Output: {step.output}
							</span>
						</div>

						<h2 className="mt-3 text-xl font-semibold text-slate-900">{step.title}</h2>
						<p className="mt-2 text-sm text-slate-700">{step.detail}</p>
					</Panel>
				))}
			</div>

			<Panel className="animate-lift-in [animation-delay:380ms]">
				<h2 className="text-xl font-semibold text-slate-900">Operational Metrics</h2>
				<p className="mt-2 text-sm text-slate-600">Key metrics shown on the dashboard after each completed run.</p>

				<div className="mt-4 grid gap-3 md:grid-cols-3">
					{METRIC_DEFINITIONS.map((metric) => (
						<div key={metric.name} className="rounded-2xl border border-slate-200 bg-white p-4">
							<p className="text-sm font-semibold text-slate-900">{metric.name}</p>
							<p className="mt-2 text-sm text-slate-600">{metric.description}</p>
						</div>
					))}
				</div>
			</Panel>
		</section>
	)
}

export default PipelinePage
