import { ArrowUpRight } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'

const NAV = [
  { href: '#missions', label: 'Missions' },
  { href: '#harness', label: 'Harness' },
  { href: '#architecture', label: 'Architecture' },
  { href: '#install', label: 'Install' },
]

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="flex h-14 items-center justify-between px-4 md:px-[max(24px,3vw)]">
        <a href="#top" className="flex items-center gap-2.5 focus-visible:outline-2 focus-visible:outline-offset-4">
          <span className="grid size-5 grid-cols-2 gap-px" aria-hidden="true">
            <span className="bg-foreground" />
            <span className="bg-foreground" />
            <span className="bg-foreground" />
            <span className="bg-signal" />
          </span>
          <span className="text-sm font-semibold tracking-tight">Evershade</span>
        </a>
        <nav aria-label="Primary" className="hidden md:block">
          <ul className="flex items-center gap-8 font-mono text-[11px] uppercase tracking-wider">
            {NAV.map((item, i) => (
              <li key={item.href}>
                <a href={item.href} className="group flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-foreground">
                  <span className="text-foreground/30 transition-colors group-hover:text-signal-ink">{`0${i + 2}`}</span>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="inline-flex h-8 items-center gap-1.5 border border-foreground px-3 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
        >
          GitHub
          <ArrowUpRight className="size-3.5" aria-hidden="true" />
        </a>
      </div>
    </header>
  )
}
