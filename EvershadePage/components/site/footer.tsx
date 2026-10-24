import { ArrowUpRight } from 'lucide-react'
import { REPO_URL, VERSION } from '@/lib/evershade'

const LINKS = [
  ['Repository', REPO_URL],
  ['Changelog', `${REPO_URL}/blob/main/CHANGELOG.md`],
  ['Roadmap', `${REPO_URL}/blob/main/ROADMAP.md`],
  ['Documentation', `${REPO_URL}/tree/main/docs`],
]

export function Footer() {
  return (
    <footer className="mt-32 overflow-hidden border-t border-foreground px-4 pt-10 md:mt-48 md:px-[max(24px,3vw)]">
      <div className="grid gap-10 md:grid-cols-12">
        <p className="max-w-sm text-pretty text-lg leading-snug md:col-span-5">
          You own everything. Nothing leaves your machine unless you explicitly connect an external AI provider.
        </p>
        <ul className="grid grid-cols-2 gap-x-8 gap-y-3 md:col-span-4 md:col-start-7">
          {LINKS.map(([label, href]) => (
            <li key={label}>
              <a href={href} target="_blank" rel="noreferrer" className="group inline-flex items-center gap-1 text-sm hover:text-signal-ink">
                {label}
                <ArrowUpRight className="size-3.5 opacity-40 transition-opacity group-hover:opacity-100" aria-hidden="true" />
              </a>
            </li>
          ))}
        </ul>
        <div className="font-mono text-[11px] uppercase leading-relaxed tracking-wider text-muted-foreground md:col-span-2 md:text-right">
          <p>{`v${VERSION}`}</p>
          <p>{'MIT License'}</p>
        </div>
      </div>
      <p
        aria-hidden="true"
        className="mt-16 select-none font-semibold leading-[0.75] tracking-[-0.075em] text-foreground"
        style={{ fontSize: 'clamp(4.5rem, 21.5vw, 26rem)' }}
      >
        Evershade<span className="text-signal">.</span>
      </p>
    </footer>
  )
}
