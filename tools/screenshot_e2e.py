import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path('screenshots')
OUT.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT / 'e2e_results.png'

# Run pytest for e2e tests
cmd = [sys.executable, '-m', 'pytest', '-q', 'tests/e2e']
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
stdout, _ = proc.communicate()
exit_code = proc.returncode

# Prepare text to render
header = 'Playwright E2E Test Output\n'
status = 'PASSED' if exit_code == 0 else f'FAILED (exit {exit_code})'
text = header + status + '\n\n' + stdout

# Render to image (monospace)
font = ImageFont.load_default()
lines = text.splitlines()
# Use ImageDraw.textbbox for text measurement (works with modern Pillow)
measure_img = Image.new('RGB', (1, 1))
measure_draw = ImageDraw.Draw(measure_img)
max_width = max((measure_draw.textbbox((0, 0), line, font=font)[2]
                 for line in lines), default=0) + 20
# compute line height using a sample bbox; add small spacing
sample_bbox = measure_draw.textbbox((0, 0), lines[0] if lines else '', font=font)
line_height = (sample_bbox[3] - sample_bbox[1]) + 4
img_height = line_height * len(lines) + 20
img = Image.new('RGB', (max_width, img_height), color='white')
d = ImageDraw.Draw(img)

y = 10
for line in lines:
    d.text((10, y), line, font=font, fill=(10, 10, 10))
    y += line_height

img.save(OUT_FILE)
print(f'Saved screenshot to {OUT_FILE}')

# Exit with same code as pytest
sys.exit(exit_code)
