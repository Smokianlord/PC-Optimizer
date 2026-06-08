from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out = Path(__file__).resolve().parent / 'app_icon.ico'
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Background rounded square
for i in range(18):
    alpha = max(25, 120 - i * 5)
    d.rounded_rectangle((18 + i, 22 + i, size - 14 + i // 3, size - 10 + i // 3), radius=48, fill=(0, 0, 0, alpha))

d.rounded_rectangle((24, 18, 232, 226), radius=46, fill=(13, 33, 68, 255), outline=(96, 165, 250, 255), width=4)
d.rounded_rectangle((38, 32, 218, 212), radius=34, fill=(30, 64, 175, 255))

# 3D button/gauge symbol
d.rounded_rectangle((58, 152, 198, 190), radius=18, fill=(5, 15, 35, 255))
d.rounded_rectangle((58, 142, 198, 180), radius=18, fill=(34, 197, 94, 255), outline=(187, 247, 208, 255), width=3)

# Gear-like ring
cx, cy = 128, 100
for angle in range(0, 360, 45):
    import math
    rad = math.radians(angle)
    x = cx + math.cos(rad) * 54
    y = cy + math.sin(rad) * 54
    d.rounded_rectangle((x - 8, y - 16, x + 8, y + 16), radius=4, fill=(191, 219, 254, 255))

d.ellipse((74, 46, 182, 154), fill=(219, 234, 254, 255), outline=(30, 64, 175, 255), width=5)
d.ellipse((100, 72, 156, 128), fill=(37, 99, 235, 255))

# Lightning bolt
d.polygon([(132, 54), (104, 108), (128, 108), (116, 148), (154, 90), (132, 90)], fill=(250, 204, 21, 255))

# Text mark
try:
    font = ImageFont.truetype('DejaVuSans-Bold.ttf', 28)
except Exception:
    font = ImageFont.load_default()
d.text((89, 154), 'PC', fill=(255, 255, 255, 255), font=font)

sizes = [(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)]
img.save(out, format='ICO', sizes=sizes)
print(out)
