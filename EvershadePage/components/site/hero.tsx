'use client'

import { useEffect, useRef } from 'react'
import { ArrowDown, ArrowUpRight } from 'lucide-react'
import { EDGES, REPO_URL, SERVICES, TIER_LABEL, VERSION, type Service } from '@/lib/evershade'
import { cn } from '@/lib/utils'

const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v))
const range = (v: number, a: number, b: number) => clamp((v - a) / (b - a))
const lerp = (a: number, b: number, t: number) => a + (b - a) * t
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

const DOT_SIZE: Record<Service['tier'], number> = {
  orchestrator: 22,
  core: 14,
  optional: 11,
  client: 11,
}

type Point = { x: number; y: number }

export function Hero() {
  const wrapRef = useRef<HTMLDivElement>(null)
  const stageRef = useRef<HTMLDivElement>(null)
  const headRef = useRef<HTMLHeadingElement>(null)
  const introRef = useRef<HTMLDivElement>(null)
  const hudRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLDivElement>(null)
  const barRef = useRef<HTMLDivElement>(null)
  const pctRef = useRef<HTMLSpanElement>(null)
  const nodeRefs = useRef<(HTMLDivElement | null)[]>([])
  const edgeRefs = useRef<(SVGLineElement | null)[]>([])
  const packetRefs = useRef<(SVGRectElement | null)[]>([])
  const edgeGroupRef = useRef<SVGGElement>(null)

  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const start = performance.now()
    let raf = 0

    const tick = (now: number) => {
      raf = requestAnimationFrame(tick)
      const wrap = wrapRef.current
      const stage = stageRef.current
      const head = headRef.current
      const title = titleRef.current
      if (!wrap || !stage || !head || !title) return

      const rect = wrap.getBoundingClientRect()
      if (rect.bottom < 0) return

      const W = stage.clientWidth
      const H = stage.clientHeight
      const desktop = W >= 768
      const pad = desktop ? Math.max(24, W * 0.03) : 16
      const time = reduce ? 0 : (now - start) / 1000
      const p = clamp(-rect.top / (wrap.offsetHeight - H))

      // Headline: oversized at the bottom → compact wordmark at top-left.
      const h = ease(range(p, 0, 0.42))
      const headW = head.offsetWidth
      const headH = head.offsetHeight
      const topY = desktop ? 96 : 76
      const finalScale = (desktop ? Math.min(W * 0.36, 560) : W * 0.64) / headW
      const s = lerp(1, finalScale, h)
      const ty = lerp(0, topY + headH * finalScale - (H - pad), h)
      head.style.transform = `translate3d(0, ${ty}px, 0) scale(${s})`
      stage.style.setProperty('--head-h', `${headH}px`)

      const fade = 1 - range(p, 0, 0.14)
      if (introRef.current) {
        introRef.current.style.opacity = String(fade)
        introRef.current.style.transform = `translate3d(0, ${(1 - fade) * -40}px, 0)`
      }
      if (hudRef.current) hudRef.current.style.opacity = String(fade)

      // Section title fades in alongside the modular grid.
      const tt = ease(range(p, 0.5, 0.75))
      const titleTop = desktop ? topY : topY + headH * finalScale + 16
      title.style.top = `${titleTop}px`
      title.style.opacity = String(tt)
      title.style.transform = `translate3d(0, ${(1 - tt) * 32}px, 0)`
      title.style.pointerEvents = tt > 0.5 ? 'auto' : 'none'

      if (barRef.current) barRef.current.style.transform = `scaleY(${p})`
      if (pctRef.current) pctRef.current.textContent = String(Math.round(p * 100)).padStart(3, '0')

      // Network layout (constellation around the orchestrator).
      const netTop = desktop ? 120 : 110
      const netBottom = H - pad - headH - (desktop ? 110 : 150)
      const cx = W / 2
      const cy = (netTop + netBottom) / 2
      const R = Math.max(60, Math.min((netBottom - netTop) / 2, W * (desktop ? 0.3 : 0.26)))
      const stretch = desktop ? 1.55 : 0.82
      const rot = reduce ? 0 : time * 0.06 * (1 - range(p, 0.2, 0.5))
      const breathe = reduce ? 0 : Math.sin(time * 0.8) * 3

      const net: Point[] = SERVICES.map((svc, i) => {
        if (svc.tier === 'orchestrator') return { x: cx, y: cy }
        if (svc.tier === 'core') {
          const a = -Math.PI / 2 + (i - 1) * ((Math.PI * 2) / 3) + rot
          const r = R * 0.46 + breathe
          return { x: cx + Math.cos(a) * r * stretch, y: cy + Math.sin(a) * r }
        }
        if (svc.tier === 'optional') {
          const a = Math.PI / 4 + (i - 4) * (Math.PI / 2) - rot * 0.7
          const r = R * 0.92 - breathe
          return { x: cx + Math.cos(a) * r * stretch, y: cy + Math.sin(a) * r }
        }
        const side = svc.id === 'slammer' ? -1 : 1
        const x = desktop ? cx + side * R * stretch * 1.45 : side < 0 ? pad + 12 : W - pad - 112
        return { x, y: desktop ? cy : cy + R * 1.05 }
      })

      // Grid layout (modular service index).
      const cols = desktop ? 5 : 2
      const rows = SERVICES.length / cols
      const titleH = desktop ? 0 : title.offsetHeight + 16
      const gTop = desktop ? topY + headH * finalScale + 56 : titleTop + titleH
      const gBottom = H - pad
      const gW = W - pad * 2
      const cw = gW / cols
      const ch = Math.max(80, (gBottom - gTop) / rows)

      const centers: Point[] = []
      SERVICES.forEach((svc, i) => {
        const node = nodeRefs.current[i]
        if (!node) return
        const g = ease(range(p, 0.24 + i * 0.022, 0.58 + i * 0.022))
        const col = i % cols
        const row = Math.floor(i / cols)
        const gx = pad + col * cw + cw / 2
        const gy = gTop + row * ch + ch / 2
        const x = lerp(net[i].x, gx, g)
        const y = lerp(net[i].y, gy, g)
        const dot = DOT_SIZE[svc.tier]
        const w = lerp(dot, cw + 1, g)
        const hh = lerp(dot, ch + 1, g)
        centers[i] = { x, y }
        node.style.width = `${w}px`
        node.style.height = `${hh}px`
        node.style.transform = `translate3d(${x - w / 2}px, ${y - hh / 2}px, 0)`
        node.style.setProperty('--g', g.toFixed(3))
      })

      const edgeOpacity = 1 - range(p, 0.18, 0.42)
      if (edgeGroupRef.current) edgeGroupRef.current.style.opacity = String(edgeOpacity)
      if (edgeOpacity > 0) {
        EDGES.forEach(([a, b], i) => {
          const line = edgeRefs.current[i]
          const packet = packetRefs.current[i]
          const A = centers[a]
          const B = centers[b]
          if (!A || !B) return
          if (line) {
            line.setAttribute('x1', String(A.x))
            line.setAttribute('y1', String(A.y))
            line.setAttribute('x2', String(B.x))
            line.setAttribute('y2', String(B.y))
          }
          if (packet) {
            const f = (time * 0.32 + i * 0.137) % 1
            packet.setAttribute('x', String(lerp(A.x, B.x, f) - 2.5))
            packet.setAttribute('y', String(lerp(A.y, B.y, f) - 2.5))
            packet.style.opacity = String(reduce ? 0 : Math.sin(f * Math.PI))
          }
        })
      }
    }

    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  return (
    <section ref={wrapRef} aria-labelledby="hero-title" className="relative h-[340vh]">
      <div ref={stageRef} className="blueprint sticky top-0 h-svh w-full overflow-hidden">
        <CornerMarks />

        <div
          ref={hudRef}
          className="absolute inset-x-4 top-[72px] flex items-start justify-end sm:justify-between font-mono text-[11px] uppercase tracking-wider text-muted-foreground md:inset-x-[max(24px,3vw)]"
        >
          <span className="hidden sm:inline">{'[ Self-hosted / Docker / MIT ]'}</span>
          <span className="flex items-center gap-2">
            <span className="relative flex size-1.5">
              <span className="animate-pulse-ring absolute inset-0 bg-signal" />
              <span className="relative size-1.5 bg-signal" />
            </span>
            {`v${VERSION} · Production ready`}
          </span>
        </div>

        <svg className="pointer-events-none absolute inset-0 size-full" aria-hidden="true">
          <g ref={edgeGroupRef}>
            {EDGES.map((_, i) => (
              <line
                key={`edge-${i}`}
                ref={(el) => {
                  edgeRefs.current[i] = el
                }}
                stroke="currentColor"
                strokeOpacity={0.22}
                strokeWidth={1}
              />
            ))}
            {EDGES.map((_, i) => (
              <rect
                key={`packet-${i}`}
                ref={(el) => {
                  packetRefs.current[i] = el
                }}
                width={5}
                height={5}
                className="fill-signal"
              />
            ))}
          </g>
        </svg>

        <ul aria-label="Evershade services">
          {SERVICES.map((svc, i) => (
            <ServiceNode
              key={svc.id}
              svc={svc}
              index={i}
              nodeRef={(el) => {
                nodeRefs.current[i] = el
              }}
            />
          ))}
        </ul>

        <div
          ref={titleRef}
          className="absolute right-4 left-4 opacity-0 md:left-auto md:right-[max(24px,3vw)] md:w-[40%] md:max-w-xl"
        >
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'01 — Modular services'}</p>
          <p className="mt-3 text-pretty text-lg leading-snug tracking-tight md:text-2xl">
            Ten specialized microservices. Each has a single responsibility, talks over HTTP, and can run on its own
            while contributing to one platform.
          </p>
        </div>

        <div
          ref={introRef}
          className="absolute inset-x-4 flex flex-col gap-5 md:inset-x-[max(24px,3vw)] md:flex-row md:items-end md:justify-between"
          style={{ bottom: 'calc(var(--head-h, 20vw) + max(16px, 3vw) + 24px)' }}
        >
          <p className="max-w-md text-pretty text-base leading-snug md:text-lg">
            A self-hosted AI agent platform built as a collection of specialized microservices. Your agents. Your
            hardware. Your data.
          </p>
          <div className="flex items-center gap-2">
            <a
              href="#install"
              className="inline-flex h-11 items-center gap-2 bg-foreground px-5 text-sm font-medium text-background transition-colors hover:bg-signal-ink focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              Install Evershade
              <ArrowDown className="size-4" aria-hidden="true" />
            </a>
            <a
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-11 items-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              GitHub
              <ArrowUpRight className="size-4" aria-hidden="true" />
            </a>
          </div>
        </div>

        <h1
          ref={headRef}
          id="hero-title"
          className="absolute left-4 bottom-4 origin-bottom-left font-semibold leading-[0.78] tracking-[-0.075em] will-change-transform md:left-[max(24px,3vw)] md:bottom-[max(24px,3vw)]"
          style={{ fontSize: 'clamp(4.5rem, 21.5vw, 26rem)' }}
        >
          Evershade
          <span className="text-signal">.</span>
        </h1>

        <div className="absolute top-1/2 right-2 hidden -translate-y-1/2 flex-col items-center gap-3 md:flex" aria-hidden="true">
          <div className="relative h-32 w-px bg-foreground/15">
            <div ref={barRef} className="absolute inset-0 origin-top scale-y-0 bg-signal" />
          </div>
          <span ref={pctRef} className="font-mono text-[10px] tabular-nums text-muted-foreground [writing-mode:vertical-rl]">
            000
          </span>
        </div>
      </div>
    </section>
  )
}

