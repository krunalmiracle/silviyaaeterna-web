#!/usr/bin/env python3
"""Generate the original SVG illustration set for the Silviya Aeterna redesign.

Every asset in assets/ is authored here: deterministic geometry, no stock, no
hotlinks, no third-party artwork. Run: python3 tools/generate_assets.py
"""
import base64
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

INK = "#060A17"
COBALT_DEEP = "#0E1B45"
COBALT = "#12225C"
MOON = "#EDF1F8"
MOON_DIM = "#C3CBDE"
MINT = "#9FE7CE"
CORAL = "#FF6B4A"


def svg(w, h, body, extra=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}"{extra}>\n{body}\n</svg>\n'
    )


def sky(cx, cy, r, mid=COBALT_DEEP, edge=INK, gid="sky"):
    return (
        f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">'
        f'<stop offset="0" stop-color="{COBALT}"/>'
        f'<stop offset="45%" stop-color="{mid}"/>'
        f'<stop offset="100%" stop-color="{edge}"/></radialGradient>'
    )


def stars(rng, w, h, n, ymax=None, rmin=0.8, rmax=2.0, op=(0.25, 0.8), color=MOON):
    ymax = h if ymax is None else ymax
    out = []
    for _ in range(n):
        x = rng.uniform(10, w - 10)
        y = rng.uniform(10, ymax - 10)
        r = rng.uniform(rmin, rmax)
        o = rng.uniform(*op)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{color}" opacity="{o:.2f}"/>')
    return "\n".join(out)


def ring(cx, cy, r, stroke=MINT, w=1.4, op=0.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{stroke}" stroke-width="{w}" opacity="{op}"{d}/>'


def line(x1, y1, x2, y2, stroke=MINT, w=1.2, op=0.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}" opacity="{op}"{d}/>'


def spokes(cx, cy, r1, r2, n, stroke=MINT, w=1.1, op=0.4, start=-90):
    out = []
    for i in range(n):
        a = math.radians(start + i * 360 / n)
        x1, y1 = cx + r1 * math.cos(a), cy + r1 * math.sin(a)
        x2, y2 = cx + r2 * math.cos(a), cy + r2 * math.sin(a)
        out.append(line(x1, y1, x2, y2, stroke, w, op))
    return "\n".join(out)


def ruler(y, x1, x2, step=18, minor=6, major=13, op=0.28, coral_index=None, stroke=MINT):
    out = [line(x1, y, x2, y, stroke, 1.2, op + 0.14)]
    i = 0
    x = x1
    while x <= x2:
        h = major if i % 5 == 0 else minor
        col = CORAL if i == coral_index else stroke
        o = 0.75 if i == coral_index else op
        sw = 1.8 if i == coral_index else 1.1
        out.append(line(x, y, x, y + h, col, sw, o))
        x += step
        i += 1
    return "\n".join(out)


def qpath(pts, close=False):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + (" Z" if close else "")


def blob(cx, cy, base, amp1, amp2, phase, n=90):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = base + amp1 * math.sin(3 * t + phase) + amp2 * math.cos(5 * t - phase)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t) * 0.82))
    return qpath(pts, close=True)


def phase_disc(cx, cy, r, frac, fill=MOON, bg=COBALT_DEEP, stroke=MOON):
    """Waxing phase: right half lit, terminator an ellipse of rx = r|cos(2*pi*frac)|."""
    rx = abs(r * math.cos(2 * math.pi * frac))
    sweep = 1 if frac < 0.5 else 0
    d = (
        f"M{cx},{cy - r} A{r},{r} 0 0 1 {cx},{cy + r} "
        f"A{rx:.2f},{r} 0 0 {sweep} {cx},{cy - r} Z"
    )
    return (
        f'<g><circle cx="{cx}" cy="{cy}" r="{r}" fill="{bg}" stroke="{stroke}" '
        f'stroke-width="1.2" opacity="0.85"/>'
        f'<path d="{d}" fill="{fill}" opacity="0.92"/></g>'
    )


def corner_arc(w, h, r=180, op=0.16):
    return (
        f'<path d="M{w - r},0 A{r},{r} 0 0 1 {w},{r}" fill="none" stroke="{MINT}" '
        f'stroke-width="1.4" opacity="{op}"/>'
    )


def gradient_bg(w, h, gid="bg"):
    return (
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#101E4E"/><stop offset="55%" stop-color="{COBALT_DEEP}"/>'
        f'<stop offset="100%" stop-color="#080D1F"/></linearGradient></defs>'
        f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>'
    )


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {name} ({len(content)} bytes)")


