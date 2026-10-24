'use client'

import { useState } from 'react'
import { Check, Copy } from 'lucide-react'
import { PROFILES } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const COMMANDS = [
  { comment: '# clone', cmd: 'git clone https://github.com/LukaG712/Evershade.git && cd Evershade' },
  { comment: '# install service repositories', cmd: './install.sh --profile minimal' },
  { comment: '# configure', cmd: 'cp .env.example .env' },
  { comment: '# start', cmd: './start.sh --profile minimal' },
]

const STEPS = [
  ['Install and start', 'Run the quick start. The API comes up at localhost:8080.'],
  ['Create an agent', 'Dashboard → Agents → Create Agent. For example: researcher, runner junie.'],
  ['Run a task', 'Open Chat, select your agent and type a prompt.'],
]

export function Install() {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    await navigator.clipboard.writeText(COMMANDS.map((c) => c.cmd).join('\n'))
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }

  return (
    <section id="install" aria-labelledby="install-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="install-title"
        index="05"
        label="Install"
        title={
          <>
            If it runs Docker,
            <br />
            <span className="text-muted-foreground">it runs Evershade.</span>
          </>
        }
        lead="Shell scripts for Linux, macOS and Windows PowerShell, plus visual step-by-step GUI installers for Ubuntu Desktop and Windows."
      />

      <div className="mt-16 grid gap-10 md:mt-24 md:grid-cols-12 md:gap-8">
        <div className="md:col-span-7">
          <div className="border border-foreground">
            <div className="flex items-center justify-between border-b border-foreground px-4 py-2.5">
              <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'quickstart.sh'}</span>
              <button
                type="button"
                onClick={copy}
                className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider transition-colors hover:text-signal-ink"
              >
                {copied ? <Check className="size-3.5 text-signal-ink" aria-hidden="true" /> : <Copy className="size-3.5" aria-hidden="true" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <pre className="overflow-x-auto p-5 font-mono text-[13px] leading-relaxed md:p-6">
              <code>
                {COMMANDS.map((c) => (
                  <span key={c.cmd} className="block">
                    <span className="text-muted-foreground">{c.comment}</span>
                    {'\n'}
                    <span className="text-signal-ink">{'$ '}</span>
                    {c.cmd}
                    {'\n\n'}
                  </span>
                ))}
              </code>
            </pre>
          </div>
          <ol className="mt-8 grid border-t border-l border-foreground sm:grid-cols-3">
            {STEPS.map(([title, body], i) => (
              <li key={title} className="border-r border-b border-foreground p-5">
                <p className="font-mono text-[11px] text-muted-foreground">{`Step ${i + 1}`}</p>
                <p className="mt-6 font-semibold tracking-tight">{title}</p>
                <p className="mt-1 text-sm leading-snug text-muted-foreground">{body}</p>
              </li>
            ))}
          </ol>
        </div>

        <div className="md:col-span-4 md:col-start-9">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'05.1 — Profiles'}</p>
          <ul className="mt-6 border-t border-foreground">
            {PROFILES.map((profile) => (
              <li key={profile.name} className="border-b border-border py-4">
                <div className="flex items-baseline justify-between gap-4">
                  <p className="text-xl font-semibold tracking-tight">{profile.name}</p>
                  <p className="text-right text-sm text-muted-foreground">{profile.detail}</p>
                </div>
                <code className="mt-1 block font-mono text-[11px] text-muted-foreground">{profile.flag}</code>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
