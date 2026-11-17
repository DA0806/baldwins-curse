#!/usr/bin/env python3
"""Convierte los renders de los modelos de Meshy en sprites de pixel art.

Cada render (Art/Meshy/renders/*.png, 1024x1024 con fondo transparente) se
recorta, se reduce al tamaño exacto del sprite que sustituye (apoyado en el
borde inferior), se cuantiza a la paleta de docs/arte.md y recibe un contorno
claro de 1 px. Los nombres y tamaños coinciden con los del juego, así que las
escenas no cambian.

    python3 tools/meshy_to_sprites.py            # escribe en Art/Meshy/sprites
    python3 tools/meshy_to_sprites.py --install  # además copia a Sprites/
"""
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / "Art/Meshy/renders"
OUT = ROOT / "Art/Meshy/sprites"

GUIDE = ["151924", "1c2230", "232b37", "303b4a", "3e4b5e", "6d8297", "e5d6b3", "a99c80",
         "b96a47", "7a3a22", "f0a758", "ffd59a"]
STEEL = (0x6D, 0x82, 0x97)
IVORY = (0xE5, 0xD6, 0xB3)
EMBER = (0xF0, 0xA7, 0x58)
COPPER = (0xB9, 0x6A, 0x47)


def palette_image():
    base = [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in GUIDE]
    colors = list(base)
    for i, a in enumerate(base):  # tonos intermedios entre colores vecinos
        for b in base[i + 1:]:
            mid = tuple((x + y) // 2 for x, y in zip(a, b))
            if mid not in colors:
                colors.append(mid)
    colors = colors[:256]
    flat = [c for rgb in colors for c in rgb] + [0] * (768 - 3 * len(colors))
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat)
    return pal


PAL = palette_image()