# ---------------------------------------------------------------- brand marks
def brand_mark():
    body = f'''<defs>
  <mask id="crescent">
    <rect width="64" height="64" fill="#000"/>
    <circle cx="32" cy="33" r="19" fill="#fff"/>
    <circle cx="41.5" cy="26" r="17" fill="#000"/>
  </mask>
</defs>
<circle cx="32" cy="32" r="27" fill="none" stroke="{MINT}" stroke-width="1.4" opacity="0.55"/>
<circle cx="32" cy="32" r="23" fill="none" stroke="{MINT}" stroke-width="0.9" stroke-dasharray="2 5" opacity="0.65"/>
<circle cx="32" cy="33" r="19" fill="{MOON}" mask="url(#crescent)"/>
<circle cx="50" cy="15" r="4.2" fill="{CORAL}"/>
<circle cx="50" cy="15" r="8.5" fill="none" stroke="{CORAL}" stroke-width="1" opacity="0.55"/>'''
    return svg(64, 64, body, ' role="img" aria-label="Silviya Aeterna"')


def favicon():
    body = f'''<rect width="32" height="32" rx="7" fill="{COBALT_DEEP}"/>
<defs><mask id="m"><rect width="32" height="32" fill="#000"/>
<circle cx="16" cy="17" r="9.5" fill="#fff"/>
<circle cx="21" cy="13.5" r="8.5" fill="#000"/></mask></defs>
<circle cx="16" cy="17" r="9.5" fill="{MOON}" mask="url(#m)"/>
<circle cx="24.5" cy="8.5" r="3" fill="{CORAL}"/>'''
    return svg(32, 32, body)


# ---------------------------------------------------------------- hero
def hero_plate():
    rng = random.Random(20261013)
    w, h = 800, 1000
    cx, cy = 400, 470
    parts = [
        "<defs>" + sky("50%", "42%", "72%", gid="hsky")
        + '<radialGradient id="sunhalo"><stop offset="0" stop-color="#FF6B4A" stop-opacity="0.75"/>'
        + '<stop offset="60%" stop-color="#FF6B4A" stop-opacity="0.22"/>'
        + '<stop offset="100%" stop-color="#FF6B4A" stop-opacity="0"/></radialGradient>'
        + '<linearGradient id="fadeb" x1="0" y1="0" x2="0" y2="1">'
        + '<stop offset="60%" stop-color="#060A17" stop-opacity="0"/>'
        + '<stop offset="100%" stop-color="#060A17" stop-opacity="0.55"/></linearGradient>'
        + "</defs>",
        f'<rect width="{w}" height="{h}" fill="url(#hsky)"/>',
        stars(rng, w, 760, 46, ymax=830, rmin=0.7, rmax=2.1),
        # rings
        ring(cx, cy, 330, MINT, 1.5, 0.4, "2 10"),
        ring(cx, cy, 300, MINT, 1.1, 0.3),
        ring(cx, cy, 248, MINT, 1.6, 0.55),
        ring(cx, cy, 206, MINT, 1.1, 0.34, "7 7"),
        # zodiac band
        spokes(cx, cy, 206, 248, 12, MINT, 1.2, 0.45),
    ]
    for i in range(12):
        a = math.radians(-90 + 15 + i * 30)
        x, y = cx + 227 * math.cos(a), cy + 227 * math.sin(a)
        if i % 3 == 0:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{MOON}" opacity="0.9"/>')
        elif i % 3 == 1:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="none" stroke="{MINT}" stroke-width="1.3" opacity="0.9"/>')
        else:
            d = f"M{x:.1f},{y - 5:.1f} L{x + 5:.1f},{y:.1f} L{x:.1f},{y + 5:.1f} L{x - 5:.1f},{y:.1f} Z"
            parts.append(f'<path d="{d}" fill="{MINT}" opacity="0.85"/>')
    # orbits and bodies
    parts += [
        f'<ellipse cx="{cx}" cy="{cy}" rx="176" ry="74" fill="none" stroke="{MINT}" stroke-width="1.2" stroke-dasharray="3 7" opacity="0.6" transform="rotate(-18 {cx} {cy})"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="146" ry="146" fill="none" stroke="{MINT}" stroke-width="1" stroke-dasharray="2 9" opacity="0.4"/>',
    ]
    for ang, dist, r, col in [(-38, 168, 21, MOON), (132, 150, 12, MINT), (58, 168, 8, MOON)]:
        a = math.radians(ang)
        x, y = cx + dist * math.cos(a), cy + dist * math.sin(a)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 9}" fill="none" stroke="{col}" stroke-width="1" opacity="0.35"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="0.95"/>')
    # sun focal
    parts += [
        f'<circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="{CORAL}" stroke-width="1" opacity="0.35"/>',
        f'<circle cx="{cx}" cy="{cy}" r="62" fill="url(#sunhalo)"/>',
        f'<circle cx="{cx}" cy="{cy}" r="30" fill="{CORAL}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{MOON}" stroke-width="1.2" opacity="0.5"/>',
    ]
    # lower ephemeris band
    pts = []
    for i in range(41):
        x = 70 + i * 16.5
        y = 862 - 44 * math.sin(i / 40 * math.pi) - 10 * math.sin(i / 3.1)
        pts.append((x, y))
    parts += [
        f'<path d="{qpath(pts)}" fill="none" stroke="{MINT}" stroke-width="1.6" opacity="0.55"/>',
        ruler(898, 70, 730, step=20, coral_index=17),
        f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="5" fill="{CORAL}"/>',
        line(70, 946, 730, 946, MINT, 1.1, 0.22, "1 9"),
        f'<rect y="820" width="{w}" height="180" fill="url(#fadeb)"/>',
    ]
    return svg(w, h, "\n".join(parts))


