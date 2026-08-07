#!/usr/bin/env bash
# Rebuilds assets/ from tools/inbox/ with the crop settings we settled on.
# Run from the repo root:   bash tools/rebuild-photos.sh
#
# Why each flag is here:
#   1-lisbon      the main portrait. Zoomed in and pushed right so her face
#                 fills the circular frame instead of the kitchen.
#   2-night-out   head sits right at the top of the frame, so keep the very
#                 top (focus 0). This is the only carousel post, so it's the
#                 only one carrying a '1/2' badge.
#   4-hotel       shot sideways; rotate upright, then bias the square left
#                 and down to land on her face.
set -euo pipefail

python tools/prepare-photos.py \
  --main 1-lisbon.png \
  --zoom       1-lisbon.png=0.80 \
  --focus-x    1-lisbon.png=0.72 \
  --focus      1-lisbon.png=0.02 \
  --focus      2-night-out.png=0.0 \
  --erase-badge 2-night-out.png \
  --rotate     4-hotel.jpg=90 \
  --focus      4-hotel.jpg=0.30 \
  --focus-x    4-hotel.jpg=0.28
