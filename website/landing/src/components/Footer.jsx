export default function Footer() {
  return (
    <footer className="w-full border-t border-neutral-200">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div className="col-span-2 md:col-span-1">
            <h3 className="text-lg font-bold tracking-tight mb-4">EVERSHADE</h3>
            <p className="text-sm text-neutral-500 leading-relaxed">
              Autonomous AI operations platform for self-improving software.
            </p>
          </div>
          <div>
            <h4 className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-4">
              Resources
            </h4>
            <ul className="space-y-2">
              <li><a href="/docs/getting-started.html" className="font-mono text-xs text-black hover:underline">getting started</a></li>
              <li><a href="/docs/deployment.html" className="font-mono text-xs text-black hover:underline">deployment</a></li>
              <li><a href="/docs/configuration.html" className="font-mono text-xs text-black hover:underline">configuration</a></li>
              <li><a href="/docs/security.html" className="font-mono text-xs text-black hover:underline">security</a></li>
              <li><a href="/reference/faq.html" className="font-mono text-xs text-black hover:underline">faq</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-4">
              Company
            </h4>
            <ul className="space-y-2">
              <li><a href="/company/about.html" className="font-mono text-xs text-black hover:underline">about</a></li>
              <li><a href="/company/architecture.html" className="font-mono text-xs text-black hover:underline">architecture</a></li>
              <li><a href="/news/changelog.html" className="font-mono text-xs text-black hover:underline">changelog</a></li>
              <li><a href="https://github.com/LukaG712/Evershade" target="_blank" rel="noopener noreferrer" className="font-mono text-xs text-black hover:underline">github</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-4">
              Legal
            </h4>
            <ul className="space-y-2">
              <li><a href="/license" className="font-mono text-xs text-black hover:underline">license</a></li>
              <li><a href="/privacy" className="font-mono text-xs text-black hover:underline">privacy</a></li>
              <li><a href="/terms" className="font-mono text-xs text-black hover:underline">terms</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-neutral-200 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="font-mono text-xs text-neutral-500">
            © 2025 Evershade. All rights reserved.
          </p>
          <p className="font-mono text-xs text-neutral-500">
            Licensed under MIT. Service names inspired by Luigi's Mansion.
          </p>
        </div>
      </div>
    </footer>
  )
}