# ---------------------------------------------------------------- manifesto band
def manifesto_plate():
    rng = random.Random(77)
    w, h = 1400, 560
    parts = [
        "<defs>" + sky("50%", "10%", "90%", gid="msky") + "</defs>",
        f'<rect width="{w}" height="{h}" fill="url(#msky)"/>',
        stars(rng, w, 300, 30, ymax=340, rmin=0.7, rmax=1.8, op=(0.2, 0.6)),
        corner_arc(w, h, 150),
    ]
    # moon phase row
    for i in range(8):
        x = 145 + i * 160
        parts.append(phase_disc(x, 86, 22, i / 8))
    parts.append(line(60, 86, 1340, 86, MINT, 1, 0.14, "1 12"))
    # sun path arcs
    horizon = 470
    for i, apex in enumerate([340, 268, 200, 140]):
        op = 0.5 - i * 0.08
        parts.append(
            f'<path d="M70,{horizon} Q700,{horizon - 2 * apex} 1330,{horizon}" fill="none" '
            f'stroke="{MINT}" stroke-width="{1.6 - i * 0.2:.1f}" opacity="{op:.2f}"/>'
        )
    # coral sun on the middle arc
    parts += [
        '<defs><radialGradient id="msun"><stop offset="0" stop-color="#FF8763" stop-opacity="0.9"/>'
        '<stop offset="55%" stop-color="#FF6B4A" stop-opacity="0.4"/>'
        '<stop offset="100%" stop-color="#FF6B4A" stop-opacity="0"/></radialGradient></defs>',
        f'<circle cx="700" cy="{horizon - 400}" r="64" fill="url(#msun)"/>',
        f'<circle cx="700" cy="{horizon - 400}" r="24" fill="{CORAL}"/>',
    ]
    # horizon + ruler
    parts.append(ruler(horizon, 40, 1360, step=22, major=14, op=0.3, coral_index=12))
    parts.append(f'<rect y="{horizon + 40}" width="{w}" height="{h - horizon - 40}" fill="{INK}" opacity="0.35"/>')
    return svg(w, h, "\n".join(parts))


# ---------------------------------------------------------------- topic plates
def plate_frame(w, h, seed, stars_n=16):
    rng = random.Random(seed)
    return gradient_bg(w, h) + "\n" + stars(rng, w, h - 70, stars_n, rmin=0.7, rmax=1.7, op=(0.2, 0.65)) + "\n" + corner_arc(w, h)


def topic_astrology():
    w, h = 700, 520
    cx, cy = 350, 245
    p = [plate_frame(w, h, 101),
         ring(cx, cy, 172, MINT, 1.5, 0.55),
         ring(cx, cy, 134, MINT, 1.2, 0.36, "6 6"),
         spokes(cx, cy, 134, 172, 12, MINT, 1.1, 0.42)]
    for i in range(12):
        a = math.radians(-90 + 15 + i * 30)
        x, y = cx + 153 * math.cos(a), cy + 153 * math.sin(a)
        if i % 2 == 0:
            p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{MOON}" opacity="0.92"/>')
        else:
            d = f"M{x:.1f},{y - 5.2:.1f} L{x + 5.2:.1f},{y:.1f} L{x:.1f},{y + 5.2:.1f} L{x - 5.2:.1f},{y:.1f} Z"
            p.append(f'<path d="{d}" fill="none" stroke="{MINT}" stroke-width="1.3" opacity="0.9"/>')
    p += [
        f'<ellipse cx="{cx}" cy="{cy}" rx="112" ry="46" fill="none" stroke="{MINT}" stroke-width="1.1" stroke-dasharray="3 7" opacity="0.6" transform="rotate(-20 {cx} {cy})"/>',
        f'<circle cx="{cx + 106 * math.cos(math.radians(-20)):.1f}" cy="{cy + 44 * math.sin(math.radians(-20)):.1f}" r="8" fill="{MOON}" opacity="0.95"/>',
        f'<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{CORAL}" stroke-width="1" opacity="0.5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="21" fill="{CORAL}"/>',
        ruler(466, 60, 640, step=16, coral_index=9),
    ]
    return svg(w, h, "\n".join(p))


