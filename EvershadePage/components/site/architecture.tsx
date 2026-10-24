import { PRINCIPLES, SERVICES, TIER_LABEL, type ServiceTier } from '@/lib/evershade'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

const LAYERS: { tier: ServiceTier; label: string; note: string }[] = [
  { tier: 'client', label: 'Access', note: 'Browser, CLI, HTTP' },
  { tier: 'orchestrator', label: 'Orchestration', note: 'Auth, CSRF, rate limiting, retry, idempotency, workflow engine' },
  { tier: 'core', label: 'Core / required', note: 'Always installed' },
  { tier: 'optional', label: 'Supporting / optional', note: 'Toggle per profile' },
]

const SECURITY = [
  ['Bearer auth', 'Every service requires an Authorization: Bearer header.'],
  ['AES-256-GCM', 'Hider encrypts secrets at rest in SQLite.'],
  ['TLS proxy', 'Optional Caddy reverse proxy profile with TLS.'],
]

export function Architecture() {
  return (
    <section id="architecture" aria-labelledby="architecture-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="architecture-title"
        index="04"
        label="Architecture"
        title={
          <>
            Small services.
            <br />
            <span className="text-muted-foreground">Clear boundaries.</span>
          </>
        }
        lead="Every service has a single responsibility and a public HTTP interface. Greenie is the API-only backend that orchestrates the rest. Slammer is the single dashboard."
      />

      <div className="mt-16 md:mt-24" role="list" aria-label="Service layers">
        {LAYERS.map((layer, li) => {
          const services = SERVICES.filter((s) => s.tier === layer.tier)
          return (
            <div key={layer.tier} role="listitem" className="grid border-t border-foreground md:grid-cols-12">
              <div className="flex items-start justify-between gap-4 py-5 md:col-span-3 md:flex-col md:justify-start md:pr-6">
                <p className="font-mono text-[11px] uppercase tracking-wider">
                  <span className="text-muted-foreground">{`L${li} `}</span>
                  {layer.label}
                </p>
                <p className="max-w-[16rem] text-right text-sm leading-snug text-muted-foreground md:mt-2 md:text-left">{layer.note}</p>
              </div>
              <ul
                className={cn(
                  'grid border-l border-border md:col-span-9',
                  services.length === 1 ? 'grid-cols-1' : services.length === 2 ? 'grid-cols-2' : services.length === 3 ? 'grid-cols-3' : 'grid-cols-2 lg:grid-cols-4',
                )}
              >
                {services.map((svc) => (
                  <li
                    key={svc.id}
                    className={cn(
                      'flex min-h-32 flex-col justify-between border-r border-b border-border p-4 md:p-5',
                      layer.tier === 'orchestrator' && 'bg-foreground text-background',
                    )}
                  >
                    <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-wider opacity-60">
                      <span>{TIER_LABEL[svc.tier]}</span>
                      <span className="tabular-nums">{svc.port === 'CLI' ? 'CLI' : `:${svc.port}`}</span>
                    </div>
                    <div className="mt-6">
                      <p className={cn('font-semibold tracking-tight', layer.tier === 'orchestrator' ? 'text-4xl md:text-6xl' : 'text-xl md:text-2xl')}>
                        {svc.name}
                        {layer.tier === 'orchestrator' ? <span className="text-signal">.</span> : null}
                      </p>
                      <p className="mt-1 text-sm leading-snug opacity-60">{svc.role}</p>
                      <p className="mt-3 font-mono text-[10px] opacity-50">{svc.stack}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )
        })}
      </div>

      <div className="mt-24 grid gap-12 md:mt-32 md:grid-cols-12 md:gap-8">
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'04.1 — Design principles'}</p>
          <ol className="mt-6 border-t border-foreground">
            {PRINCIPLES.map(([title, body], i) => (
              <li key={title} className="grid grid-cols-[3rem_1fr] gap-4 border-b border-border py-6 md:grid-cols-[4rem_1fr_1fr] md:gap-8">
                <span className="font-mono text-xs text-muted-foreground">{String(i + 1).padStart(2, '0')}</span>
                <p className="text-2xl font-semibold tracking-tight md:text-3xl">{title}</p>
                <p className="col-start-2 text-pretty leading-snug text-muted-foreground md:col-start-auto">{body}</p>
              </li>
            ))}
          </ol>
        </div>
        <div className="md:col-span-4 md:col-start-9">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'04.2 — Security by default'}</p>
          <ul className="mt-6 border-t border-l border-foreground">
            {SECURITY.map(([title, body]) => (
              <li key={title} className="border-r border-b border-foreground p-5">
                <p className="flex items-center gap-2 font-mono text-xs">
                  <span className="size-1.5 bg-signal" aria-hidden="true" />
                  {title}
                </p>
                <p className="mt-3 text-pretty leading-snug text-muted-foreground">{body}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
