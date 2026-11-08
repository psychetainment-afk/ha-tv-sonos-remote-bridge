"""Regenerate the project-owned geometric remote icon; requires Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw
image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((76, 12, 180, 244), radius=30, fill="#203448")
draw.ellipse((115, 32, 141, 58), fill="#f4f7fa")
draw.ellipse((94, 80, 162, 148), outline="#f4f7fa", width=9)
draw.ellipse((119, 105, 137, 123), fill="#f4f7fa")
for index, color in enumerate(("#ef5555", "#42bd82", "#f4ca50", "#4ba6ee")):
    x, y = 98 + (index % 2) * 40, 174 + (index // 2) * 34
    draw.ellipse((x-10, y-10, x+10, y+10), fill=color)
path = Path(__file__).resolve().parents[1] / "custom_components/tv_volume_bridge/brand/icon.png"
path.parent.mkdir(parents=True, exist_ok=True)
image.save(path)