def topic_numerology():
    w, h = 700, 520
    cell, gap = 96, 10
    gw = cell * 3 + gap * 2
    ox, oy = (w - gw) / 2, 92
    magic = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    p = [plate_frame(w, h, 202, stars_n=14)]
    # life-path line behind the grid
    p.append(f'<path d="M110,430 L{ox + 60:.0f},{oy + gw - 40:.0f} L{ox + gw - 30:.0f},{oy + 40:.0f} L600,60" '
             f'fill="none" stroke="{MINT}" stroke-width="1.2" stroke-dasharray="4 8" opacity="0.5"/>')
    for r in range(3):
        for c in range(3):
            x = ox + c * (cell + gap)
            y = oy + r * (cell + gap)
            is_center = r == 1 and c == 1
            stroke = CORAL if is_center else MINT
            op = 0.85 if is_center else 0.42
            fill = "#0B1436" if not is_center else "#151B3D"
            p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="12" fill="{fill}" '
                     f'stroke="{stroke}" stroke-width="{1.6 if is_center else 1.2}" opacity="{op}"/>')
            p.append(f'<text x="{x + cell / 2}" y="{y + cell / 2}" fill="{MOON}" font-size="42" '
                     f'font-weight="600" text-anchor="middle" dominant-baseline="central" '
                     f'font-family="Geist, system-ui, sans-serif">{magic[r][c]}</text>')
    p.append(f'<circle cx="{ox + gw + 18:.0f}" cy="{oy - 14}" r="7" fill="{CORAL}"/>')
    p.append(ruler(466, 60, 640, step=16, coral_index=6))
    return svg(w, h, "\n".join(p))


def topic_skincare():
    w, h = 700, 520
    p = [plate_frame(w, h, 303, stars_n=12)]
    # skin strata
    for i, (base, op, sw) in enumerate([(300, 0.4, 2.2), (336, 0.3, 1.6), (372, 0.22, 1.4), (406, 0.15, 1.2)]):
        pts = [(x, base + 9 * math.sin((x - 60) / 62 + i * 1.1)) for x in range(50, 651, 10)]
        p.append(f'<path d="{qpath(pts)}" fill="none" stroke="{MINT}" stroke-width="{sw}" opacity="{op}"/>')
    p.append(f'<path d="{qpath([(x, 440 + 7 * math.sin((x - 60) / 70)) for x in range(50, 651, 10)])}" '
             f'fill="none" stroke="{MOON}" stroke-width="1.2" opacity="0.2"/>')
    # droplet
    drop = "M350,96 C392,150 418,192 418,228 A68,68 0 1 1 282,228 C282,192 308,150 350,96 Z"
    p += [
        f'<path d="{drop}" fill="none" stroke="{MOON}" stroke-width="2.4" opacity="0.95"/>',
        f'<path d="M350,150 C374,186 388,208 388,230 A38,38 0 0 1 312,230 C312,208 326,186 350,150 Z" fill="{CORAL}" opacity="0.9"/>',
        f'<ellipse cx="350" cy="316" rx="86" ry="18" fill="none" stroke="{MINT}" stroke-width="1.4" opacity="0.5"/>',
        f'<ellipse cx="350" cy="316" rx="132" ry="27" fill="none" stroke="{MINT}" stroke-width="1.1" stroke-dasharray="3 8" opacity="0.38"/>',
    ]
    for x, y, r in [(196, 150, 5), (508, 176, 4), (240, 236, 3.4), (470, 268, 5.4)]:
        p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{MINT}" stroke-width="1.3" opacity="0.55"/>')
    p.append(ruler(466, 60, 640, step=16, coral_index=4))
    return svg(w, h, "\n".join(p))


