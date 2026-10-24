'use client'

import { useEffect, useRef, useState } from 'react'
import { Check, RotateCcw } from 'lucide-react'
import { MISSION_CAPABILITIES, MISSION_STAGES } from '@/lib/evershade'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

export function MissionControl() {
  const trackRef = useRef<HTMLDivElement>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    let raf = 0
    const update = () => {
      raf = 0
      const el = trackRef.current
      if (!el) return
      const rect = el.getBoundingClientRect()
      const total = el.offsetHeight - window.innerHeight
      setProgress(Math.min(1, Math.max(0, -rect.top / total)))
    }
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update)
    }
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
      cancelAnimationFrame(raf)
    }
  }, [])

  const count = MISSION_STAGES.length
  const active = Math.min(count - 1, Math.floor(progress * count * 0.999))
  const stage = MISSION_STAGES[active]

  return (
    <section id="missions" aria-labelledby="missions-title" className="relative">
      <div className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
        <SectionHeading
          id="missions-title"
          index="02"
          label="Mission Control"
          title={
            <>
              Large tasks in.
              <br />
              <span className="text-muted-foreground">Validated work out.</span>
            </>
          }
          lead="Factory-inspired orchestration for complex AI-driven development. Missions break large tasks into milestones, features and automated validation cycles."
        />
      </div>

      <div ref={trackRef} className="relative h-[280vh]">
        <div className="sticky top-0 flex h-svh flex-col justify-center px-4 pt-14 md:px-[max(24px,3vw)]">
          <div className="grid gap-10 md:grid-cols-12 md:gap-8">
            <div className="md:col-span-5" aria-live="polite">
              <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                {`Stage ${String(active + 1).padStart(2, '0')} / ${String(count).padStart(2, '0')}`}
              </p>
              <p
                key={stage.name}
                className="mt-4 text-6xl font-semibold leading-[0.85] tracking-[-0.06em] animate-in fade-in slide-in-from-bottom-4 duration-500 md:text-8xl"
              >
                {stage.name}
              </p>
              <p className="mt-6 max-w-md text-pretty text-lg leading-snug">{stage.body}</p>
              <code className="mt-6 inline-flex items-center gap-2 border border-foreground px-3 py-2 font-mono text-xs">
                <span className="size-1.5 bg-signal" aria-hidden="true" />
                {stage.endpoint}
              </code>
            </div>

            <ol className="relative md:col-span-6 md:col-start-7" aria-label="Mission workflow">
              <div className="absolute top-0 bottom-0 left-[15px] w-px bg-foreground/15" aria-hidden="true">
                <div
                  className="absolute inset-x-0 top-0 origin-top bg-signal"
                  style={{ height: '100%', transform: `scaleY(${progress})` }}
                />
              </div>
              {MISSION_STAGES.map((s, i) => {
                const done = i < active
                const current = i === active
                const isFix = s.name === 'Fix-Revalidate'
                return (
                  <li
                    key={s.name}
                    className={cn(
                      'relative flex items-center gap-5 border-b border-border py-4 transition-colors duration-300 md:py-5',
                      current ? 'text-foreground' : done ? 'text-foreground/70' : 'text-foreground/30',
                    )}
                  >
                    <span
                      className={cn(
                        'relative z-10 grid size-8 shrink-0 place-items-center border font-mono text-[11px] transition-colors duration-300',
                        current
                          ? 'border-foreground bg-foreground text-background'
                          : done
                            ? 'border-signal bg-background text-signal-ink'
                            : 'border-foreground/20 bg-background',
                      )}
                    >
                      {done ? <Check className="size-3.5" aria-hidden="true" /> : String(i + 1).padStart(2, '0')}
                    </span>
                    <span className="flex-1 text-2xl font-semibold tracking-tight md:text-3xl">{s.name}</span>
                    {isFix ? (
                      <span className="hidden items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider sm:flex">
                        <RotateCcw className="size-3" aria-hidden="true" />
                        {'On fail → Execute'}
                      </span>
                    ) : null}
                    {s.name === 'Complete' ? (
                      <span className="hidden font-mono text-[10px] uppercase tracking-wider sm:block">{'All pass'}</span>
                    ) : null}
                  </li>
                )
              })}
            </ol>
          </div>
        </div>
      </div>

      <div className="px-4 pb-8 md:px-[max(24px,3vw)]">
        <ul className="grid border-t border-l border-foreground sm:grid-cols-2 lg:grid-cols-3">
          {MISSION_CAPABILITIES.map(([title, body], i) => (
            <li key={title} className="border-r border-b border-foreground p-6 md:p-8">
              <p className="font-mono text-[11px] text-muted-foreground">{`M.${String(i + 1).padStart(2, '0')}`}</p>
              <p className="mt-10 text-xl font-semibold tracking-tight">{title}</p>
              <p className="mt-2 text-pretty leading-snug text-muted-foreground">{body}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
