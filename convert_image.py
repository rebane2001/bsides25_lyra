#!/usr/bin/python3
from PIL import Image
import sys

im = Image.open(sys.argv[1]).convert("L")
pix = im.load()
width, height = im.size
assert width == 128 and height == 64
out = "import framebuf\ndata = bytearray([" 
for h in range(height):
    for w in range(width//8):
        p = 0
        for i in range(8):
            p = p << 1
            p += 1 if pix[(w*8+i,h)] > 128 else 0
        out += f"{hex(p)},"
out += "])\nfb = framebuf.FrameBuffer(data, 128, 64, framebuf.MONO_HLSB)"

with open(".".join(sys.argv[1].split(".")[:-1])+".py", "x") as f:
    f.write(out)
