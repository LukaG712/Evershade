const features = [
  {
    number: '01',
    title: 'Control',
    description: 'Orchestrate AI agents across your entire codebase. Deploy, monitor, and govern autonomous software improvement with full audit trails and rollback capabilities.',
    tag: 'Mission Control',
    link: '/api/mission-control.html'
  },
  {
    number: '02',
    title: 'Governance',
    description: 'Enforce security policies, rate limits, and access controls across all services. Every action is logged, every decision is traceable, every risk is contained.',
    tag: 'Security First',
    link: '/docs/security.html'
  },
  {
    number: '03',
    title: 'Value',
    description: 'Measure the real impact of AI on your development velocity. Track code quality improvements, bug reduction, and deployment frequency with actionable metrics.',
    tag: 'Observable',
    link: '/docs/resources.html'
  }
]

export default function FeatureGrid() {
  return (
    <section className="w-full">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-neutral-200 border-b border-neutral-200">
          {features.map((feature) => (
            <div key={feature.number} className="group p-8 md:p-10 flex flex-col">
              <span className="font-mono text-xs text-neutral-500 mb-4">
                {feature.number}
              </span>
              <h2 className="text-2xl md:text-3xl font-bold uppercase tracking-widest mb-4">
                {feature.title}
              </h2>
              <p className="text-neutral-500 leading-relaxed mb-6 flex-grow">
                {feature.description}
              </p>
              <div className="mt-auto">
                <span className="inline-block font-mono text-xs uppercase tracking-widest px-3 py-1 border border-neutral-200 mb-4">
                  {feature.tag}
                </span>
                <a
                  href={feature.link}
                  className="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-black group-hover:underline"
                >
                  Explore
                  <span className="transition-transform group-hover:translate-x-1">→</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
