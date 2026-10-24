export const VERSION = '1.14.0'
export const REPO_URL = 'https://github.com/LukaG712/Evershade'

export type ServiceTier = 'orchestrator' | 'core' | 'optional' | 'client'

export type Service = {
  id: string
  name: string
  port: string
  role: string
  stack: string
  tier: ServiceTier
}

export const SERVICES: Service[] = [
  { id: 'greenie', name: 'Greenie', port: '8080', role: 'Central orchestrator & API backend', stack: 'Python / FastAPI', tier: 'orchestrator' },
  { id: 'slinker', name: 'Slinker', port: '8000', role: 'Code execution engine', stack: 'Python / FastAPI', tier: 'core' },
  { id: 'trapper', name: 'Trapper', port: '3000', role: 'Web scraping & crawling', stack: 'TypeScript / Fastify', tier: 'core' },
  { id: 'gobber', name: 'Gobber', port: '8085', role: 'Persistent storage & knowledge graph', stack: 'Python / FastAPI', tier: 'core' },
  { id: 'shrewd', name: 'Shrewd', port: '8089', role: 'LLM provider abstraction', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'sneaker', name: 'Sneaker', port: '8086', role: 'Metrics, traces, logs', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'hider', name: 'Hider', port: '8087', role: 'Encrypted secrets management', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'poltergeist', name: 'Poltergeist', port: '8088', role: 'Notifications & async delivery', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'slammer', name: 'Slammer', port: '5173', role: 'React web dashboard', stack: 'React / TypeScript', tier: 'client' },
  { id: 'speedy', name: 'Speedy', port: 'CLI', role: 'The evershade command', stack: 'Python / Click / Rich', tier: 'client' },
]

/** Dependency edges taken from version-manifest.json. [from, to] by index into SERVICES. */
export const EDGES: [number, number][] = [
  [0, 1],
  [0, 2],
  [0, 3],
  [0, 4],
  [0, 5],
  [0, 6],
  [0, 7],
  [3, 4],
  [8, 0],
  [9, 0],
]

export const TIER_LABEL: Record<ServiceTier, string> = {
  orchestrator: 'Orchestrator',
  core: 'Core',
  optional: 'Optional',
  client: 'Interface',
}

export const MISSION_STAGES = [
  {
    name: 'Create',
    endpoint: 'POST /api/missions',
    body: 'Define a mission. Large tasks are broken down into milestones and features.',
  },
  {
    name: 'Plan',
    endpoint: 'POST /api/missions/{id}/plan',
    body: 'LLM-based planning via Shrewd, with repository intelligence and a heuristic fallback.',
  },
  {
    name: 'Execute',
    endpoint: 'POST /api/missions/{id}/execute',
    body: 'Milestones run their features with parallel workers. Logs stream live over SSE.',
  },
  {
    name: 'Validate',
    endpoint: 'POST /api/missions/{id}/validate',
    body: 'Deterministic checks (test, lint, type) plus a diff-based security review.',
  },
  {
    name: 'Fix-Revalidate',
    endpoint: 'POST /api/missions/{id}/fix-revalidate',
    body: 'Failures become fix features automatically, then re-run, with configurable retries.',
  },
  {
    name: 'Complete',
    endpoint: 'GET /api/missions/analytics',
    body: 'When every check passes, the mission completes. Duration, model usage and outcomes are recorded.',
  },
] as const

export const MISSION_CAPABILITIES = [
  ['Mission lifecycle', 'Create, plan, execute, validate, complete, cancel, pause and resume.'],
  ['Approval gates', 'Human-in-the-loop approval for sensitive operations, with three autonomy levels.'],
  ['Code review', 'Automated test, lint and type checks and a diff-based security review.'],
  ['Checkpoint recovery', 'Mission state is persisted so a mission can recover from failures.'],
  ['SSE streaming', 'Real-time mission execution logs via Server-Sent Events.'],
  ['Secret redaction', 'Pattern-based redaction of API keys, tokens and passwords in logs.'],
] as const

export const PRINCIPLES = [
  ['Modular services', 'Each service has a clear boundary and public interface.'],
  ['SQLite-first', 'SQLite where it satisfies requirements. Other databases only when necessary.'],
  ['No heavy infrastructure', 'No Kubernetes, Kafka, Elasticsearch or distributed databases without a concrete need.'],
  ['Self-hosted practical', 'Runs on ordinary developer hardware without excessive resource consumption.'],
  ['Security by default', 'Least privilege, network isolation and container hardening as the default.'],
] as const

export const PROFILES = [
  { name: 'Minimal', detail: 'Core only. 4 services', flag: '--profile minimal' },
  { name: 'Standard', detail: 'All services. 8 services', flag: '--profile standard' },
  { name: 'Full', detail: 'Standard + Slammer dashboard', flag: '--profile full' },
  { name: 'Custom', detail: 'Pick individual services', flag: '--profile custom' },
  { name: '+ Ollama', detail: 'Local LLM support', flag: '--profile ollama' },
  { name: '+ Proxy', detail: 'Caddy reverse proxy with TLS', flag: '--profile proxy' },
] as const
