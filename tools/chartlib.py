"""
chartlib.py — dependency-free SVG chart library (Python stdlib only).

Why hand-rolled SVG? The research notes must render on GitHub *and* on the
personal website with zero external dependencies and no Dune iframes. SVG is
vector, tiny, theme-safe and diffs cleanly in git.

Author: Bonnie Bennett · MIT
"""
import math
import xml.etree.ElementTree as ET
from html import escape

PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed",
           "#0891b2", "#db2777", "#65a30d", "#0f766e", "#9333ea"]
FONT = "Helvetica, Arial, sans-serif"
BG = "#ffffff"
INK = "#1f2937"
MUTED = "#6b7280"
GRID = "#e5e7eb"


def _fmt(v):
    if v is None:
        return ""
    av = abs(v)
    if av >= 1e9:
        return f"{v/1e9:.1f}B"
    if av >= 1e6:
        return f"{v/1e6:.1f}M"
    if av >= 1e3:
        return f"{v/1e3:.1f}k"
    if av >= 10:
        return f"{v:.0f}"
    if av >= 1:
        return f"{v:.2f}"
    if v == 0:
        return "0"
    return f"{v:.3f}"


def _nice(v):
    if v == 0:
        return 1.0
    s = 1 if v > 0 else -1
    v = abs(v)
    e = math.floor(math.log10(v))
    b = 10 ** e
    for m in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * b >= v:
            return s * m * b
    return s * 10 * b


def _svglines(parts, w, h, title, subtitle, footer):
    """Wrap body parts into a valid SVG document and sanity-check XML."""
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">'
        f'<rect width="{w}" height="{h}" fill="{BG}"/>'
    )
    t = f'<text x="{w/2}" y="30" text-anchor="middle" font-size="19" font-weight="700" fill="{INK}">{escape(title)}</text>'
    s = f'<text x="{w/2}" y="50" text-anchor="middle" font-size="12.5" fill="{MUTED}">{escape(subtitle)}</text>'
    f = f'<text x="{w/2}" y="{h-10}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{escape(footer)}</text>'
    body = "".join(parts)
    svg = head + t + s + body + f + "</svg>"
    ET.fromstring(svg)  # raises if malformed
    return svg


def _frame(parts, x0, x1, y0, y1, ymin, ymax, yfmt, xlabels, show_every,
           y2min=None, y2max=None, y2fmt=None):
    n = 5
    for i in range(n + 1):
        frac = i / n
        y = y1 - frac * (y1 - y0)
        val = ymin + frac * (ymax - ymin)
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">{yfmt(val)}</text>')
    nx = len(xlabels)
    for i, lab in enumerate(xlabels):
        if nx > 12 and i % show_every != 0 and i != nx - 1:
            continue
        x = x0 + (i / max(nx - 1, 1)) * (x1 - x0)
        parts.append(f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1+5}" stroke="{MUTED}" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{y1+20}" text-anchor="middle" font-size="10.5" fill="{MUTED}">{escape(str(lab))}</text>')
    if y2min is not None:
        for i in range(n + 1):
            frac = i / n
            y = y1 - frac * (y1 - y0)
            val = y2min + frac * (y2max - y2min)
            parts.append(f'<text x="{x1+8}" y="{y+4:.1f}" text-anchor="start" font-size="11" fill="{MUTED}">{y2fmt(val)}</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="1.2"/>')
    parts.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="1.2"/>')


def _legend(parts, items, x0, y0):
    x = x0
    for name, color in items:
        parts.append(f'<rect x="{x}" y="{y0-9}" width="12" height="12" rx="2" fill="{color}"/>')
        parts.append(f'<text x="{x+17}" y="{y0+1}" font-size="11.5" fill="{INK}">{escape(name)}</text>')
        x += 26 + len(name) * 7.2