def topic_wellbeing():
    w, h = 700, 520
    p = [plate_frame(w, h, 404, stars_n=14)]
    for i in range(6):
        base = 46 + i * 34
        op = 0.55 - i * 0.075
        p.append(f'<path d="{blob(350, 250, base, 7 + i * 1.6, 5 + i, 0.9 + i * 0.5)}" fill="none" '
                 f'stroke="{MINT}" stroke-width="{1.6 - i * 0.12:.2f}" opacity="{op:.2f}"/>')
    p += [
        f'<path d="{blob(350, 250, 26, 6, 4, 2.1)}" fill="{CORAL}" opacity="0.92"/>',
        f'<circle cx="350" cy="250" r="92" fill="none" stroke="{MOON}" stroke-width="1" stroke-dasharray="2 9" opacity="0.45"/>',
        line(70, 250, 630, 250, MOON, 1.1, 0.16, "1 12"),
    ]
    p.append(ruler(466, 60, 640, step=16, coral_index=11))
    return svg(w, h, "\n".join(p))


def topic_family():
    w, h = 700, 520
    p = [plate_frame(w, h, 505, stars_n=16)]
    big, med, small = (330, 300, 95), (462, 352, 62), (236, 372, 48)
    p += [
        f'<path d="M110,236 Q350,104 596,236" fill="none" stroke="{MINT}" stroke-width="1.6" opacity="0.5"/>',
        f'<path d="M140,266 Q350,146 566,266" fill="none" stroke="{MINT}" stroke-width="1" stroke-dasharray="3 9" opacity="0.4"/>',
        line(big[0], big[1], med[0], med[1], MINT, 1.1, 0.45, "4 7"),
        line(big[0], big[1], small[0], small[1], MINT, 1.1, 0.45, "4 7"),
        line(med[0], med[1], small[0], small[1], MINT, 1.1, 0.45, "4 7"),
        f'<circle cx="{big[0]}" cy="{big[1]}" r="{big[2]}" fill="none" stroke="{MOON}" stroke-width="2" opacity="0.8"/>',
        f'<circle cx="{big[0]}" cy="{big[1]}" r="{big[2] - 14}" fill="none" stroke="{MINT}" stroke-width="1" stroke-dasharray="2 10" opacity="0.5"/>',
        f'<circle cx="{med[0]}" cy="{med[1]}" r="{med[2]}" fill="none" stroke="{MINT}" stroke-width="1.8" opacity="0.75"/>',
        f'<circle cx="{small[0]}" cy="{small[1]}" r="{small[2]}" fill="{CORAL}" fill-opacity="0.18" stroke="{CORAL}" stroke-width="1.8"/>',
        f'<circle cx="{small[0]}" cy="{small[1]}" r="9" fill="{CORAL}"/>',
        ruler(466, 60, 640, step=16, coral_index=8),
    ]
    return svg(w, h, "\n".join(p))


def topic_mental_health():
    w, h = 700, 520
    p = [plate_frame(w, h, 606, stars_n=18)]
    p.append('<defs><radialGradient id="lamp"><stop offset="0" stop-color="#FF8763" stop-opacity="0.85"/>'
             '<stop offset="100%" stop-color="#FF6B4A" stop-opacity="0"/></radialGradient></defs>')
    # window
    p.append(f'<path d="M225,425 L225,240 A125,125 0 0 1 475,240 L475,425 Z" fill="#0A1436" stroke="{MINT}" '
             f'stroke-width="2" opacity="0.95"/>')
    # night sky inside
    p.append(f'<clipPath id="win"><path d="M225,425 L225,240 A125,125 0 0 1 475,240 L475,425 Z"/></clipPath>')
    p.append('<g clip-path="url(#win)">')
    p.append(f'<circle cx="404" cy="196" r="27" fill="{MOON}" opacity="0.95"/>')
    p.append(f'<circle cx="392" cy="188" r="24" fill="#0A1436"/>')
    for x, y, r in [(280, 180, 3), (320, 236, 2.4), (440, 268, 2.8), (268, 300, 2.2), (352, 300, 2.6)]:
        p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{MOON}" opacity="0.8"/>')
    p.append(f'<circle cx="300" cy="344" r="56" fill="url(#lamp)"/>')
    p.append('</g>')
    # mullions + sill
    p.append(line(350, 122, 350, 425, MINT, 1.6, 0.75))
    p.append(line(225, 300, 475, 300, MINT, 1.6, 0.75))
    p.append(line(185, 425, 515, 425, MINT, 2, 0.85))
    # plant on the sill
    p.append(f'<path d="M255,425 L285,425 L281,456 L259,456 Z" fill="none" stroke="{MOON}" stroke-width="1.6" opacity="0.85"/>')
    for dx, dy, c in [(0, -30, -14), (0, -34, 0), (0, -28, 16)]:
        p.append(f'<path d="M270,425 Q{270 + c},{425 + dy} {270 + c * 1.5},{425 + dy - 6}" fill="none" '
                 f'stroke="{MINT}" stroke-width="1.6" opacity="0.8"/>')
    # two stacked books on the right end of the sill, balancing the plant
    p.append(f'<rect x="478" y="414" width="36" height="10" rx="3" fill="#0B1436" stroke="{MOON}" stroke-width="1.5" opacity="0.9"/>')
    p.append(f'<rect x="484" y="403" width="27" height="10" rx="3" fill="#0B1436" stroke="{MINT}" stroke-width="1.5" opacity="0.85"/>')
    p.append(f'<path d="M150,452 Q350,486 550,452" fill="none" stroke="{CORAL}" stroke-width="1.4" stroke-dasharray="4 8" opacity="0.5"/>')
    p.append(ruler(474, 60, 640, step=16, coral_index=14))
    return svg(w, h, "\n".join(p))


