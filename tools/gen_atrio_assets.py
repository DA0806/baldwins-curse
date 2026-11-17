#!/usr/bin/env python3
"""Genera el arte y el audio propios de la sala de referencia (etapa 4).

Todo sale de código: no usa archivos de terceros. Volver a ejecutarlo
reproduce los mismos archivos (semillas fijas).

    python3 tools/gen_atrio_assets.py

Requiere Pillow y numpy. Paleta: docs/arte.md.
"""
import math
import random
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / "Sprites/Environment/Atrio"
ENEMY = ROOT / "Sprites/Enemies"
AUDIO = ROOT / "Audio"

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


def rgba(c, a=255):
    return (c[0], c[1], c[2], a)


def new(w, h, fill=None):
    return Image.new("RGBA", (w, h), rgba(fill) if fill else (0, 0, 0, 0))


def rect(d, x0, y0, x1, y1, c):
    """Rectángulo con extremos incluidos."""
    d.rectangle((x0, y0, x1, y1), fill=rgba(c) if len(c) == 3 else c)


def speckle(img, color, count, seed, area=None):
    rnd = random.Random(seed)
    w, h = img.size
    x0, y0, x1, y1 = area or (0, 0, w - 1, h - 1)
    for _ in range(count):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        if img.getpixel((x, y))[3] > 0:
            img.putpixel((x, y), rgba(color))


def pointed_arch(img, cx, spring_y, half_w, thickness, color, fill_inside=None):
    """Arco apuntado: dos arcos de radio 2*half_w centrados en los arranques opuestos."""
    r_out = 2.0 * half_w
    r_in = r_out - thickness
    apex = spring_y - half_w * math.sqrt(3.0)
    w, h = img.size
    for y in range(max(0, int(apex) - 1), min(h, spring_y + 1)):
        for x in range(max(0, cx - half_w), min(w, cx + half_w)):
            # Mitad izquierda: centro en el arranque derecho, y al revés.
            center_x = cx + half_w if x < cx else cx - half_w
            dist = math.hypot(x + 0.5 - center_x, y + 0.5 - spring_y)
            if r_in <= dist <= r_out:
                img.putpixel((x, y), rgba(color))
            elif fill_inside and dist < r_in:
                img.putpixel((x, y), fill_inside if len(fill_inside) == 4 else rgba(fill_inside))


# ------------------------------------------------------------------ tiles 16 px

def bricks(img, base, brick, mortar, y_offset, seed):
    d = ImageDraw.Draw(img)
    w, h = img.size
    rect(d, 0, y_offset, w - 1, h - 1, base)
    for row, y in enumerate(range(y_offset, h, 8)):
        rect(d, 0, y, w - 1, min(h - 1, y + 6), brick)
        rect(d, 0, min(h - 1, y + 7), w - 1, min(h - 1, y + 7), mortar)
        joint = 0 if row % 2 == 0 else 8
        rect(d, joint, y, joint, min(h - 1, y + 6), mortar)
    speckle(img, base, 6, seed, (0, y_offset, w - 1, h - 1))


def make_tiles():
    top = new(16, 16)
    bricks(top, STONE_D, STONE, STONE_D, 2, 1)
    d = ImageDraw.Draw(top)
    rect(d, 0, 0, 15, 0, IVORY_D)  # borde gastado: la superficie pisable se lee
    rect(d, 0, 1, 15, 1, STEEL)
    speckle(top, STONE_L, 4, 2, (0, 3, 15, 15))
    top.save(ENV / "floor_top.png")

    fill = new(16, 16)
    bricks(fill, BG, STONE_D, BG, 0, 3)
    speckle(fill, STONE, 3, 4)
    fill.save(ENV / "floor_fill.png")


# ------------------------------------------------------------------ fondo por planos

