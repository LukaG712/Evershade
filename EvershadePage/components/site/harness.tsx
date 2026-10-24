import { SectionHeading } from './section-heading'

const HARNESS = [
  {
    code: 'SPEC',
    title: 'Spec Mode',
    body: 'Research-first development. Create a spec, analyze the repository, approve the plan, then convert it into a mission.',
    tags: ['create', 'analyze', 'approve', 'reject'],
  },
  {
    code: 'DROID',
    title: 'Custom Droids',
    body: 'Specialized subagents with their own prompts, models and tool policies.',
    tags: ['worker', 'explorer', 'reviewer', 'validator'],
  },
  {
    code: 'SKILL',
    title: 'Skills',
    body: 'Reusable SKILL.md workflows with trigger-based auto-discovery. Matched to tasks or invoked manually.',
    tags: ['SKILL.md', 'triggers', 'invoke'],
  },
  {
    code: 'HOOK',
    title: 'Hooks',
    body: 'Event-driven lifecycle hooks for mission events. Run a script or call a webhook.',
    tags: ['PreToolUse', 'PostToolUse', 'MissionStart', 'MissionEnd', 'MilestoneComplete', 'ValidationFail'],
  },
  {
    code: 'ENV',
    title: 'Environments',
    body: 'Reusable sandbox definitions with repository, dependencies, setup commands and health checks.',
    tags: ['repository', 'setup', 'health checks'],
  },
]

const TEMPLATES = [
  ['minimal-shell', 'ubuntu:24.04', 'bash, git, curl'],
  ['python-dev', 'python:3.12-slim', 'python, pip, git, pytest'],
  ['node-dev', 'node:20-slim', 'node, npm, git'],
  ['desktop-browser', 'ubuntu:24.04', 'firefox, TightVNC, noVNC'],
]

const PERSISTENCE = [
  ['ephemeral', 'Destroyed after the task.'],
  ['persistent', 'Home volume survives restarts.'],
  ['snapshotted', 'Restore to a previous state.'],
]

export function Harness() {
  return (
    <section id="harness" aria-labelledby="harness-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="harness-title"
        index="03"
        label="Agent Harness"
        title={
          <>
            Extend everything.
            <br />
            <span className="text-muted-foreground">Fork nothing.</span>
          </>
        }
        lead="Reusable workflows, specialized subagents and event-driven automation for advanced agent development."
      />

      <ul className="mt-16 grid border-t border-l border-foreground md:mt-24 md:grid-cols-2 xl:grid-cols-5">
        {HARNESS.map((item) => (
          <li key={item.code} className="group flex flex-col border-r border-b border-foreground p-6 transition-colors hover:bg-foreground hover:text-background md:min-h-[26rem]">
            <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-wider">
              <span>{item.code}</span>
              <span className="size-2 border border-current transition-colors group-hover:border-signal group-hover:bg-signal" aria-hidden="true" />
            </div>
            <p className="mt-12 text-3xl font-semibold tracking-tight md:mt-auto">{item.title}</p>
            <p className="mt-3 text-pretty leading-snug opacity-70">{item.body}</p>
            <ul className="mt-6 flex flex-wrap gap-1.5" aria-label={`${item.title} keywords`}>
              {item.tags.map((tag) => (
                <li key={tag} className="border border-current/25 px-1.5 py-0.5 font-mono text-[10px]">
                  {tag}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>

      <div className="mt-24 grid gap-10 md:mt-32 md:grid-cols-12 md:gap-8">
        <div className="md:col-span-4">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'03.1 — Workstations'}</p>
          <h3 className="mt-4 text-balance text-4xl font-semibold leading-[0.95] tracking-[-0.04em] md:text-5xl">
            A computer for every agent.
          </h3>
          <p className="mt-5 text-pretty leading-snug text-muted-foreground">
            An isolated Linux environment with its own filesystem, shell, tools, and optionally a browser and full
            desktop. Agents build, run servers and execute tests without touching the host or each other.
          </p>
          <dl className="mt-8 border-t border-foreground">
            {PERSISTENCE.map(([mode, body]) => (
              <div key={mode} className="flex items-baseline justify-between gap-4 border-b border-border py-3">
                <dt className="font-mono text-xs">{mode}</dt>
                <dd className="text-right text-sm text-muted-foreground">{body}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="overflow-x-auto md:col-span-7 md:col-start-6">
          <table className="w-full min-w-[520px] border-collapse text-left">
            <caption className="sr-only">Built-in workstation templates</caption>
            <thead>
              <tr className="border-b border-foreground font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                <th scope="col" className="py-3 pr-4 font-normal">Template</th>
                <th scope="col" className="py-3 pr-4 font-normal">Base image</th>
                <th scope="col" className="py-3 font-normal">Tools</th>
              </tr>
            </thead>
            <tbody>
              {TEMPLATES.map(([name, image, tools]) => (
                <tr key={name} className="border-b border-border">
                  <th scope="row" className="py-5 pr-4 text-lg font-semibold tracking-tight">{name}</th>
                  <td className="py-5 pr-4 font-mono text-xs">{image}</td>
                  <td className="py-5 text-sm text-muted-foreground">{tools}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-8 grid border-t border-l border-foreground sm:grid-cols-2">
            <div className="border-r border-b border-foreground p-5">
              <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Driver / default'}</p>
              <p className="mt-6 text-lg font-semibold tracking-tight">Container</p>
              <p className="mt-1 text-sm leading-snug text-muted-foreground">
                Hardened Docker containers on an isolated network, with CPU and memory limits.
              </p>
            </div>
            <div className="border-r border-b border-foreground p-5">
              <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Driver / optional'}</p>
              <p className="mt-6 text-lg font-semibold tracking-tight">Virtual machine</p>
              <p className="mt-1 text-sm leading-snug text-muted-foreground">
                KVM via libvirt or the Proxmox API, for stronger isolation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
