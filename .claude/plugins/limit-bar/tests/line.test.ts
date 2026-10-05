import { expect, test } from 'claude-code/testing'

import { bar, line } from '../hooks/register'

test('bar has ten cells', async () => {
  expect(bar(0)).toBe('▱▱▱▱▱▱▱▱▱▱')
  expect(bar(62)).toBe('▰▰▰▰▰▰▱▱▱▱')
  expect(bar(130)).toBe('▰▰▰▰▰▰▰▰▰▰')
})

test('line shows each window with time to reset', async () => {
  const now = Date.parse('2026-10-05T12:00:00Z')
  const text = line(
    [
      { kind: 'five_hour', percentUsed: 62.5, resetsAt: '2026-10-05T14:15:00Z' },
      { kind: 'seven_day', percentUsed: 87, resetsAt: '2026-10-08T23:00:00Z' },
    ],
    now,
  )
  expect(text).toBe('🟡 5ч ▰▰▰▰▰▰▱▱▱▱ 63% ↻ 2ч 15м  │  🔴 неделя ▰▰▰▰▰▰▰▰▰▱ 87% ↻ 3д 11ч')
  expect(line([], now)).toBe('Лимит: нет данных')
})