# ---------------------------------------------------------------- channel
def channel_plate():
    w, h = 1000, 640
    rng = random.Random(909)
    sx, sy = 168, 300
    p = [
        gradient_bg(w, h, "cgbg") + "\n" + stars(rng, w, 460, 26, ymax=470, rmin=0.7, rmax=1.9),
        '<defs><radialGradient id="src"><stop offset="0" stop-color="#FF8763" stop-opacity="0.95"/>'
        '<stop offset="100%" stop-color="#FF6B4A" stop-opacity="0"/></radialGradient></defs>',
    ]
    for i, r in enumerate([80, 140, 200, 262, 326, 392]):
        a0, a1 = math.radians(-64), math.radians(64)
        x0, y0 = sx + r * math.cos(a0), sy + r * math.sin(a0)
        x1, y1 = sx + r * math.cos(a1), sy + r * math.sin(a1)
        p.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 0 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{MINT}" '
                 f'stroke-width="{1.8 - i * 0.18:.2f}" opacity="{0.65 - i * 0.08:.2f}"/>')
    p += [
        f'<circle cx="{sx}" cy="{sy}" r="88" fill="url(#src)"/>',
        f'<circle cx="{sx}" cy="{sy}" r="26" fill="{CORAL}"/>',
        f'<circle cx="{sx}" cy="{sy}" r="46" fill="none" stroke="{CORAL}" stroke-width="1.2" opacity="0.6"/>',
        # signal line
        f'<path d="M{sx + 60},{sy} L940,{sy}" fill="none" stroke="{MOON}" stroke-width="1.2" stroke-dasharray="3 9" opacity="0.45"/>',
    ]
    for x in (sx + 150, sx + 300, sx + 450, sx + 600):
        p.append(f'<circle cx="{x}" cy="{sy}" r="5" fill="none" stroke="{MOON}" stroke-width="1.4" opacity="0.7"/>')
    # film strip band
    p.append(f'<rect x="40" y="520" width="920" height="86" rx="10" fill="{INK}" opacity="0.5" stroke="{MINT}" stroke-width="1.2" stroke-opacity="0.4"/>')
    x = 62
    while x < 940:
        p.append(f'<rect x="{x}" y="532" width="26" height="14" rx="4" fill="{MINT}" opacity="0.35"/>')
        p.append(f'<rect x="{x}" y="580" width="26" height="14" rx="4" fill="{MINT}" opacity="0.35"/>')
        x += 56
    p.append(ruler(496, 40, 960, step=22, major=12, op=0.26, coral_index=6))
    return svg(w, h, "\n".join(p))


