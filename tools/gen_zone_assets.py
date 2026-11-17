#!/usr/bin/env python3
"""Genera el arte y el audio de la etapa 5 (Cripta, Capilla, enemigos, jefe,
Baldwin, historia y audio). Todo sale de dibujo y síntesis por código: no usa
archivos de terceros ni servicios externos. Semillas fijas: volver a ejecutarlo
reproduce los mismos archivos.

    python3 tools/gen_zone_assets.py

Requiere Pillow y numpy. Paleta y reglas: docs/arte.md. También escribe las
hojas de contacto (docs/etapa5/previews/) y docs/etapa5/assets_manifest.md.
"""
import math
import random
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SPR = ROOT / "Sprites"
CRIPTA = SPR / "Environment/Cripta"
CAPILLA = SPR / "Environment/Capilla"
COMMON = SPR / "Environment/Common"
ENEMY = SPR / "Enemies"
BOSS = SPR / "Bosses"
WEAPONS = SPR / "Items/Weapons"
STORY = SPR / "Story"
BALDWIN = SPR / "Characters/Baldwin"
AUDIO = ROOT / "Audio"
PREV = ROOT / "docs/etapa5/previews"
DOCS5 = ROOT / "docs/etapa5"

# Paleta de la guía de arte
BG = (0x15, 0x19, 0x24)
BG_FAR = (0x1C, 0x22, 0x30)
STONE_D = (0x23, 0x2B, 0x37)
STONE = (0x30, 0x3B, 0x4A)
STONE_L = (0x3E, 0x4B, 0x5E)
STEEL = (0x6D, 0x82, 0x97)
IVORY = (0xE5, 0xD6, 0xB3)
IVORY_D = (0xA9, 0x9C, 0x80)
COPPER = (0xB9, 0x6A, 0x47)
COPPER_D = (0x7A, 0x3A, 0x22)
EMBER = (0xF0, 0xA7, 0x58)
EMBER_L = (0xFF, 0xD5, 0x9A)
# Tonos intermedios derivados
STEEL_D = (0x4A, 0x5C, 0x70)
STEEL_L = (0x92, 0xA6, 0xBA)
COPPER_DD = (0x55, 0x28, 0x18)
# Cripta (tira a cobre): fondos oscuros cálidos, plano de juego más claro
CR_BG = (0x1A, 0x16, 0x1F)
CR_FAR = (0x22, 0x1C, 0x27)
CR_FAR_L = (0x2A, 0x23, 0x2F)
CR_D = (0x2B, 0x23, 0x2A)
CR = (0x3C, 0x30, 0x35)
CR_L = (0x52, 0x40, 0x41)
CR_EDGE = (0xC8, 0x92, 0x68)
BONE_DIM = (0x4D, 0x43, 0x3E)
# Capilla (tira a marfil y acero): mármol azulado
MA_BG = (0x1D, 0x24, 0x32)
MA_D = (0x2D, 0x38, 0x48)
MA = (0x44, 0x52, 0x66)
MA_L = (0x5E, 0x6E, 0x84)
GLASS = [(0x3A, 0x2A, 0x22), (0x47, 0x31, 0x25), (0x2F, 0x25, 0x26), (0x34, 0x2D, 0x3B)]


def rgba(c, a=255):
    return (c[0], c[1], c[2], a)


def new(w, h, fill=None):
    return Image.new("RGBA", (w, h), rgba(fill) if fill else (0, 0, 0, 0))


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def rect(d, x0, y0, x1, y1, c):
    """Rectángulo con extremos incluidos."""
    d.rectangle((x0, y0, x1, y1), fill=c if len(c) == 4 else rgba(c))


def poly(d, pts, c):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=c if len(c) == 4 else rgba(c))


def line(d, p0, p1, c, w=1):
    p0 = (int(round(p0[0])), int(round(p0[1])))
    p1 = (int(round(p1[0])), int(round(p1[1])))
    col = c if len(c) == 4 else rgba(c)
    d.line([p0, p1], fill=col, width=w)
    if w >= 3:
        r = (w - 1) / 2.0
        for p in (p0, p1):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col)


def disc(d, cx, cy, r, c):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c if len(c) == 4 else rgba(c))


def put(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((int(x), int(y)), c if len(c) == 4 else rgba(c))


def bezier(p0, c, p1, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]))
    return pts