def fit(name, box_w, box_h, fill=1.0):
    """Recorta el render y lo ajusta dentro de box_w x box_h, apoyado abajo y centrado."""
    img = Image.open(RENDERS / f"{name}.png").convert("RGBA")
    img = img.crop(img.getbbox())
    scale = min(box_w * fill / img.width, box_h * fill / img.height)
    w, h = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    small = img.resize((w, h), Image.LANCZOS)
    alpha = small.split()[3].point(lambda a: 255 if a > 110 else 0)
    rgb = small.convert("RGB").quantize(palette=PAL, dither=Image.Dither.NONE).convert("RGB")
    sprite = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    piece = Image.merge("RGBA", (*rgb.split(), alpha))
    sprite.paste(piece, ((box_w - w) // 2, box_h - h), piece)
    return sprite


def rim(img, color=STEEL, alpha=200):
    """Contorno claro alrededor para separar la silueta del fondo oscuro."""
    src = img.copy()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if src.getpixel((x, y))[3]:
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src.getpixel((nx, ny))[3]:
                    img.putpixel((x, y), (*color, alpha))
                    break
    return img


def save(img, rel):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def chevrons(d, x, y, color=IVORY):
    for dx in (0, 7):
        d.polygon([(x + dx, y), (x + dx + 8, y + 8), (x + dx, y + 16), (x + dx, y + 12),
                   (x + dx + 4, y + 8), (x + dx, y + 4)], fill=(*color, 255))


def build():
    # Utilería: mismos tamaños que los sprites actuales.
    save(rim(fit("candelabro", 24, 32)), "Environment/Atrio/candelabra.png")
    save(rim(fit("urna", 16, 16)), "Environment/Atrio/urn.png")
    save(rim(fit("lapida", 32, 16)), "Environment/Atrio/tomb.png")
    save(rim(fit("pedestal", 32, 16)), "Environment/Atrio/pedestal.png")

    # Estandarte: la flecha del modelo apunta arriba; se añade el chevrón
    # hacia la salida para conservar la pista de ruta.
    banner = fit("estandarte", 32, 32)
    bd = ImageDraw.Draw(banner)  # chevrón pequeño hacia la salida en la esquina inferior
    for dx in (0, 4):
        bd.polygon([(20 + dx, 22), (24 + dx, 26), (20 + dx, 30)], fill=(*IVORY, 255))
    save(rim(banner), "Environment/Atrio/banner.png")

    # Arco de salida: interior encendido (brasa) y chevrón de ruta.
    arch = fit("arco_salida", 48, 96)
    # Sólo el hueco de la puerta (píxeles oscuros o rosados del centro) se enciende.
    px = arch.load()
    top = arch.getbbox()[1]
    for y in range(top, 96):
        for x in range(12, 36):
            r, g, b, a = px[x, y]
            dark = a and (r + g + b < 200 or (r > 170 and g < 170 and b < 170))
            if dark:
                t = (y - top) / max(1, 95 - top)
                c = tuple(int(EMBER[i] * (0.45 + 0.55 * t)) for i in range(3))
                px[x, y] = (*c, 255)
    chevrons(ImageDraw.Draw(arch), 16, 70)
    save(arch, "Environment/Atrio/arch_exit.png")

    # Brasero: cuadro 0 apagado (brasas en ceniza) y 3 cuadros de llama.
    lit = fit("brasero", 32, 32)
    sheet = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    for frame in range(4):
        img = lit.copy()
        px = img.load()
        for y in range(32):
            for x in range(32):
                r, g, b, a = px[x, y]
                warm = a and r > 150 and r > b + 60
                if frame == 0 and warm:
                    px[x, y] = (0x3E, 0x4B, 0x5E, a)  # ceniza
                elif frame > 0 and warm and (x + y + frame) % 3 == 0:
                    px[x, y] = (0xFF, 0xD5, 0x9A, a)  # parpadeo de la llama
        sheet.paste(rim(img), (frame * 32, 0))
    save(sheet, "Environment/Atrio/brazier.png")

    # Máscaras: iconos de 64x64 (también el pickup).
    save(rim(fit("mascara_voto", 64, 64, 0.9), IVORY, 160), "Items/Masks/Mask_Vow.png")
    save(rim(fit("mascara_ascua", 64, 64, 0.9), EMBER, 160), "Items/Masks/Mask_Ember.png")

    # Custodio: 4 poses de 96x48. El modelo es estático; la pose se marca con
    # la inclinación del cuerpo y la hoja dibujada encima (alzada en la
    # anticipación, extendida 54..90 en el golpe = zona de golpe real).
    body = fit("custodio", 30, 48)
    poses = [(0, None), (-2, [(44, 15), (44, 0)]), (3, [(54, 24), (90, 24)]), (2, [(58, 32), (74, 47)])]
    sheet = Image.new("RGBA", (96 * 4, 48), (0, 0, 0, 0))
    for i, (lean, blade) in enumerate(poses):
        img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
        tilted = body.rotate(-lean * 2, resample=Image.NEAREST, center=(15, 47))
        img.paste(tilted, (33 + lean, 0), tilted)
        d = ImageDraw.Draw(img)
        if blade:
            (x0, y0), (x1, y1) = blade
            d.line([(x0, y0), (x1, y1)], fill=(*STEEL, 255), width=3)
            d.line([(x0, y0 - 1), (x1, y1 - 1)], fill=(*IVORY, 255), width=1)
            d.rectangle((x0 - 2, y0 - 2, x0 + 1, y0 + 1), fill=(*COPPER, 255))
        if i in (1, 2):  # ojos encendidos en anticipación y golpe
            d.rectangle((48 + lean, 9, 51 + lean, 10), fill=(0xFF, 0xD5, 0x9A, 255))
        sheet.paste(rim(img), (i * 96, 0))
    save(sheet, "Enemies/custodio.png")


if __name__ == "__main__":
    build()
    files = sorted(OUT.rglob("*.png"))
    print(f"{len(files)} sprites en {OUT}")
    if "--install" in sys.argv:
        for f in files:
            dest = ROOT / "Sprites" / f.relative_to(OUT)
            shutil.copy2(f, dest)
            print("instalado", dest.relative_to(ROOT))
