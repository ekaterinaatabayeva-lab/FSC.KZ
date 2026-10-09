"""Synthesises the reel soundtrack (music bed + SFX synced to index.html) -> soundtrack.wav.

Pure numpy, no samples. Event times mirror the animation timings in index.html.
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 39.5
SH = 3.5  # new overview scene inserted at 4.0 s


def S(x):
    return x + SH if x >= 4 else x

N = int(SR * DUR)
rng = np.random.default_rng(7)

mus = np.zeros((N, 2))
fx = np.zeros((N, 2))


def t_arr(d):
    return np.arange(int(SR * d)) / SR


def band(x, lo, hi):
    """FFT band-pass (zero phase)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def env(d, a=0.005, r=None, curve=4.0):
    n = int(SR * d)
    e = np.ones(n)
    na = max(1, int(SR * a))
    e[:na] = np.linspace(0, 1, na)
    tail = np.linspace(1, 0, n - na) ** curve if r is None else np.exp(-np.arange(n - na) / (SR * r))
    e[na:] = tail
    return e


def add(buf, start, sig, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414


# ---------------- instruments ----------------
def kick(d=0.45, f0=120, f1=42):
    t = t_arr(d)
    f = f1 + (f0 - f1) * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(d, 0.002, r=0.12) + 0.3 * band(rng.standard_normal(len(t)), 1500, 6000) * env(d, 0.001, r=0.004)


def hat(d=0.08, open_=False):
    t = t_arr(d if not open_ else 0.25)
    return band(rng.standard_normal(len(t)), 7000, 15000) * env(len(t) / SR, 0.001, r=0.012 if not open_ else 0.06)


def bass_note(freq, d):
    t = t_arr(d)
    saw = 2 * ((t * freq) % 1) - 1
    s = 0.6 * np.sin(2 * np.pi * freq * t) + 0.4 * band(saw, 20, 600)
    return s * env(d, 0.01, curve=1.6)


def pad(freqs, d):
    t = t_arr(d)
    s = sum(np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) +
            0.5 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return s * e / len(freqs)


def sub_drop(d=1.6):
    t = t_arr(d)
    f = 30 + 70 * np.exp(-t * 3)
    return np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(d, 0.003, r=0.55)


def whoosh(d=0.45, lo=300, hi=6000, rise=True):
    n = int(SR * d)
    x = rng.standard_normal(n)
    parts = 8
    out = np.zeros(n)
    seg = n // parts
    for k in range(parts):  # time-varying band via crossfaded bands
        c = k / (parts - 1)
        c = c if rise else 1 - c
        flo = lo * (hi / lo) ** (c * 0.7)
        fhi = flo * 3
        b = band(x, flo, fhi)
        w = np.zeros(n)
        a0, a1 = max(0, (k - 1) * seg), min(n, (k + 2) * seg)
        w[a0:a1] = np.hanning(a1 - a0)
        out += b * w
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return out * e


def air_hiss(d=1.0):
    n = int(SR * d)
    return band(rng.standard_normal(n), 2500, 12000) * env(d, 0.02, r=0.3)


def thump(d=0.35):
    return kick(d, 90, 38) * 1.2


def wood(d=0.18):
    t = t_arr(d)
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(180, 30), (410, 45), (920, 70)])
    return (s + 0.4 * band(rng.standard_normal(len(t)), 800, 4000) * np.exp(-t * 80)) * 0.6


def click(d=0.05, f=2400):
    t = t_arr(d)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + 0.5 * band(rng.standard_normal(len(t)), 3000, 12000) * np.exp(-t * 400))


def tick(d=0.03):
    t = t_arr(d)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 300)


def metal(d=0.5, base=520):
    t = t_arr(d)
    s = sum(np.sin(2 * np.pi * base * m * t) * np.exp(-t * (8 + 4 * m)) for m in (1, 2.76, 5.4, 8.93))
    return s * 0.35


def pop(d=0.12, f0=500, f1=1100):
    t = t_arr(d)
    f = f0 + (f1 - f0) * (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.002, r=0.03)


def bloop(d=0.35):
    t = t_arr(d)
    f = 300 + 900 * (1 - np.exp(-t * 25))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.003, r=0.07)


def ding(d=0.9, f=1318.5):
    t = t_arr(d)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)) * env(d, 0.003, r=0.25)


def turbine(d=1.6):
    t = t_arr(d)
    f = 60 + 140 * (t / d) ** 0.6
    ph = 2 * np.pi * np.cumsum(f) / SR
    blade = np.sign(np.sin(ph * 6)) * 0.25 + np.sin(ph)
    air = band(rng.standard_normal(len(t)), 400, 3000) * (t / d)
    e = np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.4)
    return (band(blade, 30, 900) * 0.7 + air * 0.6) * e


def rumble(d=2.2):
    t = t_arr(d)
    ph = 2 * np.pi * np.cumsum(45 + 6 * np.sin(2 * np.pi * 3 * t)) / SR
    s = np.tanh(2 * np.sin(ph)) + 0.4 * band(rng.standard_normal(len(t)), 40, 300)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.6)
    return s * e