def line_chart(labels, series, title, subtitle, footer, ylabel="", yfmt=_fmt,
               width=920, height=470, y2=None, y2fmt=_fmt, y2label=""):
    """series: list of (name, values); y2: optional (name, values) on right axis."""
    L, R, T, B = 82, (84 if y2 else 26), 74, 74
    x0, x1, y0, y1 = L, width - R, T, height - B
    allv = [v for _, vs in series for v in vs if v is not None]
    ymin = min(0, min(allv))
    ymax = _nice(max(allv))
    parts = []
    y2min = y2max = None
    if y2:
        v2 = [v for v in y2[1] if v is not None]
        y2min, y2max = min(v2), _nice(max(v2))
    n = len(labels)
    step = max(1, n // 12)
    _frame(parts, x0, x1, y0, y1, ymin, ymax, yfmt, labels, step,
           y2min, y2max, y2fmt)

    def X(i):
        return x0 + (i / max(n - 1, 1)) * (x1 - x0)

    def Y(v):
        return y1 - ((v - ymin) / ((ymax - ymin) or 1)) * (y1 - y0)

    leg = []
    if y2:
        pts = " ".join(
            f"{X(i):.1f},{y1-((v-y2min)/((y2max-y2min) or 1))*(y1-y0):.1f}"
            for i, v in enumerate(y2[1]) if v is not None)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="#9ca3af" stroke-width="1.6" stroke-dasharray="5 3"/>')
        leg.append((y2[0] + " (right)", "#9ca3af"))
    for k, (name, vs) in enumerate(series):
        color = PALETTE[k % len(PALETTE)]
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vs) if v is not None)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        leg.append((name, color))
    _legend(parts, leg, x0, y0 + 12)
    if ylabel:
        parts.append(f'<text x="16" y="{(y0+y1)/2}" font-size="11.5" fill="{MUTED}" transform="rotate(-90 16 {(y0+y1)/2})" text-anchor="middle">{escape(ylabel)}</text>')
    if y2label:
        parts.append(f'<text x="{width-14}" y="{(y0+y1)/2}" font-size="11.5" fill="{MUTED}" transform="rotate(90 {width-14} {(y0+y1)/2})" text-anchor="middle">{escape(y2label)}</text>')
    return _svglines(parts, width, height, title, subtitle, footer)


def bar_chart(categories, series, title, subtitle, footer, ylabel="", yfmt=_fmt,
              width=920, height=470, show_every=1):
    L, R, T, B = 82, 26, 74, 74
    x0, x1, y0, y1 = L, width - R, T, height - B
    allv = [v for _, vs in series for v in vs]
    ymin = min(0, min(allv))
    ymax = _nice(max(allv))
    parts = []
    _frame(parts, x0, x1, y0, y1, ymin, ymax, yfmt, categories, show_every)

    def Y(v):
        return y1 - ((v - ymin) / ((ymax - ymin) or 1)) * (y1 - y0)

    m = len(series)
    bw = (x1 - x0) / max(len(categories), 1)
    inner = bw * 0.72
    sub = inner / m
    leg = []
    for k, (name, vs) in enumerate(series):
        color = PALETTE[k % len(PALETTE)]
        for i, v in enumerate(vs):
            cx = x0 + i * bw + (bw - inner) / 2 + k * sub
            yv = Y(v)
            parts.append(f'<rect x="{cx:.1f}" y="{min(yv,y1):.1f}" width="{sub*0.86:.1f}" height="{abs(y1-yv):.1f}" fill="{color}" rx="1.5"/>')
        leg.append((name, color))
    _legend(parts, leg, x0, y0 + 12)
    if ylabel:
        parts.append(f'<text x="16" y="{(y0+y1)/2}" font-size="11.5" fill="{MUTED}" transform="rotate(-90 16 {(y0+y1)/2})" text-anchor="middle">{escape(ylabel)}</text>')
    return _svglines(parts, width, height, title, subtitle, footer)


