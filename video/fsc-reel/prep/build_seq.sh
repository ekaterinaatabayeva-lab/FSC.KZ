#!/bin/sh
# bg/drone_clean.mp4 (text-free drone reveal) -> reversed push-in, slowed to 3.5 s, as a JPEG sequence
set -e
cd "$(dirname "$0")/.."
rm -rf bg/drone_seq && mkdir -p bg/drone_seq
ffmpeg -v error -y -i bg/drone_clean.mp4 \
  -vf "reverse,setpts=2.05*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,fps=30" \
  -frames:v 105 -q:v 2 bg/drone_seq/%04d.jpg
ls bg/drone_seq | wc -l
