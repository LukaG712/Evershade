export function SectionHeading({
  index,
  label,
  title,
  lead,
  id,
}: {
  index: string
  label: string
  title: React.ReactNode
  lead?: React.ReactNode
  id: string
}) {
  return (
    <div className="grid gap-6 border-t border-foreground pt-6 md:grid-cols-12 md:gap-8">
      <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink md:col-span-3">{`${index} — ${label}`}</p>
      <div className="md:col-span-9">
        <h2 id={id} className="text-balance text-5xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-7xl lg:text-8xl">
          {title}
        </h2>
        {lead ? <p className="mt-6 max-w-2xl text-pretty text-lg leading-snug text-muted-foreground md:text-xl">{lead}</p> : null}
      </div>
    </div>
  )
}
