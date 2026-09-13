"""Generate an animated 'convolution kernel scanning a feature map' banner SVG.

The whole animation runs on ONE 7.2s master timeline so the kernel position and
the output-map activations stay perfectly in sync (36 steps x 0.2s).
"""

W, H = 1000, 300
CELL, GAP = 18, 2
STEP = CELL + GAP          # 20
N_IN, K, N_OUT = 8, 3, 6   # 8x8 input, 3x3 kernel, 6x6 output (valid conv)
STEPS = N_OUT * N_OUT      # 36
DT = 0.2
DUR = STEPS * DT           # 7.2s

IN_X, IN_Y = 52, 96
OUT_X, OUT_Y = 336, 116

NAME     = "FirstKhoi"
SUBTITLE = "Vietnam"        # doi thanh "Ten That &#183; Vietnam" neu muon

BG_A, BG_B = "#0D1117", "#131A24"
GRID = "#1F2A38"
ACCENT = "#7C3AED"
CYAN = "#22D3EE"
TEXT = "#E6EDF3"
MUTED = "#7D8590"

p = []
a = p.append

a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
  f'role="img" aria-label="{NAME} - Computer Vision and Deep Learning">')

# ---------- defs ----------
a('<defs>')
a(f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
  f'<stop offset="0%" stop-color="{BG_A}"/><stop offset="100%" stop-color="{BG_B}"/></linearGradient>')
a(f'<linearGradient id="name" x1="0" y1="0" x2="1" y2="0">'
  f'<stop offset="0%" stop-color="{CYAN}"/><stop offset="55%" stop-color="#A78BFA"/>'
  f'<stop offset="100%" stop-color="{ACCENT}"/></linearGradient>')
a(f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
  f'<stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>'
  f'<stop offset="50%" stop-color="{CYAN}" stop-opacity=".55"/>'
  f'<stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>')
