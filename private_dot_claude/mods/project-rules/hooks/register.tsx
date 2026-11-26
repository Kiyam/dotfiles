import type { Register } from 'claude-code'

// Generic rules for project folders: ask before commit/push, keep compute off this machine,
// remind about a status note after job submissions. Which folders and what they say live in
// ../projects.json, kept out of git; with no such file the mod does nothing.
type Project = {
  root: string
  // none: every local python/pytest/script run is blocked; quick: `python -c` checks still run.
  compute: 'none' | 'quick'
  elsewhere: string
  status?: string
}

const COMPUTE = {
  none: /^(python3?|pytest|uv\s+run|marimo|jupyter|\.?\/?\S+\.py\b|bash\s+\S+\.sh)/,
  quick: /^(pytest|python3?\s+-m\s+pytest|python3?\s+(?!-c\b)\S+\.py|uv\s+run\s+(pytest|\S+\.py))/,
}
const PY_COMPILE = /^python3?\s+-m\s+py_compile\b/
const GIT_WRITE = /^git(\s+-C\s+\S+)?\s+(commit|push)\b/
// "commit"/"push" in the last prompt, or a short yes to Claude asking for approval.
const ASKED_TO_COMMIT = /\b(commit|push)\b|^\s*(y|yes|yep|yeah|ok|okay|sure|go|go ahead|do it)\b[\s.!]*$/i
const SUBMITS = /\bsbatch\b|run_tasks\.sh|submit_\w+_chain|\bscancel\b|\bscontrol\s+(hold|release|requeue)\b/

// Split a shell line into simple commands; a segment that starts with ssh runs elsewhere.
// Quoted text is blanked first so `ssh ursula "cd x && python run.py"` stays one segment.
const segments = (cmd: string) =>
  cmd
    .replace(/"(\\.|[^"\\])*"|'[^']*'/g, 'Q')
    .split(/&&|\|\||;|\||\n/)
    .map(s => s.trim().replace(/^(\w+=\S*\s+)+/, '').replace(/^(time|nohup|exec)\s+/, ''))

let projects: Project[] = []
let lastPrompt = ''

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const home = (await $.process.run(['sh', '-c', 'printf %s "$HOME"'])).stdout
    const tilde = (path: string) => path.replace(/^~(?=\/|$)/, home)
    try {
      const raw = JSON.parse(await $.fs.read(`${$.plugin.root}/projects.json`)) as Project[]
      projects = raw.map(p => ({ ...p, root: tilde(p.root), status: p.status && tilde(p.status) }))
    } catch {
      projects = [] // no config on this machine
    }

    return next(e)
  })

  on('prompt.submit', ($, e, next) => {
    if (!e.text.startsWith('<')) lastPrompt = e.text // skip task notifications and other machine turns

    return next(e)
  })

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (projects.length === 0) return next(e)
    const cwd = await $.session.cwd()
    const project = projects.find(p => cwd === p.root || cwd.startsWith(`${p.root}/`))
    if (!project) return next(e)

    const local = segments(e.command).filter(s => s && !/^(ssh|rsync|scp)\b/.test(s))
    if (local.some(s => GIT_WRITE.test(s)) && !ASKED_TO_COMMIT.test(lastPrompt))
      return {
        deny: 'project-rules: the user reviews before every commit/push. Show `git status` and `git diff --stat`, ask for approval, and commit only after they say so.',
      }
    const heavy = local.find(s => COMPUTE[project.compute].test(s) && !PY_COMPILE.test(s))
    if (heavy) return { deny: `project-rules: ${project.elsewhere} Blocked: ${heavy}` }

    const ran = await next(e)
    if (project.status && SUBMITS.test(e.command) && !('deny' in ran && ran.deny !== undefined))
      return {
        ...ran,
        context: [...(ran.context ?? []), `Jobs changed: update ${project.status} in this same turn.`],
      }

    return ran
  }).catch(($, e, next) => (next.called ? next(e) : { deny: 'project-rules: its guard failed; check the mod.' }))
}
