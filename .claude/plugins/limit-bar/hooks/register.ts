import type { Register, SessionRateLimit } from 'claude-code'

const LABELS: Record<string, string> = {
  five_hour: '5ч',
  seven_day: 'неделя',
  spend_limit: 'бюджет',
}

export function bar(percent: number): string {
  const filled = Math.max(0, Math.min(10, Math.round(percent / 10)))
  return '▰'.repeat(filled) + '▱'.repeat(10 - filled)
}

export function untilReset(resetsAt: string | undefined, now: number): string {
  if (!resetsAt) return ''
  const left = Math.max(0, Math.floor((Date.parse(resetsAt) - now) / 1000))
  const d = Math.floor(left / 86400)
  const h = Math.floor((left % 86400) / 3600)
  const m = Math.floor((left % 3600) / 60)
  if (d > 0) return ` ↻ ${d}д ${h}ч`
  if (h > 0) return ` ↻ ${h}ч ${m}м`
  return ` ↻ ${m}м`
}

export function line(limits: SessionRateLimit[], now: number): string {
  if (limits.length === 0) return 'Лимит: нет данных'
  return limits
    .map(l => {
      const mark = l.percentUsed >= 80 ? '🔴' : l.percentUsed >= 50 ? '🟡' : '🟢'
      const label = LABELS[l.kind] ?? l.kind
      return `${mark} ${label} ${bar(l.percentUsed)} ${Math.round(l.percentUsed)}%${untilReset(l.resetsAt, now)}`
    })
    .join('  │  ')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    const usage = await $.session.usage()
    $.ui.status(line(usage.rateLimits, await $.clock.now()))
    return result
  })

  on('session.measure', async ($, e, next) => {
    $.ui.status(line(e.rateLimits, await $.clock.now()))
    return next(e)
  })
}