def make_background():
    far = new(640, 360)
    d = ImageDraw.Draw(far)
    for y in range(360):  # cielo nocturno: un poco más claro hacia el horizonte
        t = y / 359.0
        c = tuple(int(BG[i] * (1 - t * 0.3) + BG_FAR[i] * t * 0.3 + 2 * t) for i in range(3))
        rect(d, 0, y, 639, y, c)
    # Masa de la abadía al fondo, periodo 160 px (encaja en 640).
    for base_x in range(0, 640, 160):
        rect(d, base_x + 20, 150, base_x + 140, 359, BG_FAR)
        pointed_arch(far, base_x + 80, 150, 60, 60, BG_FAR, fill_inside=BG_FAR)  # remate apuntado
        rect(d, base_x + 76, 40, base_x + 84, 70, BG_FAR)  # aguja
        for wx in (base_x + 52, base_x + 108):  # ventanas con brasa tenue
            pointed_arch(far, wx, 200, 7, 7, (0x3A, 0x2A, 0x22), fill_inside=(0x3A, 0x2A, 0x22))
            rect(d, wx - 7, 200, wx + 6, 228, (0x3A, 0x2A, 0x22))
    far.save(ENV / "bg_far.png")

    mid = new(640, 360)
    d = ImageDraw.Draw(mid)
    for base_x in range(0, 640, 128):  # columnata, periodo 128 px
        col = base_x + 10
        pointed_arch(mid, base_x + 64, 110, 54, 8, STONE_D)
        rect(d, col - 2, 100, col + 21, 108, STONE_D)  # capitel
        rect(d, col, 108, col + 19, 359, STONE_D)
        rect(d, col, 108, col + 2, 359, (0x2B, 0x34, 0x42))  # canto iluminado
        rect(d, col + 17, 108, col + 19, 359, (0x1D, 0x24, 0x2F))
    mid.save(ENV / "bg_mid.png")


# ------------------------------------------------------------------ utilería

def make_props():
    # Candelabro 16x32
    img = new(16, 32)
    d = ImageDraw.Draw(img)
    rect(d, 7, 10, 8, 30, STEEL)
    rect(d, 4, 29, 11, 31, STEEL)
    rect(d, 2, 10, 13, 11, STEEL)
    for x in (2, 7, 12):
        rect(d, x, 5, x + 1, 9, IVORY)
        rect(d, x, 2, x + 1, 4, EMBER)
        img.putpixel((x, 1), rgba(EMBER_L))
    img.save(ENV / "candelabra.png")

    # Urna funeraria 16x16
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    d.ellipse((3, 4, 12, 15), fill=rgba(COPPER))
    rect(d, 5, 1, 10, 4, COPPER_D)
    rect(d, 4, 0, 11, 1, COPPER)
    rect(d, 4, 9, 11, 9, COPPER_D)
    img.putpixel((5, 7), rgba(EMBER))
    img.save(ENV / "urn.png")

    # Lápida 32x16
    img = new(32, 16)
    d = ImageDraw.Draw(img)
    rect(d, 2, 2, 29, 15, STONE)
    rect(d, 2, 2, 29, 3, STONE_L)
    rect(d, 15, 5, 16, 13, IVORY_D)
    rect(d, 11, 7, 20, 8, IVORY_D)
    img.save(ENV / "tomb.png")

    # Estandarte que señala la salida 16x48: tela de cobre con chevrón marfil.
    img = new(16, 48)
    d = ImageDraw.Draw(img)
    rect(d, 0, 0, 15, 1, STEEL)
    d.polygon([(2, 2), (13, 2), (13, 40), (7, 46), (2, 40)], fill=rgba(COPPER))
    d.polygon([(4, 14), (9, 20), (4, 26), (4, 23), (6, 20), (4, 17)], fill=rgba(IVORY))
    d.polygon([(7, 14), (12, 20), (7, 26), (7, 23), (9, 20), (7, 17)], fill=rgba(IVORY))
    img.save(ENV / "banner.png")

    # Pedestal 32x16 bajo los objetos
    img = new(32, 16)
    d = ImageDraw.Draw(img)
    rect(d, 1, 0, 30, 3, IVORY)
    rect(d, 4, 4, 27, 15, STONE_L)
    rect(d, 4, 4, 27, 5, STEEL)
    rect(d, 2, 13, 29, 15, STONE)
    img.save(ENV / "pedestal.png")

    # Púas del foso 16x16: forma de peligro que se lee sin color.
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    for x in (0, 8):
        d.polygon([(x, 15), (x + 3, 0), (x + 7, 15)], fill=rgba(STEEL))
        d.line([(x + 3, 1), (x + 1, 14)], fill=rgba(IVORY))
        d.polygon([(x + 2, 4), (x + 3, 0), (x + 5, 4)], fill=rgba(EMBER))
    rect(d, 0, 14, 15, 15, STONE_D)
    img.save(ENV / "spikes.png")

    # Resplandor del foso 96x104: brasa que sube desde el fondo.
    img = new(96, 104)
    for y in range(104):
        a = int(150 * (y / 103.0) ** 2.2)
        for x in range(96):
            img.putpixel((x, y), (COPPER[0], COPPER[1], COPPER[2], a))
    img.save(ENV / "pit_glow.png")

    # Arco de salida 48x96 con interior encendido y chevrón.
    img = new(48, 96)
    d = ImageDraw.Draw(img)
    for y in range(28, 96):  # interior: brasa más intensa abajo
        a = int(40 + 120 * ((y - 28) / 67.0))
        rect(d, 8, y, 39, y, (EMBER[0], EMBER[1], EMBER[2], a))
    pointed_arch(img, 24, 40, 16, 7, STONE_L, fill_inside=(EMBER[0], EMBER[1], EMBER[2], 45))
    rect(d, 0, 40, 7, 95, STONE_L)
    rect(d, 40, 40, 47, 95, STONE_L)
    rect(d, 0, 40, 1, 95, STEEL)
    rect(d, 46, 40, 47, 95, STONE)
    rect(d, 21, 11, 26, 16, IVORY)  # clave del arco
    for dx in (0, 7):
        d.polygon([(17 + dx, 54), (25 + dx, 62), (17 + dx, 70), (17 + dx, 66), (21 + dx, 62), (17 + dx, 58)], fill=rgba(IVORY))
    img.save(ENV / "arch_exit.png")

    # Brasero del punto de control: 4 cuadros de 32x32 (apagado + 3 de llama).
    sheet = new(128, 32)
    for frame in range(4):
        img = new(32, 32)
        d = ImageDraw.Draw(img)
        rect(d, 14, 18, 17, 30, STEEL)
        rect(d, 10, 29, 21, 31, STEEL)
        d.polygon([(7, 13), (24, 13), (21, 19), (10, 19)], fill=rgba(COPPER))
        rect(d, 7, 13, 24, 13, IVORY_D)
        if frame == 0:
            rect(d, 11, 11, 20, 12, STONE_L)  # ceniza
        else:
            sway = (-1, 1, 0)[frame - 1]
            tip = (2, 4, 1)[frame - 1]
            d.polygon([(8, 12), (23, 12), (17 + sway, tip + 4), (16 + sway, tip)], fill=rgba(EMBER))
            d.polygon([(11, 12), (20, 12), (16 + sway, tip + 6)], fill=rgba(EMBER_L))
            rect(d, 14, 10, 17, 12, IVORY)
        sheet.paste(img, (frame * 32, 0))
    sheet.save(ENV / "brazier.png")


