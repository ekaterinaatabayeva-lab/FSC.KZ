"""Cut the drone reveal out of the source reel and paint out the burned-in captions.

usage: clean_drone.py <source.mp4> <out_dir>
Writes <out_dir>/clean.mp4 (1.77 s, 720x1280, no text).
"""
import subprocess, sys, os, glob
import cv2, numpy as np

src, out = sys.argv[1], sys.argv[2]
T0, T1 = 8.30, 10.02
raw = os.path.join(out, "raw"); os.makedirs(raw, exist_ok=True)
for f in glob.glob(raw + "/*"): os.remove(f)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(T0), "-t", str(T1 - T0), "-i", src,
                "-vf", "fps=30", raw + "/%04d.png"], check=True)
clean = os.path.join(out, "clean"); os.makedirs(clean, exist_ok=True)
for f in glob.glob(clean + "/*"): os.remove(f)

BANDS = [(170, 330), (780, 890)]          # y-ranges where the captions live
for p in sorted(glob.glob(raw + "/*.png")):
    im = cv2.imread(p)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.int16)
    med = cv2.medianBlur(g.astype(np.uint8), 31).astype(np.int16)
    d = g - med
    top = (d > 9) & (g > 120)                  # smooth sky: catch even half-faded text
    bot = (d > 22) & (g > 205)                 # bright wall: only the pure-white strokes
    mt = np.zeros(g.shape, np.uint8); mb = np.zeros(g.shape, np.uint8)
    mt[BANDS[0][0]:BANDS[0][1]] = top[BANDS[0][0]:BANDS[0][1]].astype(np.uint8) * 255
    mb[BANDS[1][0]:BANDS[1][1]] = bot[BANDS[1][0]:BANDS[1][1]].astype(np.uint8) * 255
    mt = cv2.dilate(mt, np.ones((5, 5), np.uint8), iterations=2)
    # on the wall grow only into bright pixels so dark girders are never smeared
    wall = (cv2.blur(med.astype(np.float32), (41, 41)) > 140).astype(np.uint8) * 255
    mb_big = cv2.dilate(mb, np.ones((5, 5), np.uint8), iterations=2)
    mb_small = cv2.dilate(mb, np.ones((3, 3), np.uint8), iterations=2) & ((g > 170).astype(np.uint8) * 255)
    mb = np.where(wall > 0, mb_small, mb_big).astype(np.uint8)
    res = cv2.inpaint(im, mt | mb, 3, cv2.INPAINT_TELEA)
    cv2.imwrite(os.path.join(clean, os.path.basename(p)), res)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", clean + "/%04d.png",
                "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", os.path.join(out, "clean.mp4")], check=True)
print("frames:", len(os.listdir(clean)))
