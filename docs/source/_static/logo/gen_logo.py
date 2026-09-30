# /// script
# requires-python = ">=3.10"
# dependencies = ["uharfbuzz", "fonttools"]
# ///
"""Generate the PyCFAST logo and icon (SVG) this has been AI-generated.

Requires the Inter variable font (https://rsms.me/inter/, OFL). From this directory:

    uv run gen_logo.py Inter.ttf 600
"""
import sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

INK_LIGHT = "#222832"
INK_DARK = "#E6E9EF"
ACCENT = "#EA580C"

def wordmark(font_file, text, wght, size, x0, cy):
    """Return (svg path d, right edge) for `text`, vertically centred on cy by cap height."""
    f = TTFont(font_file)
    axes = {a.axisTag: wght if a.axisTag == "wght" else a.defaultValue for a in f["fvar"].axes}
    if "opsz" in axes:
        axes["opsz"] = 32
    fi = instancer.instantiateVariableFont(f, axes)
    upm = fi["head"].unitsPerEm
    cap = fi["OS/2"].sCapHeight
    scale = size / upm
    baseline = cy + cap * scale / 2
    glyphset = fi.getGlyphSet()
    order = fi.getGlyphOrder()

    blob = hb.Blob.from_file_path(font_file)
    font = hb.Font(hb.Face(blob))
    font.set_variations(axes)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})

    x = 0
    parts = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(glyphset)
        tpen = TransformPen(pen, (scale, 0, 0, -scale, x0 + (x + pos.x_offset) * scale, baseline - pos.y_offset * scale))
        glyphset[order[info.codepoint]].draw(tpen)
        parts.append(pen.getCommands())
        x += pos.x_advance
    return " ".join(parts), x0 + x * scale

# Flame: base centred at (0,0), pointing up, height 24, width ~22
FLAME = [("M", [(3, -25)]),
         ("C", [(9, -18), (11.5, -12), (11.5, -7)]),
         ("C", [(11.5, -2.5), (6.5, 1), (0, 1)]),
         ("C", [(-6.5, 1), (-11.5, -2.5), (-11.5, -7)]),
         ("C", [(-11.5, -11), (-10.5, -14), (-8.5, -16.5)]),
         ("C", [(-7.5, -15), (-6, -11), (-3.5, -11)]),
         ("C", [(-1, -11), (-0.5, -18), (3, -25)]),
         ("Z", [])]

def flame(cx, base_y, h):
    s = h / 26.0
    out = []
    for cmd, pts in FLAME:
        out.append(cmd + " " + " ".join(f"{cx + px*s:.2f} {base_y + (py - 1)*s:.2f}" for px, py in pts))
    return " ".join(out)

WAVE = "M0 0 H48 V19.5 C38 13.5 30 25.5 20 19.5 S6 14 0 19.5 Z"  # hot upper layer, wavy interface

def mark(ink):
    """Solid tile with a hot upper layer, flame knocked out."""
    return f'''<defs><clipPath id="c"><rect width="48" height="48" rx="10"/></clipPath>
<mask id="m"><rect width="48" height="48" fill="#fff"/><path d="{flame(24, 41, 25)}" fill="#000"/></mask></defs>
<g mask="url(#m)" clip-path="url(#c)"><rect width="48" height="48" fill="{ink}"/><path d="{WAVE}" fill="{ACCENT}"/></g>'''

def logo(ink, font, wght):
    d, right = wordmark(font, "PyCFAST", wght, 36, 62, 24)
    w = round(right + 2, 1)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 48" width="{w}" height="48" role="img" aria-label="PyCFAST">
{mark(ink)}
<path d="{d}" fill="{ink}"/>
</svg>
'''

def icon(ink):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" role="img" aria-label="PyCFAST">
{mark(ink)}
</svg>
'''

if __name__ == "__main__":
    font = sys.argv[1] if len(sys.argv) > 1 else "Inter.ttf"
    wght = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    open("pycfast-logo.svg", "w").write(logo(INK_LIGHT, font, wght))
    open("pycfast-logo-dark.svg", "w").write(logo(INK_DARK, font, wght))
    open("pycfast-icon.svg", "w").write(icon(INK_LIGHT))
    print("ok")