# ------------------------------------------------------------------ enemigo

def make_enemy():
    """Custodio encapuchado, 4 poses de 96x48 mirando a la derecha.
    Origen en el centro del cuadro (48, 24); pies en y=47. La hoja del golpe
    (cuadro 2) ocupa x 54..90 = la zona de golpe real (cerca 6, alcance 42)."""
    poses = [
        dict(lean=0, drop=0, eyes=COPPER_D, blade=[(54, 30), (66, 44)]),
        dict(lean=-2, drop=0, eyes=EMBER_L, blade=[(44, 15), (44, 0)]),
        dict(lean=3, drop=0, eyes=EMBER_L, blade=[(54, 24), (90, 24)], trail=True),
        dict(lean=2, drop=3, eyes=COPPER_D, blade=[(58, 32), (74, 47)]),
    ]
    sheet = new(96 * 4, 48)
    for i, pose in enumerate(poses):
        img = new(96, 48)
        d = ImageDraw.Draw(img)
        lean, drop = pose["lean"], pose["drop"]
        if pose.get("trail"):
            for k in range(6):  # estela del tajo: arco marfil tenue
                a = 50 + k * 20
                y = 6 + k * 3
                d.line([(58 + k * 4, y), (90, 24)], fill=(IVORY[0], IVORY[1], IVORY[2], a))
        # Túnica (trapecio) con pliegues
        d.polygon([(41 + lean, 18 + drop), (55 + lean, 18 + drop), (59, 47), (37, 47)], fill=rgba(STONE))
        d.line([(45 + lean, 22 + drop), (43, 46)], fill=rgba(STONE_D))
        d.line([(51 + lean, 22 + drop), (53, 46)], fill=rgba(STEEL))
        d.line([(42 + lean, 26 + drop), (56 + lean, 32 + drop)], fill=rgba(COPPER), width=2)
        # Capucha y rostro vacío
        d.ellipse((40 + lean, 3 + drop, 56 + lean, 22 + drop), fill=rgba(STONE_L))
        d.ellipse((44 + lean, 8 + drop, 54 + lean, 19 + drop), fill=rgba(BG))
        for ex in (48, 51):
            rect(d, ex + lean, 12 + drop, ex + lean + 1, 13 + drop, pose["eyes"])
        # Hoja: acero con filo marfil y empuñadura de cobre
        (x0, y0), (x1, y1) = pose["blade"]
        d.line([(x0, y0), (x1, y1)], fill=rgba(STEEL), width=3)
        d.line([(x0, y0 - 1), (x1, y1 - 1)], fill=rgba(IVORY), width=1)
        rect(d, x0 - 2, y0 - 2, x0 + 1, y0 + 1, COPPER)
        if i == 1:  # destello en la punta: la anticipación se ve también en gris
            for dx, dy in ((0, -1), (-2, 1), (2, 1)):
                img.putpixel((44 + dx, 1 + dy), rgba(IVORY))
        rim_light(img, STEEL)
        sheet.paste(img, (i * 96, 0))
    sheet.save(ENEMY / "custodio.png")