# ---------------------------------------------------------------- shop
def shop_plate():
    w, h = 700, 900
    rng = random.Random(313)
    p = [gradient_bg(w, h, "sgbg") + "\n" + stars(rng, w, 340, 22, ymax=340, rmin=0.7, rmax=1.8),
         '<defs><pattern id="hatch" width="16" height="16" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="16" stroke="#9FE7CE" '
         'stroke-width="2.4" opacity="0.22"/></pattern></defs>']
    # shelf
    p.append(line(70, 660, 630, 660, MINT, 2, 0.7))
    p.append(line(70, 660, 70, 700, MINT, 1.2, 0.4))
    p.append(line(630, 660, 630, 700, MINT, 1.2, 0.4))
    vessels = (
        # jar
        f'<rect x="120" y="516" width="150" height="144" rx="18" fill="#0B1436" stroke="{MOON}" stroke-width="2" opacity="0.95"/>'
        f'<rect x="112" y="478" width="166" height="44" rx="12" fill="#0B1436" stroke="{MOON}" stroke-width="2" opacity="0.95"/>'
        f'<line x1="132" y1="576" x2="258" y2="576" stroke="{MINT}" stroke-width="1.4" opacity="0.5"/>'
        # bottle
        f'<rect x="336" y="472" width="52" height="60" rx="8" fill="#0B1436" stroke="{MINT}" stroke-width="2" opacity="0.95"/>'
        f'<rect x="312" y="530" width="100" height="130" rx="22" fill="#0B1436" stroke="{MINT}" stroke-width="2" opacity="0.95"/>'
        f'<line x1="326" y1="586" x2="398" y2="586" stroke="{MINT}" stroke-width="1.4" opacity="0.5"/>'
        # tube
        f'<path d="M486,540 L586,540 L586,644 Q536,660 486,644 Z" fill="#0B1436" stroke="{MOON}" stroke-width="2" opacity="0.95"/>'
        f'<rect x="504" y="504" width="64" height="36" rx="8" fill="#0B1436" stroke="{MOON}" stroke-width="2" opacity="0.95"/>'
    )
    p.append(vessels)
    # placeholder hatching + dashed frame
    p.append('<rect x="98" y="452" width="508" height="224" fill="url(#hatch)"/>')
    p.append(f'<rect x="90" y="444" width="524" height="240" rx="14" fill="none" stroke="{MINT}" '
             f'stroke-width="1.4" stroke-dasharray="8 10" opacity="0.55"/>')
    # coral price tag (no text: nothing is priced yet)
    p.append(f'<g transform="rotate(-9 546 262)">'
             f'<path d="M474,222 L624,222 Q640,222 640,238 L640,300 Q640,316 624,316 L474,316 Q458,316 458,300 L458,238 Q458,222 474,222 Z" fill="{CORAL}" opacity="0.92"/>'
             f'<circle cx="492" cy="269" r="9" fill="{COBALT_DEEP}"/>'
             f'</g>')
    p.append(f'<path d="M470,262 Q400,300 372,470" fill="none" stroke="{CORAL}" stroke-width="1.4" stroke-dasharray="5 8" opacity="0.6"/>')
    p.append(ruler(724, 70, 630, step=16, coral_index=7))
    return svg(w, h, "\n".join(p))


# ---------------------------------------------------------------- safety band
def safety_plate():
    w, h = 1200, 300
    rng = random.Random(4242)
    p = [
        gradient_bg(w, h, "fkgg") + "\n" + stars(rng, w, 300, 22, rmin=0.6, rmax=1.6, op=(0.18, 0.5)),
        f'<path d="M300,58 L232,58 L232,242 L300,242" fill="none" stroke="{MINT}" stroke-width="3" opacity="0.75" stroke-linecap="round"/>',
        f'<path d="M900,58 L968,58 L968,242 L900,242" fill="none" stroke="{MINT}" stroke-width="3" opacity="0.75" stroke-linecap="round"/>',
        ring(600, 150, 96, MINT, 1.2, 0.4, "3 10"),
        f'<circle cx="600" cy="150" r="62" fill="none" stroke="{MOON}" stroke-width="2" opacity="0.85"/>',
        line(360, 150, 840, 150, MINT, 1.4, 0.45),
        line(538, 150, 662, 150, CORAL, 3, 1),
        f'<circle cx="600" cy="150" r="7" fill="{CORAL}"/>',
        f'<circle cx="600" cy="150" r="13" fill="none" stroke="{CORAL}" stroke-width="1.4" opacity="0.7"/>',
        ruler(258, 240, 960, step=20, major=12, op=0.24),
    ]
    return svg(w, h, "\n".join(p))