a(f'<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
  f'<feGaussianBlur stdDeviation="3.2" result="b"/>'
  f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
a('</defs>')

# ---------- background ----------
a(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>')
a(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="{GRID}" stroke-width="1.5"/>')

# faint blueprint grid
a(f'<g stroke="{GRID}" stroke-width="1" opacity=".45">')
for x in range(0, W, 40):
    a(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
for y in range(0, H, 40):
    a(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
a('</g>')

# corner ticks
a(f'<g stroke="{ACCENT}" stroke-width="2" opacity=".8" fill="none">')
a('<path d="M18 44 L18 22 L40 22"/><path d="M982 44 L982 22 L960 22"/>')
a('<path d="M18 256 L18 278 L40 278"/><path d="M982 256 L982 278 L960 278"/>')
a('</g>')

# ---------- labels ----------
mono = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"
a(f'<text x="{IN_X}" y="{IN_Y-16}" font-family="{mono}" font-size="12" fill="{MUTED}" '
  f'letter-spacing="1.5">INPUT 8x8</text>')
a(f'<text x="{OUT_X}" y="{OUT_Y-16}" font-family="{mono}" font-size="12" fill="{MUTED}" '
  f'letter-spacing="1.5">FEATURE MAP 6x6</text>')

# ---------- input feature map ----------
a('<g id="input">')
for r in range(N_IN):
    for c in range(N_IN):
        x = IN_X + c * STEP
        y = IN_Y + r * STEP
        # static pseudo-random-ish texture so it reads as "data"
        o = 0.10 + ((r * 7 + c * 3) % 5) * 0.055
        a(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
          f'fill="{CYAN}" opacity="{o:.3f}"/>')
a('</g>')

# ---------- sliding kernel ----------
ksize = K * STEP - GAP  # 58
vals = []
for r in range(N_OUT):
    for c in range(N_OUT):
        vals.append(f"{c*STEP},{r*STEP}")
values = ";".join(vals)

a(f'<g transform="translate(0,0)">')
a(f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
  f'values="{values}" dur="{DUR}s" repeatCount="indefinite"/>')
a('<g filter="url(#glow)">')
a(f'<rect x="{IN_X-3}" y="{IN_Y-3}" width="{ksize+6}" height="{ksize+6}" rx="6" '
  f'fill="{ACCENT}" fill-opacity=".16" stroke="{ACCENT}" stroke-width="2"/>')
# kernel weight dots
for r in range(K):
    for c in range(K):
        cx = IN_X + c * STEP + CELL / 2
        cy = IN_Y + r * STEP + CELL / 2
        a(f'<circle cx="{cx}" cy="{cy}" r="2.2" fill="{ACCENT}"/>')
a('</g>')
a('</g>')
a(f'<text x="{IN_X+96}" y="{IN_Y+N_IN*STEP+22}" font-family="{mono}" font-size="11" '
  f'fill="{ACCENT}" text-anchor="middle" letter-spacing="1.2">kernel 3x3 | stride 1</text>')

# ---------- arrow ----------
ax0, ax1 = IN_X + N_IN * STEP + 16, OUT_X - 18
ay = IN_Y + N_IN * STEP / 2
a(f'<line x1="{ax0}" y1="{ay}" x2="{ax1-8}" y2="{ay}" stroke="{CYAN}" stroke-width="2" '
  f'stroke-dasharray="5 5" opacity=".85">'
  f'<animate attributeName="stroke-dashoffset" values="20;0" dur="1s" repeatCount="indefinite"/></line>')
a(f'<path d="M{ax1-8} {ay-5} L{ax1} {ay} L{ax1-8} {ay+5} Z" fill="{CYAN}"/>')
a(f'<text x="{(ax0+ax1)/2}" y="{ay-12}" font-family="{mono}" font-size="11" fill="{MUTED}" '
  f'text-anchor="middle">conv</text>')
a(f'<text x="{(ax0+ax1)/2}" y="{ay+22}" font-family="{mono}" font-size="11" fill="{MUTED}" '
  f'text-anchor="middle">relu</text>')

# ---------- output feature map (synced activations) ----------
a('<g id="output">')
for r in range(N_OUT):
    for c in range(N_OUT):
        idx = r * N_OUT + c
        x = OUT_X + c * STEP
        y = OUT_Y + r * STEP
        t0 = idx * DT / DUR
        t1 = (idx * DT + 0.12) / DUR
        k1 = max(0.0001, min(t0, 0.9994))
        k2 = max(k1 + 0.0002, min(t1, 0.9996))
        a(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{ACCENT}" '
          f'opacity="0.07">'
          f'<animate attributeName="opacity" values="0.07;0.07;1;0.55" '
          f'keyTimes="0;{k1:.4f};{k2:.4f};1" dur="{DUR}s" repeatCount="indefinite"/>'
          f'</rect>')
a('</g>')

# ---------- right: identity block ----------
TX = 560
a(f'<text x="{TX}" y="86" font-family="{mono}" font-size="12" fill="{MUTED}" letter-spacing="2">'
  f'$ whoami</text>')

FONT_PX = 48
adv = FONT_PX * 0.60 - 1          # mono advance width, minus letter-spacing
name_w = len(NAME) * adv
a(f'<text x="{TX}" y="140" font-family="{mono}" font-size="{FONT_PX}" font-weight="700" '
  f'fill="url(#name)" letter-spacing="-1">{NAME}</text>')
a(f'<rect x="{TX + name_w + 8:.0f}" y="112" width="13" height="34" fill="{CYAN}">'
  f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>')

a(f'<text x="{TX}" y="170" font-family="{mono}" font-size="15" fill="{TEXT}" letter-spacing=".5">'
  f'{SUBTITLE}</text>')

a(f'<line x1="{TX}" y1="188" x2="{W-52}" y2="188" stroke="{GRID}" stroke-width="1.5"/>')
a(f'<rect x="{TX}" y="185.5" width="150" height="5" fill="url(#sweep)">'
  f'<animate attributeName="x" values="{TX};{W-202};{TX}" dur="4.5s" repeatCount="indefinite"/></rect>')

a(f'<text x="{TX}" y="214" font-family="{mono}" font-size="14" fill="#A78BFA" letter-spacing=".5">'
  f'Computer Vision &#215; Deep Learning &#215; Research</text>')

chips = ["PyTorch", "OpenCV", "CUDA", "PostGIS"]
cx = TX
for ch in chips:
    w = 9 + len(ch) * 7.4
    a(f'<rect x="{cx}" y="234" width="{w:.0f}" height="24" rx="12" fill="{ACCENT}" '
      f'fill-opacity=".13" stroke="{ACCENT}" stroke-opacity=".45"/>')
    a(f'<text x="{cx + w/2:.0f}" y="250" font-family="{mono}" font-size="11" fill="#C4B5FD" '
      f'text-anchor="middle">{ch}</text>')
    cx += w + 9

a('</svg>')

svg = "\n".join(p)
with open("/home/claude/profile/assets/conv-banner.svg", "w") as f:
    f.write(svg)
print("written", len(svg), "bytes")