def overlay(img, fn):
    """Dibuja en una capa aparte y la compone con alfa."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer))
    img.alpha_composite(layer)


def speckle(img, color, count, seed, area=None):
    rnd = random.Random(seed)
    w, h = img.size
    x0, y0, x1, y1 = area or (0, 0, w - 1, h - 1)
    for _ in range(count):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        if img.getpixel((x, y))[3] > 0:
            img.putpixel((x, y), rgba(color))


def vgrad(w, h, stops):
    ys = np.linspace(0, 1, h)
    arr = np.zeros((h, w, 4), np.uint8)
    for ch in range(3):
        col = np.interp(ys, [s[0] for s in stops], [s[1][ch] for s in stops])
        arr[:, :, ch] = np.round(col)[:, None]
    arr[..., 3] = 255
    return Image.fromarray(arr, "RGBA")


def arch_masks(w, h, cx, spring_y, half_w, thickness):
    """Arco apuntado (dos arcos de radio 2*half_w): máscara de la banda y del interior."""
    r_out = 2.0 * half_w
    r_in = r_out - thickness
    apex = spring_y - half_w * math.sqrt(3.0)
    ys, xs = np.mgrid[0:h, 0:w]
    inside_box = (ys >= int(apex) - 1) & (ys < spring_y) & (xs >= cx - half_w) & (xs < cx + half_w)
    center_x = np.where(xs < cx, cx + half_w, cx - half_w)
    dist = np.hypot(xs + 0.5 - center_x, ys + 0.5 - spring_y)
    return inside_box & (dist >= r_in) & (dist <= r_out), inside_box & (dist < r_in)


def paint(img, mask, color):
    m = Image.fromarray((mask * 255).astype("uint8"), "L")
    img.paste(rgba(color) if len(color) == 3 else color, mask=m)


def pointed_arch(img, cx, spring_y, half_w, thickness, color, fill_inside=None):
    band, inside = arch_masks(img.width, img.height, cx, spring_y, half_w, thickness)
    if fill_inside:
        paint(img, inside, fill_inside)
    paint(img, band, color)


def rim_light(img, color, alpha=200):
    """Contorno claro de 1 px por arriba y a los lados (no por abajo)."""
    a = np.array(img)
    op = a[..., 3] > 0
    p = np.pad(op, 1)
    near = p[1:-1, :-2] | p[1:-1, 2:] | p[2:, 1:-1]  # vecino opaco a izq., der. o abajo
    rim = near & ~op
    a[rim] = (color[0], color[1], color[2], alpha)
    img.paste(Image.fromarray(a, "RGBA"))


def halo(img, cx, cy, radii, alphas, color):
    def f(d):
        for r, a in zip(radii, alphas):
            disc(d, cx, cy, r, rgba(color, a))
    overlay(img, f)


def periodic(period, fn, h=360, base=None):
    """Compone un fondo de 640 px que encaja en mosaico: fn(img, x0, k) dibuja el
    elemento del periodo k (con k variando módulo 640/period)."""
    n = 640 // period
    w = 640 + 2 * period
    img = base.copy() if base else new(w, h)
    if base is not None and img.width != w:
        raise ValueError("base de ancho incorrecto")
    for j in range(-1, n + 1):
        fn(img, j * period + period, j % n)
    return img.crop((period, 0, period + 640, h))


def check_seam(img):
    """Diferencia media entre la última y la primera columna (para validar el mosaico)."""
    a = np.array(img).astype(int)
    return float(np.abs(a[:, -1] - a[:, 0]).mean())


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


# ------------------------------------------------------------------ tiles 16 px

def brick_tile(rows, joints, colors, mortar, seed, top_edge=None):
    """rows: [(y0, y1)] de cada hilada; joints: juntas verticales por hilada."""
    img = new(16, 16, mortar)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for r, (y0, y1) in enumerate(rows):
        js = sorted(joints[r % len(joints)])
        for i, j in enumerate(js):
            nxt = js[(i + 1) % len(js)]
            xa, xb = j + 1, (nxt - 1 if nxt > j else nxt + 15)
            col = colors[rnd.randrange(len(colors))]
            for x in range(xa, xb + 1):
                for y in range(y0, y1 + 1):
                    c = lerp(col, IVORY, 0.10) if y == y0 else col
                    img.putpixel((x % 16, y), rgba(c))
    if top_edge:
        for y, c in enumerate(top_edge):
            rect(d, 0, y, 15, y, c)
    return img


def make_cripta_tiles():
    cols = [CR, lerp(CR, CR_L, 0.5), lerp(CR, CR_D, 0.5)]
    top = brick_tile([(2, 8), (10, 14)], [[0, 8], [4, 12]], cols, CR_BG, 11, [CR_EDGE, COPPER])
    speckle(top, CR_L, 5, 12, (0, 3, 15, 14))
    save(top, CRIPTA / "floor_top.png")
    fill = brick_tile([(0, 6), (8, 14)], [[0, 8], [4, 12]], [CR_D, lerp(CR_D, CR, 0.5), lerp(CR_D, CR_BG, 0.5)], CR_BG, 13)
    speckle(fill, CR, 4, 14)
    save(fill, CRIPTA / "floor_fill.png")
    # Losa de plataforma: borde claro, cuerpo con junta, vientre oscuro y ménsulas
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    rect(d, 0, 0, 15, 0, CR_EDGE)
    rect(d, 0, 1, 15, 1, COPPER)
    rect(d, 0, 2, 15, 9, CR)
    rect(d, 0, 2, 15, 2, CR_L)
    rect(d, 8, 3, 8, 9, CR_D)
    rect(d, 0, 10, 15, 10, CR_BG)
    rect(d, 0, 11, 15, 13, CR_D)
    rect(d, 0, 14, 15, 15, CR_BG)
    rect(d, 2, 11, 3, 15, CR)  # ménsulas bajo la losa
    rect(d, 12, 11, 13, 15, CR)
    put(img, 5, 5, CR_L)
    put(img, 11, 7, CR_L)
    save(img, CRIPTA / "platform.png")


def marble_tile(rows, ma, mb, mortar, seed, top_edge=None):
    img = new(16, 16, mortar)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for r, (y0, y1) in enumerate(rows):
        for c in range(2):
            col = ma if (r + c) % 2 == 0 else mb
            x0 = c * 8
            rect(d, x0, y0, x0 + 6, y1, col)
            rect(d, x0, y0, x0 + 6, y0, lerp(col, IVORY, 0.18))
            rect(d, x0, y0, x0, y1, lerp(col, IVORY, 0.08))
            for _ in range(2):  # vena
                vx, vy = x0 + rnd.randint(1, 5), rnd.randint(y0 + 1, y1 - 1)
                put(img, vx, vy, lerp(col, IVORY, 0.25))
                put(img, min(x0 + 6, vx + 1), min(y1, vy + 1), lerp(col, IVORY, 0.18))
    if top_edge:
        for y, c in enumerate(top_edge):
            rect(d, 0, y, 15, y, c)
    return img


def make_capilla_tiles():
    save(marble_tile([(2, 8), (10, 14)], MA, lerp(MA, MA_L, 0.45), MA_BG, 21, [IVORY, STEEL]), CAPILLA / "floor_top.png")
    save(marble_tile([(0, 6), (8, 14)], MA_D, lerp(MA_D, MA, 0.5), MA_BG, 22), CAPILLA / "floor_fill.png")
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    rect(d, 0, 0, 15, 0, IVORY)
    rect(d, 0, 1, 15, 1, STEEL)
    rect(d, 0, 2, 15, 9, MA)
    rect(d, 0, 2, 15, 2, MA_L)
    line(d, (3, 8), (6, 4), lerp(MA, IVORY, 0.3))
    line(d, (10, 9), (13, 5), lerp(MA, IVORY, 0.25))
    rect(d, 0, 10, 15, 10, MA_BG)
    rect(d, 0, 11, 15, 13, MA_D)
    rect(d, 0, 14, 15, 15, MA_BG)
    rect(d, 1, 11, 2, 15, MA)
    rect(d, 13, 11, 14, 15, MA)
    save(img, CAPILLA / "platform.png")


# ------------------------------------------------------------------ fondos

def niche(img, x, y, w=10, h=16, edge=CR_FAR_L, inner=(0x12, 0x10, 0x18), content=0):
    d = ImageDraw.Draw(img)
    rect(d, x - 1, y + 4, x + w, y + h, edge)
    d.ellipse((x - 1, y - 1, x + w, y + 9), fill=rgba(edge))
    rect(d, x, y + 5, x + w - 1, y + h, inner)
    d.ellipse((x, y, x + w - 1, y + 9), fill=rgba(inner))
    rect(d, x, y + 5, x + w - 1, y + h, inner)
    if content == 1:  # cráneo en penumbra
        rect(d, x + 3, y + h - 6, x + 6, y + h - 3, BONE_DIM)
        put(img, x + 3, y + h - 5, inner)
        put(img, x + 6, y + h - 5, inner)
    elif content == 2:  # brasa tenue al fondo
        put(img, x + 4, y + h - 2, (0x4A, 0x2C, 0x20))
        put(img, x + 5, y + h - 2, (0x3A, 0x2A, 0x22))
        put(img, x + 4, y + h - 3, (0x3A, 0x2A, 0x22))


def make_cripta_bg():
    far = vgrad(640 + 320, 360, [(0, CR_BG), (0.6, (0x1D, 0x18, 0x23)), (1, (0x26, 0x1E, 0x28))])

    def bay(img, x0, k):
        d = ImageDraw.Draw(img)
        # Bóveda de crucería: dos arcos apuntados concéntricos y nervios
        pointed_arch(img, x0 + 80, 200, 78, 9, CR_FAR_L, fill_inside=CR_FAR)
        pointed_arch(img, x0 + 80, 130, 46, 5, (0x2F, 0x27, 0x33), fill_inside=(0x1E, 0x19, 0x24))
        rect(d, x0 + 79, 40, x0 + 80, 76, (0x2F, 0x27, 0x33))  # clave
        # Pilar de arranque en el límite del periodo
        rect(d, x0 - 5, 190, x0 + 4, 359, CR_FAR_L)
        rect(d, x0 - 5, 190, x0 - 4, 359, (0x33, 0x2A, 0x36))
        rect(d, x0 - 7, 184, x0 + 6, 192, (0x33, 0x2A, 0x36))
        # Osario: hileras de nichos en penumbra
        rnd = random.Random(100 + k)
        for row, ny in enumerate((236, 268, 300)):
            for i in range(6):
                nx = x0 + 14 + i * 24 + (row % 2) * 6
                niche(img, nx, ny, content=rnd.choice([0, 0, 1, 1, 2]))
    img = periodic(160, bay, base=far)
    save(img.convert("RGBA"), CRIPTA / "bg_far.png")

    PIL_C, PIL_L, PIL_D = (0x2A, 0x22, 0x2B), (0x3C, 0x31, 0x3B), (0x1D, 0x18, 0x22)

    def bay_mid(img, x0, k):
        d = ImageDraw.Draw(img)
        # Pilar achaparrado con capitel escalonado
        rect(d, x0 + 6, 160, x0 + 29, 359, PIL_C)
        rect(d, x0 + 6, 160, x0 + 9, 359, PIL_L)
        rect(d, x0 + 26, 160, x0 + 29, 359, PIL_D)
        rect(d, x0 + 2, 150, x0 + 33, 158, PIL_C)
        rect(d, x0 + 2, 150, x0 + 33, 151, PIL_L)
        rect(d, x0 + 4, 158, x0 + 31, 161, PIL_D)
        rect(d, x0 + 3, 345, x0 + 32, 359, PIL_C)
        # Arco bajo de osario entre pilares
        pointed_arch(img, x0 + 83, 214, 53, 9, PIL_C)
        band, _ = arch_masks(img.width, img.height, x0 + 83, 214, 53, 3)
        paint(img, band, PIL_L)  # canto iluminado del intradós
        # Muro de huesos bajo el arco
        rect(d, x0 + 30, 300, x0 + 135, 359, (0x1B, 0x16, 0x20))
        rnd = random.Random(200 + k)
        for row in range(6):
            for i in range(13):
                sx = x0 + 31 + i * 8 + (row % 2) * 4
                sy = 302 + row * 9
                if sx + 6 > x0 + 135:
                    continue
                rect(d, sx, sy, sx + 5, sy + 4, BONE_DIM if rnd.random() > 0.15 else (0x38, 0x31, 0x32))
                put(img, sx + 1, sy + 2, (0x1B, 0x16, 0x20))
                put(img, sx + 4, sy + 2, (0x1B, 0x16, 0x20))
        rect(d, x0 + 30, 296, x0 + 135, 300, PIL_L)
        # Brasas dormidas en un hueco
        put(img, x0 + 70, 320, (0x6A, 0x3A, 0x26))
    save(periodic(128, bay_mid), CRIPTA / "bg_mid.png")


def make_capilla_bg():
    far = vgrad(640 + 320, 360, [(0, (0x12, 0x16, 0x20)), (0.5, BG_FAR), (1, (0x24, 0x2C, 0x3C))])
    FR = (0x2A, 0x33, 0x43)
    lead = (0x16, 0x1A, 0x25)

    def bay(img, x0, k):
        d = ImageDraw.Draw(img)
        # Arcada ciega de la nave
        pointed_arch(img, x0 + 80, 210, 76, 8, (0x25, 0x2D, 0x3C), fill_inside=(0x19, 0x1E, 0x2A))
        # Vitral apagado: lanceta con plomos y paños de brasa tenue
        cx = x0 + 80
        pointed_arch(img, cx, 170, 22, 5, FR, fill_inside=GLASS[0])
        rect(d, cx - 22, 170, cx + 21, 270, GLASS[0])
        rect(d, cx - 22, 170, cx - 18, 270, FR)
        rect(d, cx + 17, 170, cx + 21, 270, FR)
        _, inside = arch_masks(img.width, img.height, cx, 170, 22, 5)
        rnd = random.Random(300 + k)
        ys, xs = np.mgrid[0:img.height, 0:img.width]
        glass_box = (xs >= cx - 17) & (xs <= cx + 16) & (((ys >= 170) & (ys <= 270)) | inside)
        for gy in range(120, 272, 12):
            for gx in range(cx - 17, cx + 17, 8):
                col = GLASS[rnd.randrange(4)]
                cell = glass_box & (xs >= gx) & (xs < gx + 8) & (ys >= gy) & (ys < gy + 12)
                paint(img, cell, col)
        paint(img, glass_box & ((xs % 8 == (cx - 17) % 8) | (ys % 12 == 0)), lead)  # plomos
        paint(img, glass_box & ((xs == cx - 1) | (xs == cx)), lead)  # montante central
        # Brillo más cálido en el rosetón de la lanceta
        disc(d, cx, 150, 5, rgba((0x4A, 0x32, 0x26)))
        disc(d, cx, 150, 2, rgba((0x5A, 0x3A, 0x28)))
        # Columnillas de arranque
        rect(d, x0 - 3, 200, x0 + 2, 359, (0x25, 0x2D, 0x3C))
        rect(d, x0 - 5, 196, x0 + 4, 201, FR)
        # Suelo lejano
        rect(d, x0, 330, x0 + 159, 359, (0x20, 0x27, 0x35))
    img = periodic(160, bay, base=far)
    save(img, CAPILLA / "bg_far.png")

    CM, CML, CMD = (0x2B, 0x35, 0x45), (0x3B, 0x47, 0x5B), (0x1D, 0x25, 0x32)

    def col_mid(img, x0, k):
        d = ImageDraw.Draw(img)
        cx = x0 + 64
        pointed_arch(img, x0, 112, 60, 6, CMD)
        rect(d, cx - 10, 104, cx + 10, 112, CM)  # capitel
        rect(d, cx - 12, 98, cx + 12, 103, CML)
        for vx in (cx - 14, cx + 13):  # volutas
            disc(d, vx, 101, 3, rgba(CM))
        rect(d, cx - 8, 112, cx + 8, 340, CM)
        rect(d, cx - 8, 112, cx - 6, 340, CML)  # canto iluminado
        rect(d, cx + 6, 112, cx + 8, 340, CMD)
        for fx in (cx - 3, cx, cx + 3):  # estrías
            rect(d, fx, 114, fx, 338, (0x25, 0x2E, 0x3C))
        rect(d, cx - 12, 340, cx + 12, 348, CML)
        rect(d, cx - 14, 348, cx + 14, 359, CM)
    save(periodic(128, col_mid), CAPILLA / "bg_mid.png")


# ------------------------------------------------------------------ utilería

def skull(d, x, y, col=BONE_DIM, dark=(0x12, 0x10, 0x18), eye=None):
    d.ellipse((x, y, x + 6, y + 5), fill=rgba(col))
    rect(d, x + 2, y + 5, x + 4, y + 6, col)
    for ex in (x + 1, x + 4):
        rect(d, ex, y + 2, ex + 1, y + 3, rgba(eye) if eye else rgba(dark))
    put_pixel = d.point
    put_pixel((x + 3, y + 4), rgba(dark))


def make_cripta_props():
    # Nicho de calaveras 32x32
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    rect(d, 0, 0, 31, 31, CR)
    rect(d, 0, 0, 31, 1, CR_L)
    rect(d, 0, 30, 31, 31, CR_D)
    rect(d, 3, 4, 28, 28, (0x12, 0x10, 0x18))
    d.ellipse((3, 2, 28, 14), fill=rgba((0x12, 0x10, 0x18)))
    rect(d, 3, 8, 28, 28, (0x12, 0x10, 0x18))
    rect(d, 3, 28, 28, 28, CR_D)
    for row, y in enumerate((9, 16, 23)):
        n = 3 if row == 0 else 3
        for i in range(n):
            x = 5 + i * 8 + (4 if row == 1 else 0)
            if x + 7 > 28:
                continue
            skull(d, x, y, col=lerp(IVORY_D, CR, 0.25), eye=EMBER if (row == 2 and i == 1) else None)
    save(img, CRIPTA / "niche_skulls.png")

    # Ataúd 32x16 (lateral)
    img = new(32, 16)
    d = ImageDraw.Draw(img)
    poly(d, [(1, 6), (3, 3), (28, 3), (31, 6), (31, 15), (1, 15)], COPPER_D)
    rect(d, 3, 3, 28, 4, COPPER)  # tapa con luz
    rect(d, 1, 6, 30, 6, COPPER_DD)
    for x in (6, 15, 24):  # flejes de hierro
        rect(d, x, 3, x + 1, 15, STEEL_D)
        put(img, x, 3, STEEL)
    for y in (9, 12):
        rect(d, 2, y, 30, y, COPPER_DD)
    for x, y in ((6, 8), (15, 8), (24, 8)):
        put(img, x, y, COPPER)
    rect(d, 1, 14, 30, 15, COPPER_DD)
    put(img, 28, 5, EMBER)
    rim_light(img, STEEL, 150)
    save(img, CRIPTA / "coffin.png")

    # Cadena colgante 8x64
    img = new(8, 64)
    d = ImageDraw.Draw(img)
    rect(d, 1, 0, 6, 1, STEEL)
    for i in range(8):
        y = 2 + i * 8 if i < 7 else 58
        if i % 2 == 0:  # eslabón de frente
            d.rectangle((2, y, 5, y + 7), outline=rgba(STEEL), fill=None)
            rect(d, 3, y + 2, 4, y + 5, (0, 0, 0, 0))
            put(img, 2, y + 1, STEEL_L)
            put(img, 2, y + 2, STEEL_L)
        else:  # eslabón de canto
            rect(d, 3, y, 4, y + 7, STEEL_D)
            put(img, 3, y + 1, STEEL)
    rect(d, 1, 62, 6, 63, STEEL_D)
    save(img, CRIPTA / "chain.png")

    # Velas en el suelo 16x16
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    rect(d, 1, 14, 14, 15, COPPER_D)  # cera derramada
    rect(d, 2, 13, 13, 13, IVORY_D)
    for x, h in ((2, 7), (7, 10), (12, 6)):
        top = 13 - h
        rect(d, x, top, x + 2, 12, IVORY)
        rect(d, x + 2, top, x + 2, 12, IVORY_D)
        put(img, x + 1, top + 3, IVORY_D)
        rect(d, x + 1, top - 3, x + 1, top - 1, EMBER)
        put(img, x + 1, top - 2, EMBER_L)
        put(img, x + 1, top - 4, EMBER)
    save(img, CRIPTA / "candles.png")


def make_capilla_props():
    # Atril 16x32
    img = new(16, 32)
    d = ImageDraw.Draw(img)
    rect(d, 6, 13, 9, 29, MA)
    rect(d, 6, 13, 6, 29, MA_L)
    rect(d, 3, 28, 12, 31, MA_L)
    rect(d, 4, 26, 11, 27, MA)
    poly(d, [(0, 11), (15, 5), (15, 8), (0, 14)], MA_L)
    poly(d, [(1, 10), (14, 4), (14, 6), (1, 12)], IVORY)  # libro abierto
    line(d, (7, 8), (7, 11), IVORY_D)
    rect(d, 8, 4, 8, 6, COPPER)  # marcapáginas
    put(img, 3, 9, IVORY_D)
    put(img, 11, 5, IVORY_D)
    put(img, 8, 7, EMBER)
    rim_light(img, STEEL, 120)
    save(img, CAPILLA / "lectern.png")

    # Altar 48x32
    img = new(48, 32)
    d = ImageDraw.Draw(img)
    rect(d, 0, 8, 47, 11, IVORY)
    rect(d, 0, 11, 47, 11, IVORY_D)
    rect(d, 2, 12, 45, 28, MA_L)
    rect(d, 2, 12, 45, 13, STEEL)
    rect(d, 0, 29, 47, 31, MA)
    rect(d, 0, 29, 47, 29, MA_L)
    rect(d, 9, 12, 38, 24, IVORY)  # paño del altar
    rect(d, 9, 12, 38, 13, IVORY_D)
    for x in range(9, 39, 3):
        rect(d, x, 22, x, 24, IVORY_D)
    rect(d, 9, 25, 38, 25, COPPER)
    poly(d, [(21, 18), (26, 18), (26, 20), (21, 20)], COPPER)
    rect(d, 23, 14, 24, 21, COPPER_D)
    d.rectangle((22, 15, 25, 16), fill=rgba(COPPER))
    for x in (4, 41):  # candeleros
        rect(d, x, 3, x + 2, 7, IVORY)
        rect(d, x + 1, 0, x + 1, 2, EMBER)
        put(img, x + 1, 1, EMBER_L)
    # cáliz con brasa encima del paño
    rect(d, 22, 4, 25, 7, COPPER)
    poly(d, [(21, 4), (26, 4), (24, 0), (23, 0)], EMBER)
    put(img, 23, 2, EMBER_L)
    rim_light(img, STEEL, 120)
    save(img, CAPILLA / "altar.png")

    # Estatua 32x64: caballero orante con espada clavada
    img = new(32, 64)
    d = ImageDraw.Draw(img)
    rect(d, 3, 56, 28, 63, MA)
    rect(d, 3, 56, 28, 57, MA_L)
    rect(d, 1, 61, 30, 63, MA_D)
    poly(d, [(9, 56), (23, 56), (22, 34), (10, 34)], MA_L)  # faldón
    line(d, (13, 38), (12, 55), MA)
    line(d, (19, 38), (20, 55), MA)
    poly(d, [(8, 36), (24, 36), (22, 24), (10, 24)], lerp(MA_L, IVORY, 0.2))  # torso
    disc(d, 8, 26, 4, rgba(MA_L))  # hombreras
    disc(d, 24, 26, 4, rgba(MA_L))
    d.ellipse((11, 9, 21, 23), fill=rgba(lerp(MA_L, IVORY, 0.25)))  # yelmo
    rect(d, 13, 15, 19, 16, MA_D)
    rect(d, 15, 6, 17, 9, MA_L)  # cimera
    # espada clavada entre las manos
    rect(d, 15, 30, 16, 55, STEEL_L)
    rect(d, 15, 30, 15, 55, IVORY)
    rect(d, 11, 29, 20, 30, COPPER)
    rect(d, 14, 25, 17, 28, COPPER_D)
    rect(d, 12, 28, 19, 29, lerp(MA_L, IVORY, 0.4))  # manos juntas
    line(d, (9, 29), (14, 28), MA_L, 2)
    line(d, (23, 29), (18, 28), MA_L, 2)
    rim_light(img, STEEL, 150)
    save(img, CAPILLA / "statue.png")


def make_inscription():
    img = new(32, 24)
    d = ImageDraw.Draw(img)
    rect(d, 2, 6, 29, 23, STONE)
    pointed_arch(img, 16, 12, 14, 3, STONE_L, fill_inside=STONE)
    rect(d, 2, 6, 29, 23, STONE)
    rect(d, 2, 12, 29, 23, STONE)
    rect(d, 2, 2, 29, 5, (0, 0, 0, 0))
    pointed_arch(img, 16, 14, 14, 3, STONE_L, fill_inside=STONE)
    rect(d, 2, 14, 29, 23, STONE)
    rect(d, 2, 14, 3, 23, STONE_L)
    rect(d, 28, 14, 29, 23, STONE_D)
    rect(d, 2, 22, 29, 23, STONE_D)
    rnd = random.Random(55)
    for row, y in enumerate((7, 12, 17)):
        n = 3 if row == 0 else 5
        for i in range(n):
            x0 = 16 - (n * 5 - 1) // 2 + i * 5
            col = IVORY if rnd.random() > 0.3 else IVORY_D
            rect(img and ImageDraw.Draw(img), x0 + 1, y, x0 + 1, y + 4, col)
            for _ in range(rnd.randint(1, 2)):
                k = rnd.randrange(4)
                dd = ImageDraw.Draw(img)
                if k == 0:
                    dd.point([(x0, y + 1), (x0 + 2, y + 1)], fill=rgba(col))
                elif k == 1:
                    dd.point([(x0 + 2, y), (x0, y + 4)], fill=rgba(col))
                elif k == 2:
                    dd.point([(x0, y), (x0 + 2, y + 4)], fill=rgba(col))
                else:
                    dd.point([(x0, y + 3), (x0 + 2, y + 2)], fill=rgba(col))
    rim_light(img, STEEL, 150)
    save(img, COMMON / "inscription.png")


# ------------------------------------------------------------------ enemigos

def censer(img, cx, cy, r, hot):
    """Incensario: cuerpo de cobre con calados de brasa; hot=2 lo enciende a pleno."""
    if hot >= 1:
        halo(img, cx, cy, [r + 5, r + 3] if hot == 1 else [r + 7, r + 4], [40, 80] if hot == 1 else [70, 120], EMBER)
    d = ImageDraw.Draw(img)
    disc(d, cx, cy, r, COPPER)
    d.pieslice((cx - r, cy - r, cx + r, cy + r), 200, 340, fill=rgba(STEEL))
    rect(d, cx - r + 1, cy, cx + r - 1, cy, COPPER_D)
    for ox in (-r // 2, 0, r // 2):
        put(img, cx + ox, cy + 1, EMBER if hot else COPPER_D)
        if hot >= 2:
            put(img, cx + ox, cy + 2, EMBER_L)
    if hot >= 1:
        put(img, cx, cy - r - 1, EMBER_L)


def make_acolyte():
    poses = [
        dict(lean=0, drop=0, eyes=COPPER, hand=(43, 33), elbow=(40, 29), censer=(44, 40, 4, 0), chain=((43, 33), (44, 36))),
        dict(lean=-2, drop=2, eyes=EMBER_L, hand=(38, 12), elbow=(42, 19), censer=(36, 4, 5, 2), chain=((38, 12), (37, 8))),
        dict(lean=3, drop=1, eyes=EMBER_L, hand=(46, 16), elbow=(43, 20), censer=(48, 27, 3, 1), chain=((46, 17), (47, 24))),
        dict(lean=4, drop=4, eyes=COPPER_D, hand=(45, 36), elbow=(43, 31), censer=(47, 44, 4, 0), chain=((45, 36), (46, 40))),
    ]
    sheet = new(64 * 4, 48)
    for i, p in enumerate(poses):
        img = new(64, 48)
        d = ImageDraw.Draw(img)
        l, dr = p["lean"], p["drop"]
        # túnica acampanada con ribete de brasa en el bajo
        poly(d, [(27 + l, 21 + dr), (38 + l, 21 + dr), (42, 47), (22, 47)], COPPER_D)
        poly(d, [(27 + l, 21 + dr), (30 + l, 21 + dr), (26, 47), (22, 47)], COPPER_DD)
        line(d, (34 + l, 26 + dr), (37, 46), COPPER, 1)
        rect(d, 22, 45, 42, 46, COPPER_DD)
        for x in range(23, 42, 4):
            put(img, x, 46, COPPER)
        # cuerda
        line(d, (28 + l, 30 + dr), (38 + l, 31 + dr), IVORY_D, 1)
        # brazo trasero
        line(d, (28 + l, 24 + dr), (27 + l, 33 + dr), COPPER_DD, 3)
        # capucha picuda (distinta del custodio, que la lleva redonda)
        poly(d, [(33 + l, 6 + dr), (37 + l, 12 + dr), (39 + l, 21 + dr), (27 + l, 21 + dr), (28 + l, 13 + dr)], COPPER_D)
        poly(d, [(33 + l, 6 + dr), (35 + l, 10 + dr), (30 + l, 14 + dr), (28 + l, 13 + dr)], COPPER)
        d.ellipse((33 + l, 12 + dr, 39 + l, 20 + dr), fill=rgba(BG))
        for ex in (35, 37):
            rect(d, ex + l, 15 + dr, ex + l, 16 + dr, p["eyes"])
        # brazo delantero y cadena
        sx, sy = 35 + l, 24 + dr
        line(d, (sx, sy), p["elbow"], COPPER_D, 3)
        line(d, p["elbow"], p["hand"], COPPER_D, 3)
        disc(d, p["hand"][0], p["hand"][1], 1, rgba(COPPER))
        line(d, p["chain"][0], p["chain"][1], STEEL, 1)
        cx, cy, r, hot = p["censer"]
        if i == 2:  # mano abierta lanzando brasa: chispas junto al punto de nacimiento del proyectil
            for dx, dy in ((2, -1), (3, 1), (2, 3), (4, -3)):
                put(img, 46 + dx, 16 + dy, EMBER_L if dx == 2 else EMBER)
        censer(img, cx, cy, r, hot)
        rim_light(img, STEEL)
        sheet.paste(img, (i * 64, 0))
    save(sheet, ENEMY / "acolito.png")

    # Proyectil: bola de brasa 12x12, 2 cuadros (el segundo parpadea)
    sheet = new(24, 12)
    for f in range(2):
        img = new(12, 12)
        d = ImageDraw.Draw(img)
        r = 5 if f == 0 else 4
        disc(d, 6, 6, r, COPPER)
        disc(d, 6, 6, r - 1, EMBER)
        disc(d, 6, 6, 2 if f == 0 else 1, EMBER_L)
        if f == 0:
            put(img, 6, 0, EMBER)
            put(img, 6, 11, COPPER)
            put(img, 0, 6, COPPER)
            put(img, 11, 6, EMBER)
        else:
            put(img, 2, 2, EMBER_L)
            put(img, 9, 9, EMBER)
            put(img, 6, 6, EMBER_L)
        sheet.paste(img, (f * 12, 0))
    save(sheet, ENEMY / "ember_orb.png")


def make_custodio_sellado():
    ARM, ARM_D, ARM_L = (0x5C, 0x70, 0x84), STEEL_D, STEEL_L
    poses = [
        dict(lean=0, drop=0, eyes=COPPER_D, blade=((54, 31), (68, 44))),
        dict(lean=-2, drop=0, eyes=EMBER_L, blade=((59, 18), (59, 0))),
        dict(lean=3, drop=0, eyes=EMBER_L, blade=((54, 24), (90, 24)), trail=True),
        dict(lean=2, drop=3, eyes=COPPER_D, blade=((60, 31), (63, 47))),
    ]
    sheet = new(96 * 4, 48)
    for i, p in enumerate(poses):
        img = new(96, 48)
        d = ImageDraw.Draw(img)
        l, dr = p["lean"], p["drop"]
        if p.get("trail"):
            def tr(dd):
                for k in range(7):
                    a = 120 + k * 20
                    y = 5 + k * 3
                    dd.line([(56 + k * 4, y), (90, 24)], fill=rgba(IVORY, a))
                dd.polygon([(54, 20), (90, 22), (90, 27), (54, 28)], fill=rgba(IVORY, 130))
            overlay(img, tr)
        # grebas y escarpes
        for x0 in (40, 51):
            rect(d, x0, 36, x0 + 6, 47, ARM_D)
            rect(d, x0, 36, x0 + 1, 47, ARM)
            rect(d, x0, 44, x0 + 8, 47, ARM_D)
        # faldón de placas
        for k, x0 in enumerate(range(37, 59, 5)):
            rect(d, x0, 31 + dr, x0 + 4, 39, ARM if k % 2 else ARM_D)
            rect(d, x0, 31 + dr, x0 + 4, 31 + dr, ARM_L)
        # peto
        poly(d, [(38 + l, 17 + dr), (58 + l, 17 + dr), (56 + l, 32 + dr), (40 + l, 32 + dr)], ARM)
        line(d, (40 + l, 24 + dr), (56 + l, 24 + dr), ARM_D)
        line(d, (47 + l, 17 + dr), (47 + l, 32 + dr), ARM_D)
        rect(d, 38 + l, 17 + dr, 39 + l, 31 + dr, ARM_L)
        # sello marfil en el pecho
        disc(d, 51 + l, 25 + dr, 3, rgba(IVORY))
        rect(d, 51 + l, 23 + dr, 51 + l, 27 + dr, IVORY_D)
        rect(d, 49 + l, 25 + dr, 53 + l, 25 + dr, IVORY_D)
        # hombreras
        for sx in (37 + l, 58 + l):
            d.ellipse((sx - 5, 14 + dr, sx + 5, 23 + dr), fill=rgba(ARM_L))
            d.ellipse((sx - 4, 16 + dr, sx + 4, 23 + dr), fill=rgba(ARM))
        # yelmo con cresta
        d.rounded_rectangle((42 + l, 4 + dr, 55 + l, 17 + dr), radius=4, fill=rgba(ARM_L))
        rect(d, 42 + l, 9 + dr, 55 + l, 17 + dr, ARM)
        rect(d, 47 + l, 12 + dr, 55 + l, 13 + dr, BG)  # visera de rendija
        rect(d, 50 + l, 12 + dr, 54 + l, 12 + dr, p["eyes"])
        poly(d, [(44 + l, 5 + dr), (47 + l, 1 + dr), (53 + l, 1 + dr), (56 + l, 6 + dr), (52 + l, 5 + dr), (47 + l, 5 + dr)], IVORY_D)
        rect(d, 47 + l, 1 + dr, 53 + l, 1 + dr, IVORY)
        # espada: hoja ancha de acero con filo marfil y guarda de cobre
        (x0, y0), (x1, y1) = p["blade"]
        line(d, (x0, y0), (x1, y1), ARM_L, 4 if i != 2 else 4)
        line(d, (x0, y0 - 1), (x1, y1 - 1), IVORY, 1)
        rect(d, x0 - 3, y0 - 3, x0 + 2, y0 + 2, COPPER)
        rect(d, x0 - 1, y0 - 1, x0, y0, COPPER_D)
        if i == 1:
            for dx, dy in ((0, 1), (-2, 3), (2, 3)):
                put(img, x1 + dx, max(0, y1 + dy), IVORY)
        rim_light(img, STEEL)
        sheet.paste(img, (i * 96, 0))
    save(sheet, ENEMY / "custodio_sellado.png")


# ------------------------------------------------------------------ jefe: el Abad Sellado

SEAL_COLD = (0x4A, 0x56, 0x66)
CRACK = (0x5A, 0x22, 0x12)
SHAFT = (0x6A, 0x4A, 0x3A)


def seal(img, x, y, state):
    """Sello del pecho. Frío: oscuro y apagado. Caliente: disco de brasa con halo y grietas."""
    if state == "cold":
        d = ImageDraw.Draw(img)
        disc(d, x, y, 6, rgba(SEAL_COLD))
        disc(d, x, y, 4, rgba(STONE_D))
        rect(d, x, y - 3, x, y + 3, SEAL_COLD)
        rect(d, x - 3, y, x + 3, y, SEAL_COLD)
        return
    if state == "dead":
        d = ImageDraw.Draw(img)
        disc(d, x, y, 6, rgba(SEAL_COLD))
        disc(d, x, y, 4, rgba(BG))
        line(d, (x - 6, y - 4), (x + 6, y + 4), CRACK)
        put(img, x + 1, y, COPPER)
        return
    if state == "hot":
        halo(img, x, y, [17, 13], [45, 85], EMBER)
        d = ImageDraw.Draw(img)
        disc(d, x, y, 8, rgba(EMBER))
        d.ellipse((x - 8, y - 8, x + 8, y + 8), outline=rgba(IVORY))
        disc(d, x, y, 5, rgba(EMBER_L))
        disc(d, x, y, 2, rgba(IVORY))
        for dx, dy in ((9, -5), (-8, 6), (3, 9), (-5, -8), (9, 4)):  # grietas oscuras
            line(d, (x, y), (x + dx, y + dy), CRACK)
        return
    if state == "split":
        halo(img, x, y, [22, 17, 13], [35, 70, 110], EMBER)
        d = ImageDraw.Draw(img)
        for sgn in (-1, 1):
            d.pieslice((x + sgn * 4 - 8, y - 8, x + sgn * 4 + 8, y + 8), 90 if sgn > 0 else 270,
                       270 if sgn > 0 else 90, fill=rgba(EMBER))
        rect(d, x - 3, y - 11, x + 3, y + 11, EMBER_L)
        rect(d, x - 1, y - 11, x + 1, y + 11, IVORY)
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            line(d, (x + 12 * math.cos(a), y + 12 * math.sin(a)), (x + 22 * math.cos(a), y + 22 * math.sin(a)), EMBER, 1)


def hood(img, x, y, tilt=0, tip_h=20, eyes=COPPER_D, mouth=False):
    d = ImageDraw.Draw(img)
    poly(d, [(x + tilt, y - tip_h), (x + 9, y - 5), (x + 11, y + 8), (x - 11, y + 8), (x - 9, y - 5)], STONE_L)
    poly(d, [(x + tilt, y - tip_h), (x - 9, y - 5), (x - 11, y + 8), (x - 4, y + 8), (x - 4, y - 4)], STONE)
    line(d, (x + tilt, y - tip_h), (x + 9, y - 5), STEEL)
    line(d, (x + 9, y - 5), (x + 11, y + 8), STEEL)
    d.ellipse((x - 1, y - 8, x + 10, y + 6), fill=rgba(BG))
    for ex in (x + 2, x + 6):
        rect(d, ex, y - 3, ex + 1, y - 2, eyes)
    if mouth:
        rect(d, x + 2, y + 2, x + 8, y + 4, EMBER)
        rect(d, x + 4, y + 3, x + 6, y + 3, EMBER_L)
    # aro de acero del cuello
    rect(d, x - 11, y + 8, x + 11, y + 10, STEEL)
    rect(d, x - 11, y + 8, x + 11, y + 8, STEEL_L)


def pauldron(img, x, y):
    d = ImageDraw.Draw(img)
    d.ellipse((x - 8, y - 6, x + 8, y + 6), fill=rgba(STEEL))
    d.pieslice((x - 8, y - 6, x + 8, y + 6), 180, 360, fill=rgba(STEEL_L))
    rect(d, x - 5, y + 1, x + 5, y + 1, STEEL_D)
    put(img, x, y - 3, IVORY)


def sleeve(img, a, b, c, w=7):
    d = ImageDraw.Draw(img)
    line(d, a, b, STONE, w)
    line(d, b, c, STONE, w)
    line(d, b, c, STONE_L, 1)
    # brazal de acero y mano enguantada
    bx, by = lerp_pt(b, c, 0.6)
    line(d, (bx, by), c, STEEL_D, 5)
    disc(d, c[0], c[1], 3, rgba(STONE_D))


def lerp_pt(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def sickle(img, B, u, n, L, w=4, flip=False):
    """Hoja de guadaña: B=punta del astil, u=dirección del astil, n=hacia donde sale la hoja."""
    d = ImageDraw.Draw(img)
    P = lambda a, b: (B[0] + n[0] * L * a + u[0] * L * b, B[1] + n[1] * L * a + u[1] * L * b)
    outer = bezier(B, P(1.05, 0.4), P(0.85, -0.35))
    inner = bezier(P(0.85, -0.35), P(0.55, -0.02), (B[0] - u[0] * w, B[1] - u[1] * w))
    poly(d, outer + inner, STEEL_L)
    for a, b in zip(inner, inner[1:]):
        line(d, a, b, IVORY, 1)
    line(d, B, outer[3], STEEL_D, 2)


def scythe(img, butt, head, n, L=26):
    d = ImageDraw.Draw(img)
    ux, uy = head[0] - butt[0], head[1] - butt[1]
    m = math.hypot(ux, uy)
    u = (ux / m, uy / m)
    line(d, butt, head, SHAFT, 3)
    line(d, (butt[0] - 1, butt[1]), (head[0] - 1, head[1]), COPPER, 1)
    rect(d, head[0] - 3, head[1] - 1, head[0] + 3, head[1] + 3, STEEL_D)  # abrazadera
    sickle(img, head, u, n, L)


def abbot_body(img, robe, head, sh_l, sh_r, arms, seal_at, state, eyes=COPPER_D, tilt=0, tip_h=20, mouth=False,
               folds=None, belt=None):
    d = ImageDraw.Draw(img)
    poly(d, robe, STONE)
    if folds is None and len(robe) == 4:
        tl, tr, br, bl = robe
        folds = [(lerp_pt(tl, tr, t), lerp_pt(bl, br, t), c) for t, c in ((0.18, STONE_L), (0.4, STONE_D), (0.66, STONE_D), (0.88, STONE_D))]
        belt = (lerp_pt(tl, bl, 0.5), lerp_pt(tr, br, 0.5))
    for a, b, c in folds or []:
        line(d, a, b, c, 1)
    if belt:
        (ax, ay), (bx, by) = belt
        poly(d, [(ax, ay), (bx, by), (bx, by + 5), (ax, ay + 5)], STEEL_D)
        line(d, (ax, ay), (bx, by), STEEL, 1)
        rect(d, (ax + bx) // 2 - 2, (ay + by) // 2, (ax + bx) // 2 + 2, (ay + by) // 2 + 4, IVORY_D)
    # ribete del bajo
    ys = max(p[1] for p in robe)
    xs = [p[0] for p in robe if p[1] == ys]
    if xs:
        rect(d, min(xs), ys - 3, max(xs), ys - 2, STEEL_D)
        rect(d, min(xs), ys - 3, max(xs), ys - 3, STEEL)
    pauldron(img, *sh_l)
    pauldron(img, *sh_r)
    seal(img, seal_at[0], seal_at[1], state)
    hood(img, head[0], head[1], tilt, tip_h, eyes, mouth)
    for a, b, c in arms:
        sleeve(img, a, b, c)


def finish(img):
    rim_light(img, STEEL)
    return img


def abbot_frames():
    W, H = 224, 128
    frames = []

    # 0 reposo
    img = new(W, H)
    scythe(img, (142, 122), (142, 16), (1, 0), 28)
    abbot_body(img, [(100, 44), (124, 44), (137, 120), (87, 120)], (112, 30), (99, 48), (125, 48),
               [((99, 50), (94, 62), (92, 74)), ((125, 50), (134, 60), (141, 72))], (112, 66), "cold")
    d = ImageDraw.Draw(img)
    line(d, (92, 76), (90, 90), STEEL, 1)
    censer(img, 90, 98, 7, 0)
    frames.append(finish(img))

    # 1 anticipación del tajo: cuerpo cargado hacia atrás, guadaña atrás y en alto
    img = new(W, H)
    scythe(img, (134, 92), (72, 18), (0.77, -0.64), 24)
    abbot_body(img, [(92, 46), (116, 46), (137, 120), (87, 120)], (104, 32), (91, 50), (117, 50),
               [((91, 52), (92, 64), (105, 58)), ((117, 52), (126, 64), (117, 72))], (105, 66), "cold", tilt=-3)
    d = ImageDraw.Draw(img)
    line(d, (96, 80), (88, 88), STEEL, 1)
    censer(img, 86, 94, 6, 0)
    frames.append(finish(img))

    # 2 tajo bajo: la hoja barre de x 112 a x 208 entre las filas 96 y 120
    img = new(W, H)

    def trail(dd):
        top = bezier((112, 100), (160, 96), (208, 101))
        bot = bezier((208, 112), (160, 121), (112, 119))
        dd.polygon(top + bot, fill=rgba(IVORY, 55))
        top2 = bezier((124, 103), (164, 100), (206, 105))
        bot2 = bezier((206, 109), (164, 117), (124, 116))
        dd.polygon(top2 + bot2, fill=rgba(IVORY, 80))
        for (x0, x1, y, a) in ((118, 206, 101, 220), (132, 200, 105, 180), (126, 196, 112, 200), (140, 188, 116, 150)):
            dd.line([(x0, y), (x1, y)], fill=rgba(IVORY, a))
    abbot_body(img, [(114, 62), (138, 62), (144, 120), (92, 120)], (130, 46), (117, 66), (139, 66),
               [((139, 68), (147, 88), (144, 107)), ((117, 68), (125, 90), (122, 105))], (129, 84), "cold", tilt=3)
    d = ImageDraw.Draw(img)
    line(d, (98, 112), (170, 108), SHAFT, 3)
    line(d, (98, 111), (170, 107), COPPER, 1)
    overlay(img, trail)
    d = ImageDraw.Draw(img)
    outer = bezier((158, 107), (192, 93), (208, 103))
    inner = bezier((208, 103), (188, 114), (158, 115))
    poly(d, outer + inner, STEEL_L)
    for a, b in zip(outer, outer[1:]):
        line(d, a, b, IVORY, 1)
    line(d, (156, 107), (160, 115), STEEL_D, 3)
    sleeve(img, (139, 68), (147, 88), (144, 107))
    sleeve(img, (117, 68), (125, 90), (122, 105))
    line(d, (104, 84), (96, 96), STEEL, 1)
    censer(img, 94, 101, 6, 0)
    frames.append(finish(img))

    # 3 recuperación (vulnerable): rodilla en tierra, guadaña clavada, sello brillante y agrietado
    img = new(W, H)
    scythe(img, (152, 121), (142, 30), (0.99, -0.11), 28)
    abbot_body(img, [(98, 66), (124, 66), (132, 92), (140, 120), (84, 120), (90, 92)], (110, 54), (98, 70), (125, 70),
               [((125, 72), (138, 78), (146, 72)), ((98, 72), (104, 90), (121, 94))], (111, 84), "hot",
               eyes=COPPER_D, tilt=2, folds=[((104, 96), (100, 118), STONE_D), ((118, 96), (122, 118), STONE_D)],
               belt=((100, 96), (124, 96)))
    d = ImageDraw.Draw(img)
    poly(d, [(126, 112), (142, 112), (144, 120), (124, 120)], STEEL_D)  # bota delantera
    d.ellipse((84, 104, 98, 119), fill=rgba(STEEL_D))  # rodilla en tierra
    frames.append(finish(img))

    # 4 anticipación de la lluvia: incensario alzado a dos manos sobre la cabeza
    img = new(W, H)
    scythe(img, (152, 122), (150, 30), (1, 0), 26)
    abbot_body(img, [(98, 60), (126, 60), (139, 120), (85, 120)], (112, 46), (99, 64), (125, 64),
               [((99, 66), (96, 46), (104, 28)), ((125, 66), (128, 46), (120, 28))], (112, 82), "cold", eyes=EMBER_L)
    d = ImageDraw.Draw(img)
    line(d, (104, 28), (108, 20), STEEL, 1)
    line(d, (120, 28), (116, 20), STEEL, 1)
    censer(img, 112, 11, 9, 2)
    for x, y in ((100, 40), (124, 40), (112, 34)):
        put(img, x, y, EMBER)
    frames.append(finish(img))

    # 5 lanzamiento de la lluvia: incensario balanceado, brasas hacia arriba
    img = new(W, H)
    scythe(img, (80, 122), (86, 34), (-1, 0), 22)
    abbot_body(img, [(106, 56), (132, 56), (142, 120), (88, 120)], (122, 42), (108, 60), (132, 60),
               [((132, 60), (142, 46), (150, 36)), ((108, 60), (98, 76), (92, 92))], (121, 76), "cold", eyes=EMBER, tilt=3)
    d = ImageDraw.Draw(img)
    pts = [(150, 36), (158, 26), (166, 19), (172, 16)]
    for a, b in zip(pts, pts[1:]):
        line(d, a, b, STEEL, 1)
    rnd = random.Random(5)
    for k in range(26):  # brasas que salen hacia arriba
        x = 160 + rnd.randint(0, 40)
        y = rnd.randint(0, 12)
        put(img, x, y, EMBER_L if k % 3 == 0 else EMBER)
        if k % 2 == 0:
            put(img, x, y + 1, COPPER)
    for x in (166, 174, 182, 190):
        line(d, (x, 3), (x, 9), EMBER, 1)
    censer(img, 177, 20, 8, 2)
    frames.append(finish(img))

    # 6 agotado (vulnerable): de rodillas, encorvado, manos en el suelo, sello brillando
    img = new(W, H)
    d = ImageDraw.Draw(img)
    scythe(img, (100, 119), (44, 119), (0, -1), 16)
    abbot_body(img, [(90, 112), (94, 90), (108, 76), (128, 76), (142, 92), (140, 120), (86, 120)], (138, 92), (104, 82), (128, 80),
               [((128, 84), (142, 102), (150, 116)), ((106, 88), (118, 106), (128, 117))], (114, 94), "hot",
               tilt=9, tip_h=11, folds=[((100, 92), (96, 118), STONE_D), ((112, 82), (112, 118), STONE_D)], belt=None)
    d = ImageDraw.Draw(img)
    censer(img, 158, 113, 6, 1)
    for x, y in ((152, 106), (164, 104), (168, 110)):
        put(img, x, y, EMBER)
    frames.append(finish(img))

    # 7 rugido del cambio de fase: brazos abiertos, sello partido emitiendo brasa
    img = new(W, H)
    scythe(img, (156, 84), (170, 8), (1, 0), 20)
    abbot_body(img, [(98, 46), (126, 46), (140, 120), (84, 120)], (112, 28), (98, 50), (126, 50),
               [((98, 52), (80, 46), (62, 38)), ((126, 52), (144, 46), (162, 38))], (112, 62), "split", eyes=EMBER_L, mouth=True)
    d = ImageDraw.Draw(img)
    line(d, (62, 38), (58, 60), STEEL, 1)
    censer(img, 58, 67, 7, 2)
    for x, y in ((50, 30), (176, 28), (126, 8), (98, 10), (150, 14), (74, 20)):
        put(img, x, y, EMBER_L)
        put(img, x, y + 1, EMBER)
    frames.append(finish(img))

    # 8 derrotado: desplomado
    img = new(W, H)
    d = ImageDraw.Draw(img)
    line(d, (46, 120), (96, 113), SHAFT, 3)  # guadaña partida
    line(d, (120, 119), (170, 121), SHAFT, 3)
    sickle(img, (178, 119), (1, 0), (0, -1), 14)
    abbot_body(img, [(70, 120), (76, 104), (92, 92), (114, 86), (134, 92), (148, 104), (154, 120)], (146, 106), (96, 98), (128, 94),
               [((130, 98), (146, 112), (162, 117))], (108, 104), "dead", tilt=7, tip_h=9,
               folds=[((90, 100), (84, 118), STONE_D), ((108, 92), (104, 118), STONE_D), ((124, 94), (126, 118), STONE_D)], belt=None)
    censer(img, 176, 114, 6, 0)
    frames.append(finish(img))
    return frames


def make_boss():
    frames = abbot_frames()
    sheet = new(224 * 9, 128)
    for i, f in enumerate(frames):
        sheet.paste(f, (i * 224, 0))
    save(sheet, BOSS / "abad.png")

    # Brasa que cae 2x16x32: punta hacia abajo, estela arriba
    sheet = new(32, 32)
    for f in range(2):
        img = new(16, 32)

        def tr(dd, f=f):
            for y in range(0, 20):
                half = int(1 + y * 0.12) + (1 if f else 0)
                a = int(30 + 150 * (y / 20.0))
                dd.line([(8 - half, y), (8 + half, y)], fill=rgba(COPPER, a))
            for y in range(6, 20, 4):
                dd.point([(8 + (3 if (y // 4 + f) % 2 else -3), y)], fill=rgba(EMBER, 200))
        overlay(img, tr)
        d = ImageDraw.Draw(img)
        poly(d, [(8, 31), (3, 22), (5, 17), (11, 17), (13, 22)], EMBER)
        poly(d, [(8, 29), (5, 22), (6, 19), (10, 19), (11, 22)], EMBER_L)
        rect(d, 7, 21, 8, 24, IVORY)
        sheet.paste(img, (f * 16, 0))
    save(sheet, BOSS / "falling_ember.png")

    # Marca del suelo 32x8
    img = new(32, 8)

    def mk(dd):
        dd.ellipse((0, 0, 31, 7), fill=rgba(EMBER, 60))
        dd.ellipse((0, 0, 31, 7), outline=rgba(EMBER, 255))
        dd.ellipse((6, 2, 25, 5), fill=rgba(EMBER_L, 120))
        dd.ellipse((12, 3, 19, 4), fill=rgba(IVORY, 220))
    overlay(img, mk)
    save(img, BOSS / "ember_marker.png")


# ------------------------------------------------------------------ Baldwin (jugador)

def ik(a, b, l1, l2, bend):
    dx, dy = b[0] - a[0], b[1] - a[1]
    dist = max(abs(l1 - l2) + 0.01, min(math.hypot(dx, dy), l1 + l2 - 0.01))
    base = math.atan2(dy, dx)
    cos_a = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    ang = base + bend * math.acos(max(-1.0, min(1.0, cos_a)))
    return (a[0] + l1 * math.cos(ang), a[1] + l1 * math.sin(ang))


def sword(img, H, ang, L=30, s=1.0):
    """Espada de Baldwin: hoja de acero, filo marfil, guarda de cobre. ang en grados (antihorario, 0 = derecha)."""
    d = ImageDraw.Draw(img)
    a = math.radians(ang)
    dx, dy = math.cos(a), -math.sin(a)
    px, py = -dy, dx
    P = lambda t, o=0.0: (H[0] + dx * t + px * o, H[1] + dy * t + py * o)
    hw = 1.7 * s
    line(d, P(-4 * s), P(2 * s), COPPER_D, max(2, int(round(2 * s))))
    disc(d, *P(-5 * s), max(1.5, 1.6 * s), rgba(COPPER))
    ho = hw + 1.2
    poly(d, [P(3 * s, -ho), P(3 * s + L * 0.92, -ho * 0.8), P(3 * s + L + 1.5, 0), P(3 * s + L * 0.92, ho * 0.8), P(3 * s, ho)], STEEL_D)
    poly(d, [P(3 * s, -hw), P(3 * s + L * 0.92, -hw * 0.8), P(3 * s + L, 0), P(3 * s + L * 0.92, hw * 0.8), P(3 * s, hw)], STEEL_L)
    line(d, P(3 * s, -hw), P(3 * s + L, 0), IVORY, 1)
    line(d, P(5 * s, 0.4), P(3 * s + L * 0.75, 0.3), STEEL, 1)
    line(d, P(2 * s, -4 * s), P(2 * s, 4 * s), COPPER, 2)
    put(img, int(P(2 * s, -4 * s)[0]), int(P(2 * s, -4 * s)[1]), EMBER)


def draw_baldwin(p):
    """Dibuja a Baldwin (128x128, mira a la derecha) a partir de un esqueleto p."""
    img = new(128, 128)
    d = ImageDraw.Draw(img)
    hip, sh, hd = p["hip"], p["sh"], p["head"]
    cdx, cdy = p.get("cape", (0, 0))
    sx, sy = sh
    hx, hy = hip
    # capa corta de piedra oscura (detrás)
    hem_l = (sx - 14 + cdx, sy + 22 + cdy)
    hem_r = (sx - 5 + cdx * 0.6, sy + 24 + cdy)
    poly(d, [(sx - 5, sy - 3), (sx + 2, sy + 1), hem_r, hem_l], STONE_D)
    line(d, (sx - 5, sy - 3), hem_l, STONE_L, 1)
    line(d, (sx - 2, sy), (hem_l[0] + 4, hem_l[1]), STONE, 1)
    # brazo trasero
    kb = ik((sx - 3, sy + 2), p["bhand"], 9, 9, 1)
    line(d, (sx - 3, sy + 2), kb, STEEL_D, 5)
    line(d, kb, p["bhand"], STEEL_D, 5)
    disc(d, p["bhand"][0], p["bhand"][1], 3, rgba(STEEL))

    def leg(foot, back):
        hp = (hx + (-2 if back else 2), hy)
        kn = ik(hp, foot, 14, 14, -1)
        base, hi = (STEEL_D, STEEL) if back else (STEEL, STEEL_L)
        line(d, hp, kn, base, 6)
        line(d, kn, foot, base, 5)
        line(d, (hp[0] + 1, hp[1]), (kn[0] + 1, kn[1]), hi, 1)
        disc(d, kn[0], kn[1], 3, rgba(COPPER if not back else COPPER_DD))
        fx, fy = int(round(foot[0])), int(round(foot[1]))
        poly(d, [(fx - 3, fy - 5), (fx + 2, fy - 5), (fx + 6, fy - 2), (fx + 6, fy), (fx - 3, fy)], STEEL_D if back else STEEL)
        rect(d, fx - 3, fy, fx + 6, fy, STONE_D)
    leg(p["bfoot"], True)
    # torso y sobreveste marfil con ribetes de cobre
    poly(d, [(sx - 7, sy - 1), (sx + 7, sy - 1), (hx + 6, hy), (hx - 6, hy)], STEEL)
    poly(d, [(sx - 6, sy + 1), (sx + 7, sy + 1), (hx + 8, hy + 14), (hx - 6, hy + 14)], IVORY)
    line(d, (sx - 6, sy + 1), (hx - 6, hy + 14), IVORY_D, 1)
    line(d, ((sx + hx) // 2 + 1, sy + 4), (hx + 1, hy + 14), IVORY_D, 1)
    line(d, (hx - 6, hy + 14), (hx + 8, hy + 14), COPPER, 2)
    line(d, (hx - 6, hy + 1), (hx + 7, hy + 1), COPPER, 2)  # cinto
    rect(d, hx, hy, hx + 2, hy + 3, IVORY_D)
    line(d, (sx - 6, sy + 1), (sx + 7, sy + 1), COPPER, 1)
    # maldición: grieta de brasa sobre un fondo oscuro para que se lea en grises
    cr = [(sx + 2, sy + 2), (sx, sy + 6), (sx + 4, sy + 9), (sx + 1, sy + 13)]
    for a, b in zip(cr, cr[1:]):
        line(d, (a[0] - 1, a[1]), (b[0] - 1, b[1]), COPPER_DD, 3)
    for a, b in zip(cr, cr[1:]):
        line(d, a, b, EMBER, 1)
    put(img, cr[1][0], cr[1][1], EMBER_L)
    put(img, cr[2][0], cr[2][1], EMBER_L)
    leg(p["ffoot"], False)
    # hombreras
    for ox, oy, r in ((-7, 1, 4), (6, 1, 5)):
        disc(d, sx + ox, sy + oy, r, rgba(STEEL_L))
        d.pieslice((sx + ox - r, sy + oy - r, sx + ox + r, sy + oy + r), 0, 180, fill=rgba(STEEL))
        d.arc((sx + ox - r, sy + oy - r, sx + ox + r, sy + oy + r), 180, 360, fill=rgba(COPPER))
    # yelmo de visera de rendija y penacho marfil corto
    d.ellipse((hd[0] - 6, hd[1] - 8, hd[0] + 6, hd[1] + 6), fill=rgba(STEEL_L))
    rect(d, hd[0] - 6, hd[1] - 1, hd[0] + 6, hd[1] + 6, STEEL)
    rect(d, hd[0] - 6, hd[1] + 5, hd[0] + 6, hd[1] + 6, STEEL_D)
    rect(d, hd[0] + 0, hd[1] - 1, hd[0] + 6, hd[1], BG)  # rendija
    rect(d, hd[0] - 6, hd[1] - 2, hd[0] + 6, hd[1] - 2, STEEL_L)
    rect(d, hd[0] - 1, hd[1] - 8, hd[0] - 1, hd[1] + 5, STEEL_D)  # cresta del yelmo
    crest = [(hd[0] - 6, hd[1] - 5), (hd[0] - 3, hd[1] - 10), (hd[0] + 1, hd[1] - 11), (hd[0] + 4, hd[1] - 8), (hd[0], hd[1] - 6)]
    poly(d, crest, IVORY)
    line(d, (hd[0] - 7, hd[1] - 4), (hd[0] - 4, hd[1] - 8), IVORY_D, 1)
    # brazo delantero con la espada
    fs = (sx + 5, sy + 3)
    ke = ik(fs, p["fhand"], 9, 9, 1)
    line(d, fs, ke, STEEL, 5)
    line(d, ke, p["fhand"], STEEL, 5)
    line(d, fs, ke, STEEL_L, 1)
    disc(d, p["fhand"][0], p["fhand"][1], 3, rgba(STEEL_L))
    if p.get("trail"):
        p["trail"](img)
    sword(img, p["fhand"], p["ang"], 30)
    disc(ImageDraw.Draw(img), p["fhand"][0], p["fhand"][1], 2, rgba(STEEL_L))
    return img


BASE = dict(hip=(30, 102), sh=(33, 82), head=(35, 75), ffoot=(38, 127), bfoot=(24, 127),
            fhand=(42, 96), bhand=(27, 98), ang=38, cape=(0, 0))


def pose(**kw):
    q = dict(BASE)
    q.update(kw)
    return q


def attack_trail(img):
    def f(d):
        outer = bezier((38, 78), (122, 74), (70, 116))
        inner = bezier((70, 116), (86, 98), (38, 78))
        d.polygon(outer + inner, fill=rgba(IVORY, 105))
        o2 = bezier((46, 82), (112, 80), (68, 112))
        i2 = bezier((68, 112), (84, 98), (46, 82))
        d.polygon(o2 + i2, fill=rgba(IVORY, 175))
        for a, b in zip(outer, outer[1:]):
            d.line([a, b], fill=rgba(IVORY, 235), width=1)
    overlay(img, f)


def baldwin_sheets():
    out = {}
    # Idle: respiración sutil de 1 px
    fr = []
    for i, dy in enumerate((0, -1, -1, 0)):
        fr.append(draw_baldwin(pose(sh=(33, 82 + dy), head=(35, 75 + dy), fhand=(42, 96 + dy), bhand=(27, 98 + dy), cape=(-dy, 0))))
    out["Idle"] = fr
    # Walk: 8 pasos
    fr = []
    for i in range(8):
        ph = i / 8.0
        feet = []
        for off in (0.0, 0.5):
            u = (ph + off) % 1.0
            if u < 0.5:
                feet.append((32 + 9 - 18 * (u / 0.5), 127))
            else:
                v = (u - 0.5) / 0.5
                feet.append((32 - 9 + 18 * v, 127 - 6 * math.sin(math.pi * v)))
        hy = 100 + 2 * abs(math.cos(2 * math.pi * ph))
        sw = math.sin(2 * math.pi * ph)
        fr.append(draw_baldwin(pose(hip=(30, hy), sh=(34, hy - 20), head=(36, hy - 27), ffoot=feet[0], bfoot=feet[1],
                                    fhand=(42 + 2 * sw, hy - 6 + 1.5 * abs(sw)), bhand=(27 - 4 * sw, hy - 4),
                                    ang=36 + 4 * sw, cape=(-2 - 2 * abs(sw), 0))))
    out["Walk"] = fr
    # Jump: impulso, subida, cumbre, caída
    jp = [
        pose(hip=(30, 108), sh=(35, 90), head=(38, 83), ffoot=(40, 127), bfoot=(22, 127), fhand=(38, 103), bhand=(25, 101), ang=15, cape=(-3, 2)),
        pose(hip=(31, 104), sh=(33, 84), head=(35, 77), ffoot=(36, 127), bfoot=(28, 127), fhand=(46, 84), bhand=(22, 90), ang=62, cape=(-2, 5)),
        pose(hip=(30, 101), sh=(33, 81), head=(35, 74), ffoot=(39, 118), bfoot=(25, 127), fhand=(45, 86), bhand=(22, 86), ang=55, cape=(-3, 2)),
        pose(hip=(30, 101), sh=(33, 81), head=(35, 74), ffoot=(37, 121), bfoot=(26, 127), fhand=(45, 80), bhand=(21, 84), ang=80, cape=(-3, -2)),
        pose(hip=(30, 102), sh=(33, 82), head=(35, 75), ffoot=(39, 127), bfoot=(25, 127), fhand=(45, 76), bhand=(21, 80), ang=105, cape=(-2, -9)),
        pose(hip=(30, 103), sh=(33, 83), head=(35, 76), ffoot=(40, 127), bfoot=(24, 127), fhand=(46, 90), bhand=(20, 88), ang=35, cape=(-3, -11)),
    ]
    out["Jump"] = [draw_baldwin(q) for q in jp]
    # Attack: 0-3 anticipación (la espada se echa atrás y arriba), 4 tajo
    ap = [
        pose(hip=(30, 102), sh=(32, 82), head=(34, 75), ffoot=(37, 127), bfoot=(23, 127), fhand=(41, 94), bhand=(26, 96), ang=30),
        pose(hip=(29, 103), sh=(30, 83), head=(32, 76), ffoot=(36, 127), bfoot=(22, 127), fhand=(38, 86), bhand=(25, 92), ang=75, cape=(-2, 0)),
        pose(hip=(28, 104), sh=(28, 84), head=(30, 77), ffoot=(35, 127), bfoot=(20, 127), fhand=(34, 76), bhand=(23, 90), ang=112, cape=(-3, 0)),
        pose(hip=(27, 105), sh=(25, 85), head=(27, 78), ffoot=(35, 127), bfoot=(17, 127), fhand=(29, 72), bhand=(20, 90), ang=140, cape=(-4, 0)),
        pose(hip=(33, 104), sh=(40, 86), head=(44, 79), ffoot=(46, 127), bfoot=(19, 127), fhand=(57, 93), bhand=(32, 98), ang=-2,
             cape=(-8, -2), trail=attack_trail),
    ]
    out["Attack"] = [draw_baldwin(q) for q in ap]
    # Hurt: retroceso en 2 cuadros
    hp = [
        pose(hip=(29, 103), sh=(26, 83), head=(24, 76), ffoot=(36, 127), bfoot=(22, 127), fhand=(37, 88), bhand=(19, 92), ang=85, cape=(-5, -2)),
        pose(hip=(27, 105), sh=(22, 86), head=(19, 80), ffoot=(34, 127), bfoot=(17, 127), fhand=(31, 94), bhand=(15, 96), ang=105, cape=(-7, -3)),
    ]
    out["Hurt"] = [draw_baldwin(q) for q in hp]
    # Dead: tambaleo, rodillas, caída hacia atrás y tumbado sobre la fila 127
    dp = [
        pose(hip=(28, 103), sh=(24, 84), head=(22, 77), ffoot=(36, 127), bfoot=(18, 127), fhand=(34, 92), bhand=(17, 94), ang=70, cape=(-6, -2)),
        pose(hip=(28, 113), sh=(25, 93), head=(24, 86), ffoot=(38, 127), bfoot=(14, 127), fhand=(35, 106), bhand=(18, 104), ang=-20, cape=(-5, 0)),
    ]
    kneel = draw_baldwin(pose(hip=(24, 114), sh=(19, 96), head=(16, 89), ffoot=(36, 127), bfoot=(8, 127), fhand=(30, 110), bhand=(10, 108), ang=-55, cape=(-3, 0)))
    frames = [draw_baldwin(q) for q in dp] + [kneel]
    for ang, left in ((32, None), (62, 10), (90, 12)):
        big = new(300, 300)
        big.paste(kneel, (80, 80))
        big = big.rotate(ang, resample=Image.NEAREST, center=(80 + 24, 80 + 127))
        bbox = big.getbbox()
        crop = big.crop(bbox)
        cell = new(128, 128)
        x = 6 if left is None else left
        if left is None:
            x = max(2, 80 + 8 - bbox[0] + 8)
        cell.paste(crop, (x, 128 - crop.height))
        frames.append(cell)
    out["Dead"] = frames
    return out


def make_baldwin():
    sheets = baldwin_sheets()
    counts = dict(Idle=4, Walk=8, Jump=6, Attack=5, Dead=6, Hurt=2)
    for name, fr in sheets.items():
        assert len(fr) == counts[name], name
        sheet = new(128 * len(fr), 128)
        for i, f in enumerate(fr):
            rim_light(f, STEEL)
            sheet.paste(f, (i * 128, 0))
        save(sheet, BALDWIN / f"{name}.png")


def baldwin_back(img, x, f, ember_rim=True):
    """Baldwin de espaldas (el mismo diseño: yelmo con penacho marfil, hombreras, capa corta,
    sobreveste marfil, espada al cinto y la grieta de brasa en el brazo). ~46 px de alto."""
    layer = new(img.width, img.height)
    d = ImageDraw.Draw(layer)
    for ox in (-5, 1):  # botas y grebas
        rect(d, x + ox, f - 14, x + ox + 4, f, STEEL)
        rect(d, x + ox, f - 4, x + ox + 5, f, STEEL_D)
    rect(d, x - 7, f - 18, x + 7, f - 13, IVORY)  # sobreveste bajo la capa
    rect(d, x - 7, f - 14, x + 7, f - 13, COPPER)
    poly(d, [(x - 8, f - 31), (x + 8, f - 31), (x + 10, f - 17), (x + 5, f - 15), (x, f - 17), (x - 5, f - 15), (x - 10, f - 17)], STONE_D)
    line(d, (x - 8, f - 31), (x - 10, f - 17), STONE_L, 1)
    line(d, (x - 3, f - 28), (x - 3, f - 17), STONE, 1)
    line(d, (x + 3, f - 28), (x + 4, f - 17), STONE, 1)
    rect(d, x - 7, f - 22, x + 7, f - 21, COPPER_DD)  # cinto bajo la capa
    # espada al cinto: empuñadura que asoma a la derecha
    line(d, (x + 8, f - 20), (x + 14, f - 26), COPPER, 2)
    line(d, (x + 11, f - 29), (x + 17, f - 23), COPPER, 2)
    disc(d, x + 15, f - 28, 1, rgba(COPPER))
    line(d, (x + 8, f - 20), (x + 12, f - 5), STEEL_D, 2)
    for ox in (-9, 9):  # hombreras
        d.ellipse((x + ox - 4, f - 36, x + ox + 4, f - 29), fill=rgba(STEEL_L))
        rect(d, x + ox - 3, f - 32, x + ox + 3, f - 31, COPPER)
    rect(d, x - 5, f - 36, x + 5, f - 32, STEEL_D)  # cuello
    d.ellipse((x - 6, f - 46, x + 6, f - 33), fill=rgba(STEEL_L))
    rect(d, x - 6, f - 39, x + 6, f - 34, STEEL)
    rect(d, x, f - 46, x, f - 35, STEEL_D)
    poly(d, [(x - 2, f - 45), (x - 1, f - 50), (x + 2, f - 50), (x + 3, f - 45)], IVORY)  # penacho
    # grieta de la maldición en el brazo derecho
    for a, b in (((x + 10, f - 29), (x + 11, f - 25)), ((x + 11, f - 25), (x + 9, f - 22))):
        line(d, a, b, COPPER_DD, 3)
        line(d, a, b, EMBER, 1)
    put(layer, x + 11, f - 25, EMBER_L)
    rim_light(layer, EMBER if ember_rim else STEEL, 190)
    img.alpha_composite(layer)


def make_weapon_icons():
    # Baldwin_Sword 64x64: espada en diagonal, hoja de acero, filo marfil, guarda de cobre
    img = new(64, 64)
    d = ImageDraw.Draw(img)
    a = math.radians(45)
    dx, dy = math.cos(a), -math.sin(a)
    px, py = -dy, dx
    H = (16, 49)
    P = lambda t, o=0.0: (H[0] + dx * t + px * o, H[1] + dy * t + py * o)
    line(d, P(-9), P(5), COPPER_D, 5)
    for t in (-6, -2, 2):
        line(d, P(t, -2), P(t, 2), COPPER_DD, 1)
    disc(d, *P(-11), 4, rgba(COPPER))
    disc(d, *P(-11), 2, rgba(COPPER_D))
    poly(d, [P(6, -3), P(6 + 38, -2.6), P(6 + 46, 0), P(6 + 38, 2.6), P(6, 3)], STEEL_L)
    poly(d, [P(6, 0), P(6 + 44, 0), P(6 + 38, 2.6), P(6, 3)], STEEL)
    line(d, P(6, -3), P(6 + 46, 0), IVORY, 1)
    line(d, P(9, 0), P(6 + 34, 0), STEEL_D, 1)
    line(d, P(5, -9), P(5, 9), COPPER, 4)
    line(d, P(5, -8), P(5, -4), COPPER_D, 2)
    put(img, int(P(5, 0)[0]), int(P(5, 0)[1]), EMBER)
    put(img, int(P(5, 0)[0]) + 1, int(P(5, 0)[1]), EMBER_L)
    rim_light(img, STEEL, 120)
    save(img, WEAPONS / "Baldwin_Sword.png")

    # Crypt_Mace 64x64: mango recto y cabeza de hierro con aletas y remaches de cobre
    img = new(64, 64)
    d = ImageDraw.Draw(img)
    line(d, (27, 61), (34, 30), COPPER_D, 5)
    line(d, (26, 60), (33, 30), COPPER, 1)
    for t in range(0, 6):  # vendaje del mango
        y = 56 - t * 5
        x = 27 + (61 - y) * 7 / 31.0
        line(d, (x - 2, y), (x + 2, y - 2), COPPER_DD, 1)
    disc(d, 27, 61, 3, rgba(STEEL_D))
    cx, cy = 36, 19
    for ang in (-90, -30, 30, 90, 150, 210):  # aletas / púas
        a = math.radians(ang)
        tip = (cx + 17 * math.cos(a), cy + 17 * math.sin(a))
        l = (cx + 9 * math.cos(a - 0.45), cy + 9 * math.sin(a - 0.45))
        r = (cx + 9 * math.cos(a + 0.45), cy + 9 * math.sin(a + 0.45))
        poly(d, [l, tip, r], STEEL_D)
    disc(d, cx, cy, 12, rgba(STEEL_D))
    d.pieslice((cx - 12, cy - 12, cx + 12, cy + 12), 150, 300, fill=rgba(STEEL_L))
    d.pieslice((cx - 9, cy - 9, cx + 9, cy + 9), 160, 290, fill=rgba(STEEL))
    d.arc((cx - 12, cy - 12, cx + 12, cy + 12), 0, 360, fill=rgba(BG))
    rect(d, cx - 12, cy - 2, cx + 12, cy + 1, COPPER_D)  # banda de cobre
    rect(d, cx - 12, cy - 2, cx + 12, cy - 2, COPPER)
    for ox in (-9, -4, 1, 6, 10):
        disc(d, cx + ox, cy, 1, rgba(EMBER_L if ox == 1 else COPPER))
    rect(d, cx - 4, cy + 12, cx + 4, cy + 15, COPPER_D)  # base de la cabeza
    rim_light(img, STEEL, 150)
    save(img, WEAPONS / "Crypt_Mace.png")


# ------------------------------------------------------------------ historia

def stars(img, n, seed, ymax):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.randint(0, 639), rnd.randint(0, ymax)
        c = rnd.choice([(0x5A, 0x66, 0x7A), (0x7A, 0x86, 0x96), IVORY_D])
        put(img, x, y, c)
        if rnd.random() < 0.12:
            put(img, x + 1, y, (0x4A, 0x56, 0x6A))
            put(img, x, y + 1, (0x4A, 0x56, 0x6A))


def draw_abbey(img, g, pal, open_doors=False, broken=False):
    W, WL, WD, WIN, DOOR = pal["wall"], pal["wall_l"], pal["wall_d"], pal["window"], pal["door"]
    d = ImageDraw.Draw(img)
    for sgn in (-1, 1):  # naves laterales con contrafuertes y ventanas apuntadas
        xa, xb = (70, 200) if sgn < 0 else (440, 570)
        rect(d, xa, g - 100, xb, g, W)
        rect(d, xa - 4, g - 104, xb + 4, g - 100, WL)
        for bx in range(xa, xb, 30):
            rect(d, bx, g - 100, bx + 7, g, WD)
            rect(d, bx, g - 100, bx, g, WL)
        for wx in range(xa + 16, xb - 6, 30):
            pointed_arch(img, wx + 5, g - 56, 5, 5, WL, fill_inside=WIN)
            rect(d, wx, g - 56, wx + 9, g - 34, WIN)
            rect(d, wx, g - 56, wx, g - 34, WL)
    for cx in (220, 420):  # torres con aguja
        rect(d, cx - 22, g - 172, cx + 22, g, W)
        rect(d, cx - 22, g - 172, cx - 20, g, WL)
        rect(d, cx + 19, g - 172, cx + 22, g, WD)
        rect(d, cx - 24, g - 176, cx + 24, g - 172, WL)
        poly(d, [(cx - 25, g - 176), (cx + 25, g - 176), (cx, g - 218)], WD)
        poly(d, [(cx - 25, g - 176), (cx, g - 218), (cx - 4, g - 176)], W)
        line(d, (cx - 25, g - 176), (cx, g - 218), WL, 1)
        rect(d, cx, g - 224, cx, g - 218, WL)
        pointed_arch(img, cx, g - 130, 7, 4, WD, fill_inside=DOOR)  # campanario
        rect(d, cx - 7, g - 130, cx + 6, g - 112, DOOR)
        pointed_arch(img, cx, g - 70, 5, 4, WL, fill_inside=WIN)
        rect(d, cx - 5, g - 70, cx + 4, g - 52, WIN)
    # fachada central con piñón
    rect(d, 242, g - 146, 398, g, W)
    poly(d, [(238, g - 146), (402, g - 146), (320, g - 192)], W)
    line(d, (238, g - 146), (320, g - 192), WL, 1)
    line(d, (402, g - 146), (320, g - 192), WL, 1)
    rect(d, 236, g - 148, 404, g - 146, WL)
    rect(d, 242, g - 146, 246, g, WL)
    rect(d, 394, g - 146, 398, g, WD)
    rect(d, 242, g - 96, 398, g - 94, WL)
    rect(d, 319, g - 202, 320, g - 192, WL)
    rect(d, 316, g - 199, 323, g - 198, WL)
    # rosetón: el sello de la abadía
    rc = (320, g - 164)
    if not broken:
        disc(d, rc[0], rc[1], 14, rgba(WL))
        disc(d, rc[0], rc[1], 11, rgba(WIN))
        for ang in range(0, 180, 45):
            a = math.radians(ang)
            line(d, (rc[0] - 11 * math.cos(a), rc[1] - 11 * math.sin(a)), (rc[0] + 11 * math.cos(a), rc[1] + 11 * math.sin(a)), WD, 1)
        disc(d, rc[0], rc[1], 3, rgba(WL))
    else:
        disc(d, rc[0], rc[1], 14, rgba(WD))
        disc(d, rc[0], rc[1], 11, rgba(pal["glow"]))
        disc(d, rc[0], rc[1], 6, rgba(EMBER_L))
        for a0 in (25, 75, 140, 200, 260, 320):
            a = math.radians(a0)
            line(d, rc, (rc[0] + 15 * math.cos(a), rc[1] + 15 * math.sin(a)), WD, 2)
    # nichos
    for nx in (256, 378):
        pointed_arch(img, nx + 5, g - 100, 5, 3, WL, fill_inside=WD)
        rect(d, nx, g - 100, nx + 9, g - 70, WD)
    # portal: arquivoltas concéntricas y puertas
    sp = g - 84
    for hw, col in ((42, WL), (37, WD), (32, WL)):
        pointed_arch(img, 320, sp, hw, 4, col)
        rect(d, 320 - hw, sp, 320 - hw + 3, g, col)
        rect(d, 320 + hw - 4, sp, 320 + hw - 1, g, col)
    pointed_arch(img, 320, sp, 28, 40, DOOR, fill_inside=DOOR)
    rect(d, 292, sp, 347, g, DOOR)
    if not open_doors:
        for hy in (sp + 12, sp + 38):  # herrajes
            rect(d, 292, hy, 347, hy + 1, WL)
        rect(d, 319, g - 118, 320, g - 1, pal["seam"])  # junta de las hojas: brasa que se cuela
        rect(d, 292, g - 1, 347, g - 1, pal["seam"])
        overlay(img, lambda dd: dd.polygon([(300, g), (340, g), (372, g + 36), (268, g + 36)], fill=rgba(EMBER, 28)))
    else:
        def glow(dd):
            for y in range(sp - 30, g):
                t = (y - (sp - 30)) / float(g - sp + 30)
                c = lerp(EMBER_L, EMBER, t)
                dd.line([(295, y), (344, y)], fill=rgba(c, 235))
        overlay(img, glow)
        pointed_arch(img, 320, sp, 26, 6, EMBER_L)
        poly(d, [(290, sp - 6), (298, sp), (298, g), (290, g)], DOOR)
        poly(d, [(349, sp - 6), (341, sp), (341, g), (349, g)], DOOR)
        overlay(img, lambda dd: dd.polygon([(296, g), (344, g), (420, g + 60), (220, g + 60)], fill=rgba(EMBER_L, 70)))
    # escalones
    rect(d, 280, g - 4, 360, g - 1, WL)
    rect(d, 272, g - 1, 368, g + 2, W)
    rect(d, 264, g + 2, 376, g + 5, WD)


def graveyard(img, g, seed, col, light):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    for _ in range(14):
        x = rnd.choice([rnd.randint(8, 250), rnd.randint(390, 630)])
        y = g + rnd.randint(8, 44)
        h = rnd.randint(9, 15)
        d.rounded_rectangle((x, y - h, x + 7, y), radius=3, fill=rgba(col))
        rect(d, x, y - h + 2, x, y, light)
        rect(d, x + 3, y - h + 4, x + 3, y - h + 7, light)
        rect(d, x + 2, y - h + 5, x + 5, y - h + 5, light)


def dead_tree(img, x, g, col, seed):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    def branch(px, py, ang, ln, w, depth):
        if depth == 0 or ln < 4:
            return
        nx, ny = px + ln * math.cos(ang), py - ln * math.sin(ang)
        line(d, (px, py), (nx, ny), col, w)
        branch(nx, ny, ang + rnd.uniform(0.3, 0.7), ln * 0.72, max(1, w - 1), depth - 1)
        branch(nx, ny, ang - rnd.uniform(0.3, 0.7), ln * 0.7, max(1, w - 1), depth - 1)
    branch(x, g + 6, math.pi / 2 + rnd.uniform(-0.1, 0.1), 34, 4, 5)


def path_ground(img, g, ground, path, cobble):
    d = ImageDraw.Draw(img)
    rect(d, 0, g, 639, 359, ground)
    poly(d, [(296, g), (344, g), (452, 359), (188, 359)], path)
    for k in range(1, 9):
        t = (k / 9.0) ** 1.6
        y = g + t * (359 - g)
        xa = 296 + (188 - 296) * t
        xb = 344 + (452 - 344) * t
        d.line([(xa, y), (xb, y)], fill=rgba(cobble))


def make_story():
    g = 312
    # ---- intro: Baldwin de espaldas ante las puertas, de noche; arriba queda libre para el texto
    img = vgrad(640, 360, [(0, (0x0F, 0x12, 0x1B)), (0.28, BG), (0.7, (0x20, 0x28, 0x38)), (1, BG)])
    stars(img, 70, 1, 90)
    d = ImageDraw.Draw(img)
    for hx, hr in ((0, 250), (210, 262), (560, 256)):  # colinas lejanas
        pass
    rnd = random.Random(2)
    for x in range(640):  # silueta de colinas lejanas
        y = int(g - 60 + 10 * math.sin(x / 70.0) + 6 * math.sin(x / 23.0 + 1))
        d.line([(x, y), (x, g)], fill=rgba((0x1B, 0x21, 0x2F)))
    # luna: arco de marfil apagado, bajo la franja del texto
    disc(d, 560, 122, 15, rgba((0xB8, 0xAD, 0x92)))
    disc(d, 566, 118, 13, rgba((0x1C, 0x22, 0x31)))
    halo(img, 560, 122, [34, 26], [10, 16], IVORY_D)
    pal = dict(wall=(0x22, 0x2A, 0x39), wall_l=(0x34, 0x40, 0x54), wall_d=(0x17, 0x1C, 0x28), window=(0x4E, 0x32, 0x26),
               door=(0x0D, 0x0F, 0x16), seam=EMBER, glow=EMBER)
    draw_abbey(img, g, pal)
    path_ground(img, g, (0x13, 0x17, 0x21), (0x27, 0x2F, 0x3E), (0x1C, 0x22, 0x2E))
    graveyard(img, g, 3, (0x2A, 0x33, 0x44), (0x44, 0x52, 0x66))
    dead_tree(img, 40, g, (0x10, 0x13, 0x1C), 4)
    dead_tree(img, 604, g, (0x10, 0x13, 0x1C), 5)

    def mist(dd):
        for y, a in ((g - 6, 14), (g + 6, 18), (g + 22, 14)):
            dd.ellipse((-60, y - 6, 700, y + 8), fill=rgba(IVORY_D, a))
    overlay(img, mist)
    baldwin_back(img, 320, 342, ember_rim=True)
    save(img, STORY / "intro.png")

    # ---- epílogo: amanecer de brasa y marfil sobre la abadía, el sello roto
    img = vgrad(640, 360, [(0, (0x1B, 0x20, 0x2E)), (0.25, (0x4A, 0x36, 0x48)), (0.5, (0xA3, 0x58, 0x3C)),
                           (0.68, EMBER), (0.84, EMBER_L), (1, IVORY)])
    d = ImageDraw.Draw(img)
    stars(img, 22, 6, 40)

    def rays(dd):
        sx, sy = 320, g - 56
        for k in range(-7, 8):
            a = math.pi / 2 + k * 0.17
            w = 0.04
            dd.polygon([(sx, sy), (sx + 700 * math.cos(a - w), sy - 700 * math.sin(a - w)),
                        (sx + 700 * math.cos(a + w), sy - 700 * math.sin(a + w))], fill=rgba(EMBER_L, 22 if k % 2 else 12))
    overlay(img, rays)
    halo(img, 320, g - 56, [86, 66, 50], [28, 50, 90], EMBER_L)
    d = ImageDraw.Draw(img)
    disc(d, 320, g - 56, 36, rgba(IVORY))
    disc(d, 320, g - 56, 30, rgba((0xFF, 0xEB, 0xC8)))
    for x in range(640):  # colinas oscuras con borde cálido
        y = int(g - 40 + 8 * math.sin(x / 60.0 + 2) + 5 * math.sin(x / 19.0))
        d.line([(x, y), (x, g)], fill=rgba((0x4A, 0x2A, 0x2E)))
        put(img, x, y, (0xC9, 0x7A, 0x52))
    pal = dict(wall=(0x25, 0x21, 0x2D), wall_l=(0xC9, 0x7A, 0x52), wall_d=(0x15, 0x14, 0x1D), window=(0x7A, 0x3A, 0x22),
               door=(0x10, 0x0F, 0x16), seam=EMBER_L, glow=EMBER)
    draw_abbey(img, g, pal, open_doors=True, broken=True)
    path_ground(img, g, (0x1A, 0x16, 0x1F), (0x5A, 0x3A, 0x3A), (0x3A, 0x26, 0x2A))
    graveyard(img, g, 7, (0x2A, 0x20, 0x28), (0xA0, 0x62, 0x48))
    dead_tree(img, 40, g, (0x16, 0x12, 0x18), 8)
    dead_tree(img, 604, g, (0x16, 0x12, 0x18), 9)

    # el sello roto: aro de marfil partido en el cielo, con la brasa colándose por la grieta
    def broken_seal(dd):
        cx, cy, r = 320, 68, 38
        for half, (ox, oy) in ((0, (-7, 4)), (1, (7, -3))):
            a0, a1 = (100, 280) if half == 0 else (280, 460)
            dd.arc((cx - r + ox, cy - r + oy, cx + r + ox, cy + r + oy), a0, a1, fill=rgba(IVORY, 255), width=5)
            dd.arc((cx - r + 6 + ox, cy - r + 6 + oy, cx + r - 6 + ox, cy + r - 6 + oy), a0, a1, fill=rgba(IVORY_D, 255), width=2)
        for ang in range(0, 360, 30):
            a = math.radians(ang)
            x, y = cx + (r + 6) * math.cos(a), cy + (r + 6) * math.sin(a)
            if abs(math.cos(a)) < 0.9:
                dd.rectangle((x - 1, y - 1, x + 1, y + 1), fill=rgba(IVORY_D))
        dd.polygon([(cx - 3, cy - r - 8), (cx + 3, cy - r - 6), (cx + 1, cy + r + 8), (cx - 2, cy + r + 6)], fill=rgba(EMBER_L, 235))
        dd.polygon([(cx - 1, cy - r - 4), (cx + 1, cy - r - 4), (cx + 1, cy + r + 4), (cx - 1, cy + r + 4)], fill=rgba(IVORY, 255))
        for fx, fy in ((cx - 30, cy + 44), (cx + 34, cy + 40), (cx - 12, cy + 52), (cx + 14, cy + 60)):
            dd.polygon([(fx, fy), (fx + 4, fy + 2), (fx + 2, fy + 6)], fill=rgba(IVORY, 255))
    halo(img, 320, 68, [58, 48], [18, 30], EMBER)
    overlay(img, broken_seal)

    def mist2(dd):
        for y, a in ((g - 4, 40), (g + 8, 46), (g + 24, 34), (g + 40, 24)):
            dd.ellipse((-60, y - 8, 700, y + 10), fill=rgba(IVORY, a))
    overlay(img, mist2)
    baldwin_back(img, 320, 342, ember_rim=True)
    save(img, STORY / "epilogue.png")


# ------------------------------------------------------------------ audio

RATE = 44100
PEAK = 0.89  # -1 dBFS


def write_wav(path, x, peak=PEAK, fade_ms=0):
    x = np.asarray(x, dtype=np.float64)
    if fade_ms:
        n = int(RATE * fade_ms / 1000.0)
        x = x.copy()
        x[:n] *= np.linspace(0, 1, n)
        x[-n:] *= np.linspace(1, 0, n)
    x = x / max(1e-9, np.max(np.abs(x))) * peak
    pcm = np.round(x * 32767).astype("<i2")
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())


def lowpass(x, cutoff):
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = 1.0 - np.exp(-2.0 * np.pi * np.maximum(cutoff, 1.0) / RATE)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def pnoise(n, lo, hi, rng):
    """Ruido de banda limitada y periódico (se genera en frecuencia): cierra sin costura."""
    freqs = np.fft.rfftfreq(n, 1.0 / RATE)
    spec = np.zeros(len(freqs), complex)
    m = (freqs >= lo) & (freqs <= hi)
    spec[m] = np.exp(1j * rng.uniform(0, 2 * np.pi, m.sum()))
    x = np.fft.irfft(spec, n)
    return x / np.max(np.abs(x))


def fold(buf, n):
    out = buf[:n].copy()
    tail = buf[n:]
    out[:len(tail)] += tail
    return out


def place(buf, start, ev):
    s = int(start * RATE)
    buf[s:s + len(ev)] += ev[:len(buf) - s]


def reverb(x, rng, secs=2.5, decay=2.2, wet=0.4):
    n = len(x)
    t = np.arange(int(secs * RATE)) / RATE
    ir = rng.standard_normal(len(t)) * np.exp(-t * decay * 2.3 / secs * 2.0)
    ir /= np.sqrt(np.sum(ir ** 2))
    y = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(ir, n), n)  # convolución circular: el bucle sigue cerrando
    return x * (1 - wet) + y * wet * 1.5


def q8(f):
    return round(f * 8) / 8.0  # ciclos enteros en 8 s


def make_loops():
    rng = np.random.default_rng(11)
    N = 8 * RATE
    t = np.arange(N) / RATE
    TAU = 2 * np.pi

    # --- amb_cripta: goteo, viento grave y crepitar de brasas
    wind = pnoise(N, 40, 260, rng) * (0.55 + 0.45 * np.sin(TAU * 0.25 * t + 1.0))
    wind2 = pnoise(N, 280, 900, rng) * 0.12 * (0.5 + 0.5 * np.sin(TAU * 0.125 * t))
    drone = 0.20 * np.sin(TAU * 55 * t) + 0.10 * np.sin(TAU * 82.5 * t) + 0.10 * np.sin(TAU * 55.125 * t)
    drips = np.zeros(N + 3 * RATE)
    for ts, f in ((0.8, 1500), (2.9, 1250), (4.4, 1700), (6.3, 1350)):
        tt = np.arange(int(0.5 * RATE)) / RATE
        ph = TAU * (f * 0.45 * tt + f * 0.55 * (1 - np.exp(-tt * 40)) / 40)
        ev = np.sin(ph) * np.exp(-tt * 35) * 0.5
        place(drips, ts, ev)
        place(drips, ts + 0.19, ev * 0.35)
        place(drips, ts + 0.41, ev * 0.15)
    drips = fold(drips, N)
    drips = reverb(drips, rng, 1.8, 1.6, 0.35)
    crack = np.zeros(N + RATE // 2)
    for _ in range(46):
        ts = rng.uniform(0, 8.0)
        n = int(rng.uniform(0.004, 0.02) * RATE)
        ev = np.diff(rng.standard_normal(n + 1)) * np.exp(-np.arange(n) / (n / 4.0)) * rng.uniform(0.05, 0.6) ** 2
        place(crack, ts, ev)
    crack = fold(crack, N)
    hiss = pnoise(N, 3000, 9000, rng) * 0.03 * (0.5 + 0.5 * np.sin(TAU * 0.375 * t + 2))
    x = wind * 0.9 + wind2 + drone + drips * 0.8 + crack * 1.6 + hiss
    write_wav(AUDIO / "amb_cripta.wav", np.tanh(1.3 * x))

    # --- amb_capilla: coro / órgano tenue con reverberación simulada
    notes = [73.42, 110.0, 146.83, 174.61, 220.0, 293.66, 349.23, 440.0]
    x = np.zeros(N)
    for k, f in enumerate(notes):
        f = q8(f)
        vib = 0.0035 * f ** 0.35 * np.sin(TAU * 0.5 * t + k)
        swell = 0.6 + 0.4 * np.sin(TAU * (0.125 * (1 + k % 3)) * t + k * 1.7)
        for h, a in ((1, 1.0), (2, 0.35), (3, 0.16)):
            for det in (0.0, 0.25 if k % 2 else -0.25):
                x += (0.12 / (1 + 0.15 * k)) * a * swell * np.sin(TAU * (f * h + det) * t + vib * h + k)
    breath = pnoise(N, 800, 3000, rng) * 0.004 * (0.5 + 0.5 * np.sin(TAU * 0.25 * t))
    x = reverb(x + breath, rng, 3.5, 2.0, 0.6)
    write_wav(AUDIO / "amb_capilla.wav", x)

    # --- boss_loop: percusión grave rítmica con un pulso tenso (120 bpm, 16 tiempos)
    beat = 0.5
    buf = np.zeros(N + 2 * RATE)
    tk = np.arange(int(0.6 * RATE)) / RATE
    kick = np.sin(TAU * (42 * tk + 95 / 28.0 * (1 - np.exp(-28 * tk)))) * np.exp(-tk * 7.5)
    kick += np.diff(rng.standard_normal(len(tk) + 1)) * np.exp(-tk * 200) * 0.12
    tom = np.sin(TAU * (62 * tk + 40 / 12.0 * (1 - np.exp(-12 * tk)))) * np.exp(-tk * 6)
    tom += lowpass(rng.standard_normal(len(tk)), 500) * np.exp(-tk * 30) * 0.5
    for b in range(16):
        place(buf, b * beat, kick * (1.0 if b % 4 == 0 else 0.7))
    for b in (2.5, 6.5, 10.5, 11.5, 14.5, 15.0, 7.0):
        place(buf, b * beat, tom * 0.7)
    for b in (3.75, 7.75, 15.75):  # doble golpe de pulso
        place(buf, b * beat, tom * 0.45)
    perc = fold(buf, N)
    pulse_env = (0.5 + 0.5 * np.cos(TAU * 2 * t)) ** 3
    tension = (0.10 * np.sin(TAU * 55 * t) + 0.08 * np.sin(TAU * q8(58.27) * t)) * (0.55 + 0.45 * np.sin(TAU * 8 * t))
    shimmer = 0.045 * pulse_env * (np.sin(TAU * q8(659.25) * t) + np.sin(TAU * 660 * t))
    cluster = 0.04 * sum(np.sin(TAU * q8(f) * t) for f in (110, 116.54, 164.81))
    write_wav(AUDIO / "boss_loop.wav", np.tanh(1.2 * (perc * 0.9 + tension + shimmer + cluster)))


def make_sfx():
    rng = np.random.default_rng(23)
    T = lambda s: np.arange(int(s * RATE)) / RATE
    TAU = 2 * np.pi

    # lanzamiento del acólito: soplido que sube y baja + ronroneo de brasa
    t = T(0.4)
    fc = 500 + 3200 * np.sin(np.pi * np.minimum(t / 0.4, 1.0)) ** 1.5
    n = rng.standard_normal(len(t))
    band = lowpass(n, fc) - lowpass(n, 260)
    env = np.sin(np.pi * np.minimum(t / 0.4, 1.0)) ** 1.4
    thrum = np.sin(TAU * (240 * t - 220 * t * t / 2 * 0.9)) * np.exp(-t * 7) * 0.5
    pops = np.zeros(len(t))
    for ts in (0.05, 0.11, 0.17):
        k = int(ts * RATE)
        pops[k:k + 300] += np.diff(rng.standard_normal(301)) * np.exp(-np.arange(300) / 60.0) * 0.4
    write_wav(AUDIO / "sfx_throw.wav", band * env * 1.4 + thrum + pops, fade_ms=4)

    # aviso del tajo: chirrido metálico ascendente (raspado de acero)
    dur = 0.6
    t = T(dur)
    f = 600 * np.exp(np.log(4400 / 600.0) * (t / dur) ** 1.2)
    ph = TAU * np.cumsum(f) / RATE
    saw = 2 * ((ph / TAU) % 1.0) - 1
    metal = saw * 0.5 + 0.35 * np.sign(np.sin(2.76 * ph)) * 0.5 + 0.25 * np.sin(5.4 * ph)
    scrape = 0.5 + 0.5 * np.sin(TAU * 55 * t)
    hi = np.diff(rng.standard_normal(len(t) + 1)) * 0.25
    env = np.minimum(1.0, t / 0.02) * (t / dur) ** 1.2
    x = (metal * (0.6 + 0.4 * scrape) + hi) * env
    k = int(0.5 * RATE)
    tt = T(0.1)
    x[k:k + len(tt)] += np.sin(TAU * 3300 * tt) * np.exp(-tt * 35) * 0.9  # destello final
    x[int(0.58 * RATE):] *= np.linspace(1, 0.0, len(x) - int(0.58 * RATE))
    write_wav(AUDIO / "sfx_tell_sweep.wav", x, fade_ms=3)

    # aviso de la lluvia: campana grave que se apaga (tonal y descendente, nada que ver con el chirrido)
    t = T(0.8)
    x = np.zeros(len(t))
    for r, a, dc in ((0.5, 0.5, 3.0), (1.0, 1.0, 4.0), (1.19, 0.55, 5.0), (1.56, 0.35, 6.0), (2.0, 0.5, 6.5),
                     (2.74, 0.3, 8.0), (3.76, 0.18, 11.0), (5.4, 0.1, 14.0)):
        x += a * np.sin(TAU * 392 * r * t * (1 - 0.02 * t)) * np.exp(-t * dc)
    x *= np.minimum(1.0, t / 0.003)
    x += np.diff(rng.standard_normal(len(t) + 1)) * np.exp(-t * 300) * 0.25
    x[int(0.7 * RATE):] *= np.linspace(1, 0, len(x) - int(0.7 * RATE))
    write_wav(AUDIO / "sfx_tell_rain.wav", x, fade_ms=2)

    # rugido del cambio de fase: gruñido grave con modulación
    t = T(0.8)
    f0 = 74 - 28 * (t / 0.8)
    ph = TAU * np.cumsum(f0) / RATE
    saw = sum(np.sin(h * ph) / h ** 0.8 for h in range(1, 14))
    fc = 900 - 650 * (t / 0.8)
    body = lowpass(saw, fc)
    growl = 0.55 + 0.45 * np.sin(TAU * 29 * t)
    breath = lowpass(rng.standard_normal(len(t)), 700) * 0.7
    x = np.tanh(2.2 * (body * growl * 0.5 + breath * 0.25))
    env = np.minimum(1.0, t / 0.07) * np.where(t > 0.55, np.maximum(0.0, 1 - (t - 0.55) / 0.25), 1.0)
    write_wav(AUDIO / "sfx_roar.wav", x * env, fade_ms=3)

    # brasero que se enciende: soplo, crepitar y acorde ascendente
    t = T(0.7)
    n = rng.standard_normal(len(t))
    fc = 250 + 2600 * np.clip(t / 0.3, 0, 1)
    whoosh = lowpass(n, fc) * (np.clip(t / 0.25, 0, 1) * np.exp(-np.maximum(t - 0.25, 0) * 5))
    x = whoosh * 0.9
    for i, (fq, ts) in enumerate(((330, 0.08), (495, 0.2), (660, 0.32))):
        m = t >= ts
        x[m] += (0.4 * np.sin(TAU * fq * (t[m] - ts)) + 0.12 * np.sin(TAU * 2 * fq * (t[m] - ts))) * np.exp(-(t[m] - ts) * 5)
    for ts in (0.02, 0.12, 0.2, 0.27, 0.36, 0.44, 0.52):
        k = int(ts * RATE)
        x[k:k + 250] += np.diff(rng.standard_normal(251)) * np.exp(-np.arange(250) / 50.0) * rng.uniform(0.2, 0.5)
    x[int(0.62 * RATE):] *= np.linspace(1, 0, len(x) - int(0.62 * RATE))
    write_wav(AUDIO / "sfx_checkpoint.wav", x, fade_ms=3)

    # brasa contra el suelo: golpe sordo y siseo
    t = T(0.3)
    thump = np.sin(TAU * (50 * t + 110 / 14.0 * (1 - np.exp(-14 * t)))) * np.exp(-t * 14)
    click = np.diff(rng.standard_normal(len(t) + 1)) * np.exp(-t * 90) * 0.4
    sizz = np.diff(rng.standard_normal(len(t) + 1)) * np.exp(-t * 11) * 0.12 * (rng.random(len(t)) > 0.5)
    x = thump + click + sizz
    x[int(0.26 * RATE):] *= np.linspace(1, 0, len(x) - int(0.26 * RATE))
    write_wav(AUDIO / "sfx_ember_impact.wav", x, fade_ms=2)


# ------------------------------------------------------------------ hojas de contacto

def on_bg(im):
    base = new(im.width, im.height, BG)
    base.alpha_composite(im)
    return base


def to_gray(im):
    return on_bg(im).convert("L").convert("RGBA")


def sheet_canvas(entries, scale=3, width=1920, pad=10, title=None):
    """entries: [(etiqueta, imagen, marcas)] con marcas = (x_origen, fila_pies) o None."""
    items = []
    for label, im, marks in entries:
        big = on_bg(im).resize((im.width * scale, im.height * scale), Image.NEAREST)
        if marks:
            dd = ImageDraw.Draw(big)
            ox, fy = marks
            dd.line([(ox * scale + scale // 2, 0), (ox * scale + scale // 2, big.height)], fill=(255, 0, 255, 255), width=1)
            dd.line([(0, fy * scale + scale - 1), (big.width, fy * scale + scale - 1)], fill=(0, 255, 255, 255), width=1)
        items.append((label, big))
    x, y, rowh = pad, pad + (16 if title else 0), 0
    pos = []
    for label, big in items:
        if x + big.width + pad > width and x > pad:
            x, y, rowh = pad, y + rowh + 18 + pad, 0
        pos.append((x, y + 14))
        x += max(big.width, 60) + pad
        rowh = max(rowh, big.height)
    canvas = new(width, y + rowh + 14 + pad + 6, (0x0A, 0x0C, 0x12))
    dd = ImageDraw.Draw(canvas)
    if title:
        dd.text((pad, pad - 2), title, fill=rgba(EMBER))
    for (label, big), (px, py) in zip(items, pos):
        dd.text((px, py - 12), label, fill=rgba(IVORY_D))
        canvas.paste(big, (px, py))
    return canvas


def frames_of(sheet_path, cw, name, marks=None, gray=False):
    sh = Image.open(sheet_path).convert("RGBA")
    out = []
    for i in range(sh.width // cw):
        f = sh.crop((i * cw, 0, (i + 1) * cw, sh.height))
        out.append((f"{name} {i}" + (" gris" if gray else ""), to_gray(f) if gray else f, marks))
    return out


def scene(far, mid, floor_top, floor_fill, platform, props, shift=320):
    """Escena de prueba: el fondo se desplaza media pantalla para que la costura caiga en el centro."""
    def roll(p):
        a = np.roll(np.array(Image.open(p).convert("RGBA")), shift, axis=1)
        return Image.fromarray(a, "RGBA")
    img = roll(far)
    img.alpha_composite(roll(mid))
    ft, ff, pl = (Image.open(p).convert("RGBA") for p in (floor_top, floor_fill, platform))
    for x in range(0, 640, 16):
        img.alpha_composite(ft, (x, 296))
        for y in range(312, 360, 16):
            img.alpha_composite(ff, (x, y))
    for x in range(176, 240, 16):
        img.alpha_composite(pl, (x, 236))
    for p, x, y in props:
        pi = Image.open(p).convert("RGBA")
        img.alpha_composite(pi, (x, y if y >= 0 else 296 + y - pi.height + 16 * 0))
    return img


def make_previews():
    PREV.mkdir(parents=True, exist_ok=True)
    (PREV / ".gdignore").write_bytes(b"")
    L = lambda p: Image.open(p).convert("RGBA")
    # Cripta
    props = [(CRIPTA / "niche_skulls.png", 70, 264), (CRIPTA / "coffin.png", 250, 280), (CRIPTA / "candles.png", 300, 280),
             (CRIPTA / "chain.png", 420, 0), (CRIPTA / "chain.png", 520, 0), (COMMON / "inscription.png", 360, 272)]
    sc = scene(CRIPTA / "bg_far.png", CRIPTA / "bg_mid.png", CRIPTA / "floor_top.png", CRIPTA / "floor_fill.png", CRIPTA / "platform.png",
               [(p, x, y) for p, x, y in props])
    ent = [(n, L(CRIPTA / n), None) for n in ("floor_top.png", "floor_fill.png", "platform.png", "niche_skulls.png", "coffin.png", "chain.png", "candles.png")]
    ent.append(("common/inscription.png", L(COMMON / "inscription.png"), None))
    ent.append(("escena de prueba (fondo desplazado 320 px: la costura cae en el centro)", sc, None))
    ent.append(("bg_far.png sin desplazar", L(CRIPTA / "bg_far.png"), None))
    ent.append(("bg_mid.png sobre bg_far (sin desplazar)", (lambda a, b: (a.alpha_composite(b), a)[1])(L(CRIPTA / "bg_far.png"), L(CRIPTA / "bg_mid.png")), None))
    sheet_canvas(ent, title="Cripta de las Ascuas (x3)").save(PREV / "cripta.png")
    # Capilla
    props = [(CAPILLA / "lectern.png", 80, 264), (CAPILLA / "altar.png", 250, 264), (CAPILLA / "statue.png", 400, 232),
             (CAPILLA / "statue.png", 520, 232)]
    sc = scene(CAPILLA / "bg_far.png", CAPILLA / "bg_mid.png", CAPILLA / "floor_top.png", CAPILLA / "floor_fill.png", CAPILLA / "platform.png", props)
    ent = [(n, L(CAPILLA / n), None) for n in ("floor_top.png", "floor_fill.png", "platform.png", "lectern.png", "altar.png", "statue.png")]
    ent.append(("escena de prueba (costura al centro)", sc, None))
    ent.append(("bg_far.png sin desplazar", L(CAPILLA / "bg_far.png"), None))
    ent.append(("bg_mid.png sobre bg_far (sin desplazar)", (lambda a, b: (a.alpha_composite(b), a)[1])(L(CAPILLA / "bg_far.png"), L(CAPILLA / "bg_mid.png")), None))
    sheet_canvas(ent, title="Capilla del Ultimo Sello (x3)").save(PREV / "capilla.png")
    # Enemigos (color y grises; rejilla: columna del origen en magenta, fila de pies en cian)
    ent = []
    for g in (False, True):
        ent += frames_of(ENEMY / "acolito.png", 64, "acolito", (32, 47), g)
        ent += frames_of(ENEMY / "custodio_sellado.png", 96, "custodio_sellado", (48, 47), g)
        ent += frames_of(ENEMY / "custodio.png", 96, "custodio (actual)", (48, 47), g)
        ent += frames_of(ENEMY / "ember_orb.png", 12, "ember_orb", None, g)
    sheet_canvas(ent, width=1920, title="Enemigos (x3, color y grises)").save(PREV / "enemigos.png")
    # Jefe
    ent = []
    names = ["0 reposo", "1 anticipa tajo", "2 tajo", "3 recup. VULN", "4 anticipa lluvia", "5 lanza lluvia", "6 agotado VULN", "7 rugido", "8 derrotado"]
    for g in (False, True):
        sh = Image.open(BOSS / "abad.png").convert("RGBA")
        for i in range(9):
            f = sh.crop((i * 224, 0, (i + 1) * 224, 128))
            ent.append(("abad " + names[i] + (" gris" if g else ""), to_gray(f) if g else f, (112, 120)))
    for g in (False, True):
        ent += frames_of(BOSS / "falling_ember.png", 16, "falling_ember", None, g)
    ent.append(("ember_marker", L(BOSS / "ember_marker.png"), None))
    sheet_canvas(ent, width=2064, title="Abad Sellado (x3; magenta = origen x, cian = pies fila 120)").save(PREV / "jefe.png")
    # Baldwin
    ent = []
    for g in (False, True):
        for nm, n in (("Idle", 4), ("Walk", 8), ("Jump", 6), ("Attack", 5), ("Dead", 6), ("Hurt", 2)):
            ent += frames_of(BALDWIN / f"{nm}.png", 128, nm, (32, 127), g)
    for nm in ("Idle", "Walk", "Jump", "Attack", "Dead", "Hurt"):  # superposición de celdas
        sh = Image.open(BALDWIN / f"{nm}.png").convert("RGBA")
        acc = new(128, 128, BG)
        for i in range(sh.width // 128):
            f = sh.crop((i * 128, 0, (i + 1) * 128, 128))
            a = np.array(f)
            a[..., 3] = (a[..., 3] * 0.45).astype(np.uint8)
            acc.alpha_composite(Image.fromarray(a, "RGBA"))
        ent.append((f"superpuesto {nm}", acc, (32, 127)))
    ent.append(("Baldwin_Sword", L(WEAPONS / "Baldwin_Sword.png"), None))
    ent.append(("Crypt_Mace", L(WEAPONS / "Crypt_Mace.png"), None))
    ent.append(("Copper_Sword (actual)", L(WEAPONS / "Copper_Sword.png"), None))
    sheet_canvas(ent, width=1960, title="Baldwin (x3; magenta = columna 32, cian = fila 127)").save(PREV / "baldwin.png")
    # Historia
    ent = [("intro.png", L(STORY / "intro.png"), None), ("epilogue.png", L(STORY / "epilogue.png"), None)]
    sheet_canvas(ent, width=1960, title="Historia (x3)").save(PREV / "historia.png")


# ------------------------------------------------------------------ verificación y manifiesto

S = "Sprites/"
SPEC = [
    # (ruta, (ancho, alto), cuadros, uso)
    (S + "Environment/Cripta/floor_top.png", (16, 16), 1, "Borde superior pisable de la Cripta"),
    (S + "Environment/Cripta/floor_fill.png", (16, 16), 1, "Relleno en mosaico de la Cripta"),
    (S + "Environment/Cripta/platform.png", (16, 16), 1, "Losa de plataforma de la Cripta"),
    (S + "Environment/Cripta/bg_far.png", (640, 360), 1, "Fondo lejano opaco (mosaico horizontal, periodo 160)"),
    (S + "Environment/Cripta/bg_mid.png", (640, 360), 1, "Plano medio con transparencia (mosaico horizontal, periodo 128)"),
    (S + "Environment/Cripta/niche_skulls.png", (32, 32), 1, "Utilería: nicho de calaveras"),
    (S + "Environment/Cripta/coffin.png", (32, 16), 1, "Utilería: ataúd"),
    (S + "Environment/Cripta/chain.png", (8, 64), 1, "Utilería: cadena colgante"),
    (S + "Environment/Cripta/candles.png", (16, 16), 1, "Utilería: velas en el suelo"),
    (S + "Environment/Capilla/floor_top.png", (16, 16), 1, "Borde superior pisable de la Capilla (mármol)"),
    (S + "Environment/Capilla/floor_fill.png", (16, 16), 1, "Relleno en mosaico de la Capilla"),
    (S + "Environment/Capilla/platform.png", (16, 16), 1, "Losa de plataforma de la Capilla"),
    (S + "Environment/Capilla/bg_far.png", (640, 360), 1, "Nave con vitrales apagados (mosaico, periodo 160)"),
    (S + "Environment/Capilla/bg_mid.png", (640, 360), 1, "Columnas de mármol (mosaico, periodo 128)"),
    (S + "Environment/Capilla/lectern.png", (16, 32), 1, "Utilería: atril"),
    (S + "Environment/Capilla/altar.png", (48, 32), 1, "Utilería: altar"),
    (S + "Environment/Capilla/statue.png", (32, 64), 1, "Utilería: estatua de caballero"),
    (S + "Environment/Common/inscription.png", (32, 24), 1, "Lápida o placa con runas marfil"),
    (S + "Enemies/acolito.png", (256, 48), 4, "Acólito de la Ascua: hoja 4x64x48; origen (32,24), pies fila 47; mano de lanzamiento en el cuadro 2 hacia (46,16)"),
    (S + "Enemies/ember_orb.png", (24, 12), 2, "Proyectil del acólito: hoja 2x12x12 (el segundo cuadro parpadea)"),
    (S + "Enemies/custodio_sellado.png", (384, 48), 4, "Custodio sellado: hoja 4x96x48; origen (48,24), pies fila 47; golpe de x 54 a 90"),
    (S + "Bosses/abad.png", (2016, 128), 9, "Abad Sellado: hoja 9x224x128; origen (112,64), pies fila 120"),
    (S + "Bosses/falling_ember.png", (32, 32), 2, "Brasa que cae: hoja 2x16x32"),
    (S + "Bosses/ember_marker.png", (32, 8), 1, "Marca de aviso en el suelo"),
    (S + "Items/Weapons/Crypt_Mace.png", (64, 64), 1, "Icono de la Maza de la Cripta"),
    (S + "Items/Weapons/Baldwin_Sword.png", (64, 64), 1, "Icono de la espada de Baldwin"),
    (S + "Story/intro.png", (640, 360), 1, "Ilustración de introducción (franja superior libre para texto)"),
    (S + "Story/epilogue.png", (640, 360), 1, "Ilustración del epílogo"),
    (S + "Characters/Baldwin/Idle.png", (512, 128), 4, "Baldwin, reposo (celdas 128x128, pies fila 127, centro columna 32)"),
    (S + "Characters/Baldwin/Walk.png", (1024, 128), 8, "Baldwin, andar"),
    (S + "Characters/Baldwin/Jump.png", (768, 128), 6, "Baldwin, salto"),
    (S + "Characters/Baldwin/Attack.png", (640, 128), 5, "Baldwin, ataque (0-3 anticipación, 4 tajo con estela en x 38-92, filas 76-116)"),
    (S + "Characters/Baldwin/Dead.png", (768, 128), 6, "Baldwin, muerte"),
    (S + "Characters/Baldwin/Hurt.png", (256, 128), 2, "Baldwin, daño"),
]
AUDIO_SPEC = [
    ("amb_cripta.wav", "Ambiente de la Cripta (bucle de 8 s)", 8.0),
    ("amb_capilla.wav", "Ambiente de la Capilla (bucle de 8 s)", 8.0),
    ("boss_loop.wav", "Música del jefe (bucle de 8 s)", 8.0),
    ("sfx_throw.wav", "Lanzamiento del acólito", None),
    ("sfx_tell_sweep.wav", "Aviso del tajo (chirrido metálico ascendente)", None),
    ("sfx_tell_rain.wav", "Aviso de la lluvia (campana)", None),
    ("sfx_roar.wav", "Rugido del cambio de fase", None),
    ("sfx_checkpoint.wav", "Brasero que se enciende", None),
    ("sfx_ember_impact.wav", "Brasa contra el suelo", None),
]


def verify():
    ok = True
    rows = []
    for rel, (w, h), n, uso in SPEC:
        im = Image.open(ROOT / rel)
        good = im.size == (w, h) and im.mode == "RGBA"
        ok &= good
        rows.append((rel, im.size, n, uso, good))
    arows = []
    for name, uso, loop in AUDIO_SPEC:
        with wave.open(str(AUDIO / name)) as w:
            dur = w.getnframes() / w.getframerate()
            pcm = np.frombuffer(w.readframes(w.getnframes()), "<i2")
            good = w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == 44100
            good &= (w.getnframes() == 8 * 44100) if loop else (dur <= 0.8)
        peak = 20 * math.log10(np.max(np.abs(pcm)) / 32768.0)
        seam = abs(int(pcm[0]) - int(pcm[-1])) / 32768.0
        ok &= good
        arows.append((name, uso, dur, peak, seam, good))
    far_opaque = np.array(Image.open(CRIPTA / "bg_far.png"))[..., 3].min() == 255 and np.array(Image.open(CAPILLA / "bg_far.png"))[..., 3].min() == 255
    return ok, rows, arows, far_opaque


PROV_AUTHOR = "Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py)"


def write_manifest(rows, arows):
    L = ["# Manifiesto de assets de la etapa 5", "",
         "Generado por `tools/gen_zone_assets.py` (dibujo y síntesis por código con Pillow y numpy; semillas fijas; sin archivos de terceros ni servicios externos). Este archivo lo reescribe el propio script.", "",
         "Todos los personajes miran a la derecha; el juego los voltea. Las hojas son tiras horizontales de cuadros del mismo tamaño.", "",
         "## Imágenes", "", "| Archivo | Medida | Cuadros | Uso |", "| --- | --- | --- | --- |"]
    for rel, size, n, uso, _ in rows:
        L.append(f"| `{rel}` | {size[0]}×{size[1]} | {n} | {uso} |")
    L += ["", "## Audio (WAV mono, 16 bits, 44,1 kHz; pico en torno a −1 dBFS)", "", "| Archivo | Duración | Pico | Uso |", "| --- | --- | --- | --- |"]
    for name, uso, dur, peak, seam, _ in arows:
        L.append(f"| `Audio/{name}` | {dur:.3f} s | {peak:.1f} dBFS | {uso} |")
    L += ["",
          "Los bucles de 8 s se generan con ruido periódico, frecuencias de ciclos enteros y colas plegadas sobre el inicio, de modo que cierran sin chasquido. Al estar los bucles normalizados al mismo pico que los efectos, conviene bajar su `volume_db` en el bus Music.", "",
          "## Notas de integración", "",
          "- Acólito: la mano que lanza está en (46,16) del cuadro 2 (cuadro de 64×48, origen en (32,24)). El cuadro 1 lleva el incensario sobre la cabeza.",
          "- Abad: el cuadro 2 barre de x 112 a x 208 entre las filas 96 y 120; los cuadros 3 y 6 tienen el sello brillando (vulnerable); los cuadros 1 y 4 son poses claramente distintas (guadaña atrás y en alto frente a incensario sobre la cabeza).",
          "- Baldwin: celdas de 128×128; pies en la fila 127 y centro del cuerpo en la columna 32 en todos los cuadros (en Jump, el pie más bajo toca la fila 127 aunque el personaje esté en el aire; en Dead 3-5 el cuerpo rota y queda tumbado sobre la fila 127). La estela del cuadro 4 de Attack cubre x 38-92, filas 76-116.",
          "- `platform.png` (Cripta y Capilla) es opaco en los 16×16; `bg_mid.png` de ambas zonas tiene transparencia.", "",
          "## Filas para `docs/assets.md`", "",
          "Columnas: Archivo | Uso | Autor | Fuente | Permiso de distribución | Créditos | Estado.", "",
          "| Archivo | Uso | Autor | Fuente | Permiso de distribución | Créditos | Estado |", "| --- | --- | --- | --- | --- | --- | --- |"]
    groups = [
        ("`Sprites/Environment/Cripta/*.png` (tiles de 16 px, bg_far, bg_mid, niche_skulls, coffin, chain, candles), `Sprites/Environment/Capilla/*.png` (tiles de 16 px, bg_far, bg_mid, lectern, altar, statue), `Sprites/Environment/Common/inscription.png`", "Zonas Cripta de las Ascuas y Capilla del Último Sello"),
        ("`Sprites/Enemies/acolito.png` (4×64×48), `ember_orb.png` (2×12×12), `custodio_sellado.png` (4×96×48)", "Enemigos de la etapa 5"),
        ("`Sprites/Bosses/abad.png` (9×224×128), `falling_ember.png` (2×16×32), `ember_marker.png` (32×8)", "Jefe: el Abad Sellado y sus ataques"),
        ("`Sprites/Characters/Baldwin/*.png` (Idle, Walk, Jump, Attack, Dead, Hurt; celdas de 128×128)", "Jugador (Baldwin); sustituye a `Sprites/Characters/Knight_1/`"),
        ("`Sprites/Items/Weapons/Crypt_Mace.png`, `Baldwin_Sword.png` (64×64)", "Iconos de la Maza de la Cripta y de la espada de Baldwin"),
        ("`Sprites/Story/intro.png`, `epilogue.png` (640×360)", "Ilustraciones de introducción y epílogo"),
        ("`Audio/amb_cripta.wav`, `amb_capilla.wav`, `boss_loop.wav`, `sfx_throw.wav`, `sfx_tell_sweep.wav`, `sfx_tell_rain.wav`, `sfx_roar.wav`, `sfx_checkpoint.wav`, `sfx_ember_impact.wav`", "Ambientes, música del jefe y efectos de la etapa 5"),
    ]
    for files, uso in groups:
        L.append(f"| {files} | {uso} | {PROV_AUTHOR} | Este repositorio | Propio | — | Candidato a final |")
    DOCS5.mkdir(parents=True, exist_ok=True)
    (DOCS5 / "assets_manifest.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    for folder in (CRIPTA, CAPILLA, COMMON, ENEMY, BOSS, WEAPONS, STORY, BALDWIN, AUDIO):
        folder.mkdir(parents=True, exist_ok=True)
    make_cripta_tiles()
    make_cripta_bg()
    make_cripta_props()
    make_capilla_tiles()
    make_capilla_bg()
    make_capilla_props()
    make_inscription()
    make_acolyte()
    make_custodio_sellado()
    make_boss()
    make_baldwin()
    make_weapon_icons()
    make_story()
    make_loops()
    make_sfx()
    ok, rows, arows, far_opaque = verify()
    make_previews()
    write_manifest(rows, arows)
    for rel, size, n, uso, good in rows:
        print(("OK  " if good else "FALLA"), rel, size, n)
    for name, uso, dur, peak, seam, good in arows:
        print(("OK  " if good else "FALLA"), "Audio/" + name, f"{dur:.3f}s pico {peak:.1f} dBFS salto en la costura {seam:.4f}")
    for z, p in (("Cripta", CRIPTA), ("Capilla", CAPILLA)):
        for n in ("bg_far", "bg_mid"):
            print(f"costura {z}/{n}: diferencia media entre última y primera columna", round(check_seam(Image.open(p / f'{n}.png')), 2))
    print("bg_far opacos:", far_opaque)
    print("TODO CORRECTO" if ok else "HAY ERRORES")


if __name__ == "__main__":
    main()