# ---------------------------------------------------------------- closing
def closing_plate():
    w, h = 1000, 800
    rng = random.Random(515)
    cx, cy = 560, 360
    p = [
        f'<defs>{sky("60%", "40%", "80%", gid="clsky")}'
        f'<linearGradient id="clfade" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{INK}" stop-opacity="1"/>'
        f'<stop offset="52%" stop-color="{INK}" stop-opacity="0"/>'
        f'</linearGradient>'
        f'<mask id="clcres"><rect width="{w}" height="{h}" fill="#000"/>'
        f'<circle cx="{cx}" cy="{cy}" r="170" fill="#fff"/>'
        f'<circle cx="{cx + 86}" cy="{cy - 64}" r="152" fill="#000"/></mask></defs>',
        f'<rect width="{w}" height="{h}" fill="url(#clsky)"/>',
        stars(rng, w, h, 40, rmin=0.7, rmax=2.0),
        ring(cx, cy, 250, MINT, 1.4, 0.35, "2 11"),
        ring(cx, cy, 214, MINT, 1, 0.22),
        f'<circle cx="{cx}" cy="{cy}" r="170" fill="{MOON}" opacity="0.16" mask="url(#clcres)"/>',
        f'<circle cx="{cx + 196}" cy="{cy - 148}" r="60" fill="none" stroke="{CORAL}" stroke-width="1.4" opacity="0.5"/>',
        f'<circle cx="{cx + 196}" cy="{cy - 148}" r="34" fill="{CORAL}" opacity="0.9"/>',
        # dawn arcs
        f'<path d="M40,700 Q500,540 960,700" fill="none" stroke="{MINT}" stroke-width="1.6" opacity="0.4"/>',
        f'<path d="M40,744 Q500,586 960,744" fill="none" stroke="{CORAL}" stroke-width="1.6" opacity="0.5"/>',
        ruler(766, 40, 960, step=22, major=12, op=0.26, coral_index=9),
        f'<rect width="{w}" height="{h}" fill="url(#clfade)"/>',
    ]
    return svg(w, h, "\n".join(p))


# ---------------------------------------------------------------- social card
def social_og():
    w, h = 1200, 630
    rng = random.Random(626)
    font_b64 = ""
    font_file = OUT / "fonts" / "Geist-Variable-subset.woff2"
    if font_file.exists():
        font_b64 = base64.b64encode(font_file.read_bytes()).decode()
    face = (
        f"@font-face{{font-family:'Geist';src:url(data:font/woff2;base64,{font_b64}) format('woff2');"
        "font-weight:100 900;font-display:block;}}"
        if font_b64 else ""
    )
    cx, cy = 268, 315
    p = [
        f'<defs>{sky("72%", "30%", "95%", gid="ogsky")}'
        f'<mask id="ogcres"><rect width="{w}" height="{h}" fill="#000"/>'
        f'<circle cx="{cx}" cy="{cy}" r="112" fill="#fff"/>'
        f'<circle cx="{cx + 58}" cy="{cy - 44}" r="99" fill="#000"/></mask>'
        f'<style>{face}</style></defs>',
        f'<rect width="{w}" height="{h}" fill="url(#ogsky)"/>',
        stars(rng, w, h, 46, rmin=0.7, rmax=2.0),
        ring(cx, cy, 162, MINT, 1.4, 0.5),
        ring(cx, cy, 140, MINT, 1, 0.35, "2 10"),
        f'<circle cx="{cx}" cy="{cy}" r="112" fill="{MOON}" opacity="0.95" mask="url(#ogcres)"/>',
        f'<circle cx="{cx + 148}" cy="{cy - 112}" r="42" fill="none" stroke="{CORAL}" stroke-width="1.4" opacity="0.6"/>',
        f'<circle cx="{cx + 148}" cy="{cy - 112}" r="26" fill="{CORAL}"/>',
        f'<text x="500" y="300" fill="{MOON}" font-family="Geist, system-ui, sans-serif" font-size="94" '
        f'font-weight="600" letter-spacing="-3">Silviya Aeterna</text>',
        f'<text x="504" y="372" fill="{MINT}" font-family="Geist, system-ui, sans-serif" font-size="34" '
        f'font-weight="500">Bulgarian and English</text>',
        f'<text x="504" y="430" fill="{MOON_DIM}" font-family="Geist, system-ui, sans-serif" font-size="27" '
        f'font-weight="400">Astrology, numerology, skincare, wellbeing</text>',
        line(504, 470, 1120, 470, MINT, 1.4, 0.35),
        ruler(560, 504, 1120, step=20, major=12, op=0.3, coral_index=5),
    ]
    return svg(w, h, "\n".join(p))


def main():
    OUT.mkdir(exist_ok=True)
    write("brand-mark.svg", brand_mark())
    write("favicon.svg", favicon())
    write("hero-plate.svg", hero_plate())
    write("manifesto-plate.svg", manifesto_plate())
    write("topic-astrology.svg", topic_astrology())
    write("topic-numerology.svg", topic_numerology())
    write("topic-skincare.svg", topic_skincare())
    write("topic-wellbeing.svg", topic_wellbeing())
    write("topic-family.svg", topic_family())
    write("topic-mental-health.svg", topic_mental_health())
    write("channel-plate.svg", channel_plate())
    write("shop-plate.svg", shop_plate())
    write("safety-plate.svg", safety_plate())
    write("closing-plate.svg", closing_plate())
    write("social-og.svg", social_og())


if __name__ == "__main__":
    main()
