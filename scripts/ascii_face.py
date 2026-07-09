"""Convert a source image into a monospace ASCII/density-art grid.

Used to render the portrait in the README neofetch-style banner from a
checked-in source image (assets/ascii_face_source.png), so the art can be
regenerated deterministically instead of living only as a hardcoded blob.
"""
from PIL import Image, ImageOps

# Sparse -> dense visual weight. Darker source pixels map to denser glyphs
# so ink shows up against the dark terminal-style background.
RAMP = " .`'^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def build_ascii(source_path: str, cols: int = 58, char_aspect: float = 0.52,
                 bg_thresh: int = 245, gamma: float = 0.7) -> list[str]:
    img = Image.open(source_path).convert("RGB")
    width, height = img.size

    cell_w = width / cols
    cell_h = cell_w / char_aspect
    rows = max(1, int(height / cell_h))

    gray = ImageOps.grayscale(img)

    lines = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            x0, y0 = int(c * cell_w), int(r * cell_h)
            x1, y1 = int((c + 1) * cell_w), int((r + 1) * cell_h)
            x1, y1 = max(x1, x0 + 1), max(y1, y0 + 1)

            brightness_raw = gray.crop((x0, y0, x1, y1)).resize((1, 1)).getpixel((0, 0))

            if brightness_raw >= bg_thresh:
                row_chars.append(' ')
                continue

            brightness = (brightness_raw / 255.0) ** gamma
            idx = int((1 - brightness) * (len(RAMP) - 1))
            idx = min(max(idx, 0), len(RAMP) - 1)
            row_chars.append(RAMP[idx])
        lines.append(''.join(row_chars).rstrip())
    return lines


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "assets/ascii_face_source.png"
    for line in build_ascii(src):
        print(line)
