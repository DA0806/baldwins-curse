#!/usr/bin/env python3
"""Versiones de las capturas de la etapa 4 a 1280x720 y 1920x1080 y en grises.

El proyecto usa stretch "viewport" con escala entera: el juego se dibuja a
640x360 y la ventana lo amplía x2 o x3 por vecino más cercano. Esta ampliación
reproduce ese paso píxel a píxel. La comprobación en una pantalla real de
1920x1080 queda anotada como pendiente en docs/etapa4/README.md.

    python3 tools/stage4_sheets.py
"""
from pathlib import Path

from PIL import Image

DIR = Path(__file__).resolve().parent.parent / "docs/etapa4/capturas"

base = sorted(p for p in DIR.glob("0*.png") if p.stem.count("_") <= 2 and "_x" not in p.stem and "_gris" not in p.stem)
grays = []
for path in base:
    img = Image.open(path).convert("RGB")
    assert img.size == (640, 360), (path, img.size)
    for factor in (2, 3):
        img.resize((640 * factor, 360 * factor), Image.NEAREST).save(DIR / f"{path.stem}_x{factor}.png")
    gray = img.convert("L")
    gray.save(DIR / f"{path.stem}_gris.png")
    grays.append(gray)

sheet = Image.new("L", (640 * 2 + 8, (360 + 8) * ((len(grays) + 1) // 2)), 0)
for i, gray in enumerate(grays):
    sheet.paste(gray, ((i % 2) * 648, (i // 2) * 368))
sheet.save(DIR.parent / "hoja_grises.png")
print(f"{len(base)} capturas -> x2, x3 y grises; hoja en {DIR.parent / 'hoja_grises.png'}")
