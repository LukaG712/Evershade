export default function Navbar() {
  return (
    <header className="w-full border-b border-neutral-200">
      <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-12">
          <a href="/" className="text-lg font-bold tracking-tight">
            EVERSHADE
          </a>
          <div className="hidden md:flex items-center gap-8">
            <a href="/services/" className="font-mono text-xs uppercase tracking-widest text-neutral-500 hover:text-black transition-colors">
              Services
            </a>
            <a href="/docs/getting-started.html" className="font-mono text-xs uppercase tracking-widest text-neutral-500 hover:text-black transition-colors">
              Docs
            </a>
            <a href="/api/api-reference.html" className="font-mono text-xs uppercase tracking-widest text-neutral-500 hover:text-black transition-colors">
              API
            </a>
            <a href="/company/about.html" className="font-mono text-xs uppercase tracking-widest text-neutral-500 hover:text-black transition-colors">
              Company
            </a>
            <a href="/reference/glossary.html" className="font-mono text-xs uppercase tracking-widest text-neutral-500 hover:text-black transition-colors">
              Reference
            </a>
          </div>
        </div>
        <a
          href="/contact"
          className="font-mono text-xs uppercase tracking-widest px-5 py-2 border border-black rounded-none hover:bg-black hover:text-white transition-colors duration-150"
        >
          Contact
        </a>
      </nav>
    </header>
  )
}