function ServiceNode({
  svc,
  index,
  nodeRef,
}: {
  svc: Service
  index: number
  nodeRef: (el: HTMLDivElement | null) => void
}) {
  const filled = svc.tier === 'core'
  const orchestrator = svc.tier === 'orchestrator'

  return (
    <li>
      <div
        ref={nodeRef}
        className="absolute top-0 left-0 size-0 will-change-transform"
        style={{ '--g': 0 } as React.CSSProperties}
      >
        <div
          className={cn(
            'absolute inset-0 border bg-background',
            svc.tier === 'client' ? 'border-dashed border-foreground/60' : 'border-foreground',
          )}
        />
        <div
          className={cn('absolute inset-0', orchestrator ? 'bg-signal' : filled ? 'bg-foreground' : 'bg-transparent')}
          style={{ opacity: 'max(0, 1 - var(--g) * 4)' }}
        />
        {orchestrator ? (
          <span
            className="animate-pulse-ring absolute inset-0 border border-signal"
            style={{ opacity: 'calc(1 - var(--g))' }}
            aria-hidden="true"
          />
        ) : null}

        <span
          className="pointer-events-none absolute top-1/2 left-[calc(100%+10px)] -translate-y-1/2 whitespace-nowrap font-mono text-[10px] uppercase tracking-wider"
          style={{ opacity: 'max(0, 1 - var(--g) * 4)' }}
        >
          {svc.name}
          <span className="text-muted-foreground">{svc.port === 'CLI' ? ' cli' : ` :${svc.port}`}</span>
        </span>

        <div
          className="absolute inset-0 flex flex-col justify-between overflow-hidden p-3 md:p-5"
          style={{ opacity: 'max(0, var(--g) * 3 - 2)' }}
        >
          <div className="flex items-start justify-between font-mono text-[10px] uppercase tracking-wider text-muted-foreground md:text-[11px]">
            <span className="flex items-center gap-1.5">
              <span
                className={cn(
                  'size-1.5',
                  orchestrator ? 'bg-signal' : filled ? 'bg-foreground' : 'border border-foreground',
                )}
              />
              {String(index + 1).padStart(2, '0')}
              <span className="hidden lg:inline">{` / ${TIER_LABEL[svc.tier]}`}</span>
            </span>
            <span className="tabular-nums">{svc.port === 'CLI' ? 'CLI' : `:${svc.port}`}</span>
          </div>
          <div>
            <p className="text-xl font-semibold leading-none tracking-tight md:text-3xl">{svc.name}</p>
            <p className="mt-2 hidden text-sm leading-snug text-muted-foreground md:block">{svc.role}</p>
          </div>
        </div>
      </div>
    </li>
  )
}

function CornerMarks() {
  const base = 'pointer-events-none absolute size-3 border-foreground/40'
  return (
    <div aria-hidden="true">
      <span className={cn(base, 'top-[60px] left-2 border-t border-l')} />
      <span className={cn(base, 'top-[60px] right-2 border-t border-r')} />
      <span className={cn(base, 'bottom-2 left-2 border-b border-l')} />
      <span className={cn(base, 'bottom-2 right-2 border-b border-r')} />
    </div>
  )
}
