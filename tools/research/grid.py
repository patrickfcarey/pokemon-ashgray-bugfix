#!/usr/bin/env python3
# grid.py out.png cols img1 img2 ...  (PIL grid montage with labels)
import sys
from PIL import Image, ImageDraw
out, cols = sys.argv[1], int(sys.argv[2])
paths = sys.argv[3:]
imgs = [Image.open(p).convert("RGB") for p in paths]
w, h = imgs[0].size
pad, lab = 4, 14
rows = (len(imgs) + cols - 1) // cols
W = cols * w + (cols + 1) * pad
H = rows * (h + lab) + (rows + 1) * pad
canvas = Image.new("RGB", (W, H), (20, 20, 20))
d = ImageDraw.Draw(canvas)
for i, im in enumerate(imgs):
    r, c = divmod(i, cols)
    x = pad + c * (w + pad)
    y = pad + r * (h + lab + pad)
    d.text((x + 2, y + 1), paths[i].split("/")[-1].replace(".png", ""), fill=(255, 255, 0))
    canvas.paste(im, (x, y + lab))
canvas.save(out)
print("wrote", out, canvas.size)