def rim_light(img, color):
    """Contorno claro de 1 px por arriba y a los lados: separa la silueta del
    fondo oscuro también en escala de grises."""
    w, h = img.size
    src = img.copy()
    for y in range(h):
        for x in range(w):
            if src.getpixel((x, y))[3] == 0:
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src.getpixel((nx, ny))[3] == 0 and img.getpixel((nx, ny))[3] == 0:
                    img.putpixel((nx, ny), rgba(color, 200))


# ------------------------------------------------------------------ audio

RATE = 44100


def write_wav(path, samples):
    data = np.clip(samples, -1.0, 1.0)
    pcm = (data * 32767 * 0.9).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())


def lowpass(x, cutoff):
    """Filtro de un polo; cutoff puede variar por muestra."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = 1.0 - np.exp(-2.0 * np.pi * cutoff / RATE)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def make_audio():
    rng = np.random.default_rng(7)
    t = lambda dur: np.arange(int(dur * RATE)) / RATE

    # Ambiente del Atrio: 8 s en bucle (todas las frecuencias cierran ciclo en 8 s).
    tt = t(8.0)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * tt)
    drone = 0.22 * np.sin(2 * np.pi * 55 * tt) + 0.12 * np.sin(2 * np.pi * 82.5 * tt) * lfo
    wind = lowpass(rng.standard_normal(len(tt)), 300.0)
    wind = wind / np.max(np.abs(wind)) * (0.10 + 0.08 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.125 * tt)))
    fade = np.minimum(1.0, np.minimum(tt, 8.0 - tt) / 0.05)  # sin chasquido en la costura
    bell = np.zeros_like(tt)
    start = int(2.0 * RATE)
    bt = tt[: int(3.0 * RATE)]
    for freq, amp in ((392, 0.10), (987, 0.04), (1568, 0.02)):
        bell[start:start + len(bt)] += amp * np.sin(2 * np.pi * freq * bt) * np.exp(-bt * 1.6)
    write_wav(AUDIO / "amb_atrio.wav", (drone + wind + bell) * fade)

    # Ataque: soplido de ruido con corte descendente.
    tt = t(0.2)
    env = np.sin(np.pi * tt / 0.2) ** 2
    write_wav(AUDIO / "sfx_attack.wav", lowpass(rng.standard_normal(len(tt)), 3000 - 12000 * tt) * env * 1.6)

    # Impacto: golpe grave descendente con chasquido.
    tt = t(0.16)
    freq = 110 - 260 * tt
    thump = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-tt * 28)
    click = rng.standard_normal(len(tt)) * np.exp(-tt * 140) * 0.5
    write_wav(AUDIO / "sfx_hit.wav", thump + click)

    # Recogida: dos notas.
    tt = t(0.4)
    note = lambda f, start: np.where(tt >= start, np.sin(2 * np.pi * f * (tt - start)) * np.exp(-(tt - start) * 9), 0.0)
    write_wav(AUDIO / "sfx_pickup.wav", 0.5 * note(660, 0.0) + 0.5 * note(990, 0.08))

    # Cambio de máscara: barrido vítreo con quinta.
    tt = t(0.32)
    sweep = 400 + 900 * tt
    phase = 2 * np.pi * np.cumsum(sweep) / RATE
    env = np.exp(-tt * 7) * np.minimum(1.0, tt / 0.01)
    write_wav(AUDIO / "sfx_mask.wav", (0.4 * np.sin(phase) + 0.25 * np.sin(1.5 * phase)) * env)


if __name__ == "__main__":
    for folder in (ENV, ENEMY, AUDIO):
        folder.mkdir(parents=True, exist_ok=True)
    make_tiles()
    make_background()
    make_props()
    make_enemy()
    make_audio()
    print("ok:", ENV, ENEMY, AUDIO)
