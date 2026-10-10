"""Soundtrack for the intro (4 bars @124 BPM = 7.742 s) so the beat flows straight into reel 2."""
import sys, wave, os
import numpy as np

src = open(os.path.join(os.path.dirname(__file__), '..', 'fsc-reel', 'sfx.py')).read()
head = src[:src.index('# ---------------- music bed')].replace('DUR = 39.5', 'DUR = 7.742')
exec(head)

BPM = 124
beat = 60 / BPM
roots = [55.0, 43.65, 65.41, 49.0]
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
bar = 4 * beat
for b in range(4):
    t0 = b * bar; k = b % 4
    add(mus, t0, pad(chords[k], bar + 0.3), 0.10)
    for q in range(4):
        tb = t0 + q * beat
        if tb >= DUR - 0.05:
            continue
        add(mus, tb, kick(), 0.5)
        add(mus, tb + beat / 2, hat(), 0.10, pan=0.3)
        add(mus, tb + beat / 2, bass_note(roots[k], beat / 2 - 0.02), 0.30)
        add(mus, tb, bass_note(roots[k] * (2 if q == 3 else 1), beat / 2 - 0.02), 0.22)

# A: who are you
add(fx, 0.00, sub_drop(), 0.9); add(fx, 0.00, air_hiss(0.9), 0.3, pan=-0.2)
add(fx, 0.10, tick(), 0.3); add(fx, 0.25, tick(), 0.3)
add(fx, 0.62, pop(0.12, 500, 1200), 0.5, pan=-0.4); add(fx, 0.88, pop(0.12, 600, 1400), 0.5, pan=0.4)
add(fx, 1.35, ding(0.9, 1568), 0.35, pan=0.4)
# cut A -> B
add(fx, 2.38, whoosh(0.42, rise=True), 0.55); add(fx, 2.6, thump(), 0.85)
# B: harvest
add(fx, 2.65, rumble(2.4), 0.30)
for i in range(4): add(fx, 3.7 + i * 0.18, pop(0.09, 500 + i * 110, 1000 + i * 110), 0.3, pan=(i - 1.5) * 0.3)
for k in range(8): add(fx, 3.0 + k * 0.32, wood(), 0.28, pan=(k % 3 - 1) * 0.5)
# cut B -> C
add(fx, 4.98, whoosh(0.42, rise=True), 0.55); add(fx, 5.2, thump(), 0.85)
# C: question
for i in range(3): add(fx, 5.95 + i * 0.2, click(0.05, 2200 + i * 240), 0.5, pan=(i - 1) * 0.3); add(fx, 5.97 + i * 0.2, whoosh(0.2, 800, 5000), 0.2)
for k in range(3): add(fx, 5.95 + k * 0.28, tick(), 0.25)
add(fx, 6.95, impact(1.0), 0.7); add(fx, 7.0, shimmer(0.8), 0.3)
# lead-out into reel 2
add(fx, 7.5, whoosh(0.3, 500, 6000, rise=True), 0.4)

def norm(x, peak): return x / (np.max(np.abs(x)) + 1e-9) * peak
mus = norm(mus, 0.42); fx = norm(fx, 0.85)
mix = np.tanh((mus + fx) * 1.15) * 0.92
out = sys.argv[1] if len(sys.argv) > 1 else 'sound_intro.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