def scatter_chart(groups, title, subtitle, footer, xlabel="", ylabel="",
                  xfmt=_fmt, yfmt=_fmt, width=920, height=470):
    """groups: list of (name, xs, ys). A trend line is fit on the first group."""
    L, R, T, B = 82, 26, 74, 84
    x0, x1, y0, y1 = L, width - R, T, height - B
    allx = [x for _, xs, _ in groups for x in xs]
    ally = [y for _, _, ys in groups for y in ys]
    xmin, xmax = min(allx), max(allx)
    ymin, ymax = min(0, min(ally)), _nice(max(ally))
    parts = []
    n = 5
    for i in range(n + 1):
        frac = i / n
        y = y1 - frac * (y1 - y0)
        v = ymin + frac * (ymax - ymin)
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}"/>')
        parts.append(f'<text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">{yfmt(v)}</text>')
        x = x0 + frac * (x1 - x0)
        vx = xmin + frac * (xmax - xmin)
        parts.append(f'<text x="{x:.1f}" y="{y1+20}" text-anchor="middle" font-size="10.5" fill="{MUTED}">{xfmt(vx)}</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}"/>')
    parts.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}"/>')

    def X(v):
        return x0 + ((v - xmin) / ((xmax - xmin) or 1)) * (x1 - x0)

    def Y(v):
        return y1 - ((v - ymin) / ((ymax - ymin) or 1)) * (y1 - y0)

    leg = []
    for k, (name, xs, ys) in enumerate(groups):
        color = PALETTE[k % len(PALETTE)]
        for x, y in zip(xs, ys):
            parts.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="2.6" fill="{color}" fill-opacity="0.55"/>')
        leg.append((name, color))
    xs0, ys0 = groups[0][1], groups[0][2]
    if len(xs0) > 2:
        mx = sum(xs0) / len(xs0)
        my = sum(ys0) / len(ys0)
        den = sum((x - mx) ** 2 for x in xs0) or 1
        slope = sum((x - mx) * (y - my) for x, y in zip(xs0, ys0)) / den
        b = my - slope * mx
        parts.append(f'<line x1="{X(xmin):.1f}" y1="{Y(slope*xmin+b):.1f}" x2="{X(xmax):.1f}" y2="{Y(slope*xmax+b):.1f}" stroke="{PALETTE[0]}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    _legend(parts, leg, x0, y0 + 12)
    if xlabel:
        parts.append(f'<text x="{(x0+x1)/2}" y="{height-30}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{escape(xlabel)}</text>')
    if ylabel:
        parts.append(f'<text x="16" y="{(y0+y1)/2}" font-size="11.5" fill="{MUTED}" transform="rotate(-90 16 {(y0+y1)/2})" text-anchor="middle">{escape(ylabel)}</text>')
    return _svglines(parts, width, height, title, subtitle, footer)


def histogram(values, title, subtitle, footer, bins=20, xlabel="", yfmt=_fmt,
              width=920, height=470):
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    wbin = (hi - lo) / bins
    counts = [0] * bins
    for v in values:
        counts[min(int((v - lo) / wbin), bins - 1)] += 1
    if not xlabel:
        cats = [f"{lo+i*wbin:.2f}" for i in range(bins)]
        return bar_chart(cats, [("count", counts)], title, subtitle, footer,
                         ylabel="频数 / count", yfmt=yfmt, width=width,
                         height=height, show_every=max(1, bins // 12))
    L, R, T, B = 82, 26, 74, 88
    x0, x1, y0, y1 = L, width - R, T, height - B
    ymax = _nice(max(counts))
    parts = []
    for i in range(6):
        frac = i / 5
        y = y1 - frac * (y1 - y0)
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}"/>')
        parts.append(f'<text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">{yfmt(frac*ymax)}</text>')
    bw = (x1 - x0) / bins
    for i, c in enumerate(counts):
        yv = y1 - (c / (ymax or 1)) * (y1 - y0)
        parts.append(f'<rect x="{x0+i*bw:.1f}" y="{yv:.1f}" width="{bw*0.92:.1f}" height="{y1-yv:.1f}" fill="{PALETTE[0]}" fill-opacity="0.8" rx="1"/>')
    for i in range(0, bins + 1, max(1, bins // 8)):
        x = x0 + i * bw
        parts.append(f'<text x="{x:.1f}" y="{y1+20}" text-anchor="middle" font-size="10.5" fill="{MUTED}">{lo+(hi-lo)*i/bins:.2f}</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}"/>')
    parts.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}"/>')
    parts.append(f'<text x="{(x0+x1)/2}" y="{height-32}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{escape(xlabel)}</text>')
    return _svglines(parts, width, height, title, subtitle, footer)


def donut_chart(labels, values, title, subtitle, footer, width=920, height=470):
    cx, cy, r, rw = width / 2 - 80, height / 2 + 6, 128, 60
    total = sum(values) or 1
    parts = []
    ang = -math.pi / 2
    for i, (lab, v) in enumerate(zip(labels, values)):
        frac = v / total
        a2 = ang + frac * 2 * math.pi
        large = 1 if frac > 0.5 else 0
        x1 = cx + r * math.cos(ang); y1 = cy + r * math.sin(ang)
        x2 = cx + r * math.cos(a2); y2 = cy + r * math.sin(a2)
        color = PALETTE[i % len(PALETTE)]
        parts.append(f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{color}" stroke-width="{rw}"/>')
        mid = (ang + a2) / 2
        lx = cx + (r + 24) * math.cos(mid); ly = cy + (r + 24) * math.sin(mid)
        anchor = "start" if math.cos(mid) >= 0 else "end"
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="12" fill="{INK}">{escape(lab)} {frac*100:.1f}%</text>')
        ang = a2
    parts.append(f'<text x="{cx}" y="{cy}" text-anchor="middle" font-size="12" fill="{MUTED}">total</text>')
    parts.append(f'<text x="{cx}" y="{cy+20}" text-anchor="middle" font-size="15" font-weight="700" fill="{INK}">{_fmt(total)}</text>')
    return _svglines(parts, width, height, title, subtitle, footer)
