"""Render a plain, font-independent P favicon. Optional: Pillow + fonttools."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

parser = argparse.ArgumentParser()
parser.add_argument('--font', default='C:/Windows/Fonts/georgia.ttf')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
font_path = Path(args.font)
tt = TTFont(font_path)
glyphs = tt.getGlyphSet()
glyph = glyphs[tt.getBestCmap()[ord('P')]]
pen = SVGPathPen(glyphs)
glyph.draw(pen)
from fontTools.pens.boundsPen import BoundsPen
bounds = BoundsPen(glyphs)
glyph.draw(bounds)
x0, y0, x1, y1 = bounds.bounds
scale = 46 / (y1 - y0)
tx = (64 - (x1 - x0) * scale) / 2 - x0 * scale
ty = 55 + y0 * scale
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#fff"/><path d="{pen.getCommands()}" transform="translate({tx:.4f} {ty:.4f}) scale({scale:.6f} {-scale:.6f})" fill="#222"/></svg>\n'
(root / 'assets/images/favicon-p.svg').write_text(svg, encoding='utf-8')
image = Image.new('RGB', (256, 256), 'white')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(str(font_path), 255)
bbox = draw.textbbox((0,0), 'P', font=font)
factor = 184 / (bbox[3]-bbox[1])
font = ImageFont.truetype(str(font_path), round(255*factor))
bbox = draw.textbbox((0,0), 'P', font=font)
draw.text(((256-(bbox[2]-bbox[0]))/2-bbox[0],36-bbox[1]), 'P',font=font,fill='#222')
image.save(root/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
print('Generated serif P SVG and multi-resolution ICO.')
