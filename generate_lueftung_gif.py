#!/usr/bin/env python3
"""Create an animated GIF comparing tilted-window and wide-open ventilation.

Install Pillow with `python -m pip install pillow`, then run:
    python generate_lueftung_gif.py
The GIF is written to lueftung-vergleich.gif in this script's directory.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 570
FRAMES, DURATION = 40, 90
BG = (11, 18, 32)
PANEL = (19, 30, 48)
ROOM = (20, 38, 58)
WALL = (41, 59, 79)
TEXT = (239, 246, 255)
MUTED = (164, 183, 205)
CYAN = (82, 214, 242)
ORANGE = (255, 171, 99)


def load_font(size, bold=False):
    candidates = (
        ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/Library/Fonts/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf']
        if bold else
        ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/Library/Fonts/Arial.ttf', 'C:/Windows/Fonts/arial.ttf']
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT_TITLE = load_font(31, True)
FONT_HEAD = load_font(21, True)
FONT_BODY = load_font(15)
FONT_SMALL = load_font(13)


def cubic(a, b, c, d, t):
    u = 1 - t
    return (u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*d[0],
            u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*d[1])


def draw_arrow(draw, x, y, color, direction=1):
    draw.line((x-8, y, x+7, y), fill=color, width=2)
    if direction > 0:
        draw.polygon([(x+7,y),(x+1,y-4),(x+1,y+4)], fill=color)
    else:
        draw.polygon([(x-8,y),(x-2,y-4),(x-2,y+4)], fill=color)


def draw_panel(image, x0, title, wide, frame):
    d = ImageDraw.Draw(image)
    panel_w, panel_h = 470, 450
    d.rounded_rectangle((x0, 94, x0+panel_w, 94+panel_h), radius=18, fill=PANEL, outline=(43,59,80), width=2)
    d.text((x0+22, 111), title, font=FONT_HEAD, fill=TEXT)
    badge = 'GROSSE ÖFFNUNG' if wide else 'KLEINE ÖFFNUNG'
    badge_box = d.textbbox((0,0), badge, font=FONT_SMALL)
    badge_w = badge_box[2] + 18
    d.rounded_rectangle((x0+panel_w-badge_w-18, 112, x0+panel_w-18, 137), radius=12, fill=(31,47,67), outline=(62,82,106))
    d.text((x0+panel_w-badge_w-9, 117), badge, font=FONT_SMALL, fill=MUTED)

    rx, ry, rw, rh = x0+96, 182, 328, 264
    d.rectangle((rx, ry, rx+rw, ry+rh), fill=ROOM, outline=WALL, width=10)
    # Opening and window frame on the left wall.
    opening_h = 105 if wide else 48
    oy = ry + (rh-opening_h)//2
    d.rectangle((rx-6, oy-5, rx+8, oy+opening_h+5), fill=PANEL)
    d.line((rx-3, oy-5, rx+11, oy-5), fill=(127,151,174), width=3)
    d.line((rx-3, oy+opening_h+5, rx+11, oy+opening_h+5), fill=(127,151,174), width=3)
    if wide:
        d.line((rx+2, oy, rx-18, oy-11), fill=(159,180,199), width=3)
        d.line((rx+2, oy+opening_h, rx-18, oy+opening_h+11), fill=(159,180,199), width=3)
    else:
        d.line((rx+4, oy+opening_h, rx-15, oy+7), fill=(159,180,199), width=3)
    d.text((rx+rw//2-24, ry+28), 'RAUM', font=FONT_SMALL, fill=MUTED)
    d.text((x0+15, oy+opening_h//2-8), 'AUSSEN', font=FONT_SMALL, fill=MUTED)
    # Simple sofa silhouette.
    d.rounded_rectangle((rx+183, ry+188, rx+291, ry+218), radius=6, fill=(36,56,78))
    d.rectangle((rx+193, ry+215, rx+201, ry+232), fill=(47,67,88))
    d.rectangle((rx+273, ry+215, rx+281, ry+232), fill=(47,67,88))

    # Streamlines are deliberately schematic, not a physical simulation.
    in_start = (rx-23, oy + opening_h*.72)
    in_ctrl1 = (rx+rw*.12, ry+rh*.90)
    in_ctrl2 = (rx+rw*.60, ry+rh*.98)
    in_end = (rx+rw*.66, ry+rh*.33)
    out_start = (rx+rw*.66, ry+rh*.27)
    out_ctrl1 = (rx+rw*.41, ry+rh*.04)
    out_ctrl2 = (rx+rw*.08, ry+rh*.13)
    out_end = (rx-24, oy+opening_h*.23)
    count = 13 if wide else 8
    rate = 0.075 if wide else 0.041
    for flow, color, points in ((0, CYAN, (in_start,in_ctrl1,in_ctrl2,in_end)), (1, ORANGE, (out_start,out_ctrl1,out_ctrl2,out_end))):
        a,b,c,e = points
        for i in range(count):
            t = ((frame*rate + i/count + flow*.37) % 1)
            px, py = cubic(a,b,c,e,t)
            py += math.sin(frame*.22 + i*1.7)*1.7
            radius = 4 if wide else 3
            d.ellipse((px-radius,py-radius,px+radius,py+radius), fill=color)
            if i % 4 == 0:
                draw_arrow(d, px, py, color, 1 if flow == 0 else -1)

    # Legend
    ly = 468
    d.ellipse((x0+26,ly+3,x0+36,ly+13), fill=CYAN)
    d.text((x0+43,ly), 'Frische Außenluft', font=FONT_SMALL, fill=MUTED)
    d.ellipse((x0+210,ly+3,x0+220,ly+13), fill=ORANGE)
    d.text((x0+227,ly), 'Warme Raumluft', font=FONT_SMALL, fill=MUTED)


def make_frame(frame):
    image = Image.new('RGB', (W,H), BG)
    d = ImageDraw.Draw(image)
    d.text((34, 25), 'LÜFTUNG IM VERGLEICH', font=FONT_SMALL, fill=CYAN)
    d.text((34, 46), 'Wie strömt die Luft?', font=FONT_TITLE, fill=TEXT)
    draw_panel(image, 24, 'Fenster gekippt', False, frame)
    draw_panel(image, 506, 'Fenster ganz geöffnet', True, frame)
    d.text((26, 558-20), 'Schematische Darstellung · tatsächliche Luftströmung hängt von Wind, Temperatur und Raum ab.', font=FONT_SMALL, fill=MUTED)
    return image


def main():
    frames = [make_frame(i) for i in range(FRAMES)]
    output = Path(__file__).resolve().with_name('lueftung-vergleich.gif')
    palette_frames = [frame.quantize(colors=256, method=Image.Quantize.MEDIANCUT) for frame in frames]
    palette_frames[0].save(output, save_all=True, append_images=palette_frames[1:], duration=DURATION, loop=0, optimize=True, disposal=2)
    print(f'Created {output}')


if __name__ == '__main__':
    main()
