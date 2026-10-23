export default function Hero() {
  return (
    <section className="w-full border-b border-neutral-200">
      <div className="max-w-7xl mx-auto px-6 py-24 md:py-32">
        <p className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-6">
          Autonomous AI Operations Platform
        </p>
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-black uppercase tracking-[0.25em] leading-[1.1] mb-8">
          Make Your Software<br />
          Improve Itself
        </h1>
        <p className="text-lg md:text-xl text-neutral-500 max-w-2xl mb-12 leading-relaxed">
          Evershade is a self-improving software platform that uses AI agents to automate development, deployment, monitoring, and optimization — so your systems get better without you lifting a finger.
        </p>
        <div className="flex flex-wrap gap-4">
          <a
            href="/docs/getting-started.html"
            className="btn-primary"
          >
            Get Started
          </a>
          <a
            href="/company/about.html"
            className="btn-secondary"
          >
            Learn More
          </a>
        </div>
      </div>
    </section>
  )
}
