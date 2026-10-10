"""Soundtrack for reel 2 (19.5 s): reuses the synth instruments from ../fsc-reel/sfx.py."""
import sys, wave, os
import numpy as np

src = open(os.path.join(os.path.dirname(__file__), '..', 'fsc-reel', 'sfx.py')).read()
head = src[:src.index('# ---------------- music bed')].replace('DUR = 39.5', 'DUR = 21.0')
exec(head)

def S(x):
    return x + 1.5 if x >= 8.0 else x   # scene 3 is 1.5 s longer


BPM = 124
beat = 60 / BPM
roots = [55.0, 43.65, 65.41, 49.0]
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
bar = 4 * beat
for b in range(int(DUR / bar) + 1):
    t0 = b * bar; k = b % 4
    add(mus, t0, pad(chords[k], bar + 0.3), 0.10)
    for q in range(4):
        tb = t0 + q * beat
        if tb >= DUR - 0.05 or 16.1 <= tb < 16.5:
            continue
        add(mus, tb, kick(), 0.5)
        add(mus, tb + beat / 2, hat(), 0.10, pan=0.3)
        add(mus, tb + beat / 2, bass_note(roots[k], beat / 2 - 0.02), 0.30)
        add(mus, tb, bass_note(roots[k] * (2 if q == 3 else 1), beat / 2 - 0.02), 0.22)

# hook
add(fx, 0.00, sub_drop(), 0.9); add(fx, 0.00, air_hiss(1.0), 0.3, pan=-0.2)
add(fx, 0.10, tick(), 0.3); add(fx, 0.22, tick(), 0.3)
add(fx, 1.00, whoosh(0.35, 400, 5000), 0.35); add(fx, 1.05, thump(), 0.6)
for k in range(10): add(fx, 1.0 + k * 0.12, tick(), 0.12)
add(fx, 2.25, pop(0.15, 400, 1400), 0.5)
for c in (2.5, 5.0, 9.5, 14.0, 16.5): add(fx, c - 0.22, whoosh(0.42, rise=True), 0.55)
# 2 positive
add(fx, 2.5, thump(), 0.7)
for i in range(3):
    add(fx, 3.15 + i * 0.22, pop(0.1, 600, 1300), 0.35, pan=(i - 1) * 0.4)
    add(fx, 3.75 + i * 0.25, ding(0.7, 1318.5 + i * 220), 0.28, pan=(i - 1) * 0.4)
# 3 solution: 3D warehouse assembles, trucks reverse in, labels pop
add(fx, 5.0, impact(0.9), 0.5)
add(fx, 5.35, whoosh(0.5, 300, 3000, rise=True), 0.25)
for i in range(5): add(fx, 5.55 + i * 0.13, thump(0.25), 0.28 + 0.05 * i, pan=(i - 2) * 0.25)
for i in range(5): add(fx, 5.6 + i * 0.13, click(0.05, 1800 + i * 160), 0.3)
add(fx, 6.0, rumble(2.4), 0.26)
for i in range(6): add(fx, 6.1 + i * 0.4, tick(0.03), 0.2)
add(fx, 6.6, pop(0.14, 500, 1400), 0.5)
add(fx, 6.65, ding(0.8, 1568), 0.3)
add(fx, 8.35, thump(0.3), 0.3, pan=-0.3); add(fx, 8.85, thump(0.3), 0.3, pan=0.3)
for i in range(4): add(fx, 7.7 + i * 0.18, pop(0.09, 500 + i * 120, 1100 + i * 120), 0.3, pan=(i - 1.5) * 0.3)
# 4 numbers
add(fx, S(8.0), thump(), 0.85)
for i in range(4): add(fx, S(8.45 + i * 0.18), click(), 0.45, pan=(i - 1.5) * 0.3)
for k in range(24): add(fx, S(8.7 + k * 0.07), tick(), 0.14)
for i in range(8): add(fx, S(9.1 + i * 0.12), pop(0.06, 900 + i * 60, 1200 + i * 60), 0.15)
add(fx, S(10.6), ding(0.9, 1568), 0.3); add(fx, S(11.1), pop(), 0.35)
# 5 who
add(fx, S(12.5), thump(), 0.7)
for i in range(4): add(fx, S(12.8 + i * 0.17), whoosh(0.2, 800, 5000), 0.2); add(fx, S(13.0 + i * 0.17), click(0.05, 2200 + i * 200), 0.4)
# 6 CTA
add(fx, S(15.0), click(0.08, 1800), 0.8)
for i in range(6): add(fx, S(15.45 + i * 0.07), click(0.04, 2600 + i * 180), 0.35, pan=(i - 2.5) * 0.15)
add(fx, S(16.55), impact(1.2), 0.75)
add(fx, S(17.20), pop(), 0.4); add(fx, S(17.55), ding(1.0, 1318.5), 0.35); add(fx, S(17.6), shimmer(1.8), 0.4)

def norm(x, peak): return x / (np.max(np.abs(x)) + 1e-9) * peak
mus = norm(mus, 0.42)
fade = np.ones(N); nf = int(1.2 * SR); fade[-nf:] = np.linspace(1, 0, nf); mus *= fade[:, None]
fx = norm(fx, 0.85)
mix = np.tanh((mus + fx) * 1.15) * 0.92
out = sys.argv[1] if len(sys.argv) > 1 else 'soundtrack2.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