def impact(d=1.4):
    return 0.9 * sub_drop(d) + 0.5 * band(rng.standard_normal(int(SR * d)), 200, 5000) * env(d, 0.001, r=0.08)


def shimmer(d=2.4):
    t = t_arr(d)
    s = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate([1760, 2217, 2637, 3520]))
    return s * env(d, 0.2, r=0.7) * 0.25


# ---------------- music bed: 120 bpm, Am - F - C - G ----------------
BPM = 120
beat = 60 / BPM
roots = [55.0, 43.65, 65.41, 49.0]  # A1 F1 C2 G1
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
bar = 4 * beat
for b in range(int(DUR / bar) + 1):
    t0 = b * bar
    k = b % 4
    if t0 < DUR:
        add(mus, t0, pad(chords[k], bar + 0.3), 0.10)
    for q in range(4):
        tb = t0 + q * beat
        if tb >= DUR - 0.05:
            continue
        if 34.5 <= tb < 35.4:  # breath before the logo
            continue
        add(mus, tb, kick(), 0.55)
        add(mus, tb + beat / 2, hat(), 0.10, pan=0.3)
        add(mus, tb + beat / 2, bass_note(roots[k], beat / 2 - 0.02), 0.30)
        add(mus, tb, bass_note(roots[k] * (2 if q == 3 else 1), beat / 2 - 0.02), 0.22)
        if q in (1, 3):
            add(mus, tb, hat(open_=True), 0.05, pan=-0.3)

# ---------------- SFX timeline ----------------
add(fx, S(0.00), sub_drop(), 0.9)
add(fx, S(0.00), air_hiss(1.1), 0.35, pan=-0.2)
for i in range(3):  # crate landings
    add(fx, S(0.35 + i * 0.22 + 0.20), wood(), 0.7, pan=(i - 1) * 0.5)
add(fx, S(2.10), pop(), 0.45)
for k in range(10):
    add(fx, S(2.3 + k * 0.1), tick(), 0.25)

CUTS = [4, 7.5, 12.5, 18.5, 23.5, 28.5, 34.5]
for c in CUTS:
    add(fx, c - 0.22, whoosh(0.42, rise=True), 0.55)

add(fx, 4.00, impact(1.0), 0.55)
add(fx, 4.05, shimmer(2.2), 0.45)
for i in range(3):
    add(fx, 5.0 + i * 0.18, pop(0.1, 600 + i * 150, 1300 + i * 150), 0.35, pan=(i - 1) * 0.4)
for k in range(12):
    add(fx, 5.0 + k * 0.1, tick(), 0.15)
add(fx, S(4.00), thump(), 0.9)
add(fx, S(4.05), turbine(1.8), 0.35)
for i in range(3):
    add(fx, S(4.15 + i * 0.1), metal(0.4, 480 + i * 90), 0.35, pan=(i - 1) * 0.4)
add(fx, S(4.55), whoosh(0.5, 200, 3000, rise=False), 0.25)
for i in range(3):
    add(fx, S(5.3 + i * 0.15), pop(0.1, 600, 1300), 0.3)

for tt in (9.9, 11.4, 13.2):  # panel taps
    add(fx, S(tt), click(), 0.6)
    for k in range(5):
        add(fx, S(tt + 0.06 + k * 0.09), tick(), 0.18)

add(fx, S(16.40), bloop(), 0.55)
add(fx, S(17.90), pop(), 0.45, pan=-0.3)
add(fx, S(18.25), pop(0.12, 600, 1300), 0.45, pan=0.3)

add(fx, S(20.05), whoosh(0.5, 300, 4000, rise=False), 0.3)
add(fx, S(22.20), ding(), 0.35)
add(fx, S(22.32), ding(0.9, 1975.5), 0.25)
add(fx, S(22.70), pop(), 0.4, pan=0.4)

add(fx, S(25.55), rumble(2.4), 0.35)
for k in range(18):
    add(fx, S(26.8 + k * 0.1), tick(), 0.18)
for tt in (27.6, 28.1, 28.6):
    add(fx, S(tt), pop(0.1, 700, 1400), 0.35, pan=0.4)

add(fx, S(31.00), click(0.08, 1800), 0.8)
for i in range(6):
    add(fx, S(31.5 + i * 0.08), click(0.04, 2600 + i * 180), 0.35, pan=(i - 2.5) * 0.15)
add(fx, S(32.30), impact(), 0.8)
add(fx, S(33.10), pop(), 0.4)
add(fx, S(33.60), shimmer(), 0.5)


# ---------------- mix ----------------
def norm(x, peak):
    return x / (np.max(np.abs(x)) + 1e-9) * peak


mus = norm(mus, 0.42)
# fade music out over the last 1.5 s
fade = np.ones(N)
nf = int(1.5 * SR)
fade[-nf:] = np.linspace(1, 0, nf)
mus *= fade[:, None]
fx = norm(fx, 0.85)
mix = np.tanh((mus + fx) * 1.15) * 0.92

out = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", out)
