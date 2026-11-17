#!/usr/bin/env python3
"""Pack fixed-camera 4x RGBA renders without moving their anchors.

Default output is a review batch; only --install changes game sprites.
Requires Pillow. See docs/arte_prerenderizado.md for contracts and usage.
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parent.parent
BASE = Path('Art/Meshy/prerendered')
SHEETS = [
    *(('baldwin', name, 128, 128, count, f'Characters/Baldwin/{name}.png')
      for name, count in [('Idle', 4), ('Walk', 8), ('Jump', 6), ('Attack', 5), ('Dead', 6), ('Hurt', 2)]),
    ('custodio', 'poses', 96, 48, 4, 'Enemies/custodio.png'),
    ('custodio_sellado', 'poses', 96, 48, 4, 'Enemies/custodio_sellado.png'),
    ('acolito', 'poses', 64, 48, 4, 'Enemies/acolito.png'),
    ('abad', 'poses', 224, 128, 9, 'Bosses/abad.png'),
]


# Build short material ramps from the art guide without introducing dithering.
def material_palette():
    ramps = [
        ['#151924', '#232B37', '#303B4A', '#3E4B5E', '#6D8297', '#A99C80', '#E5D6B3'],
        ['#151924', '#3A2A22', '#7A3A22', '#B96A47', '#F0A758', '#FFD59A', '#E5D6B3'],
        ['#232B37', '#5F5D58', '#A99C80', '#E5D6B3'],
    ]
    colors = []
    for ramp in ramps:
        stops = [tuple(bytes.fromhex(color[1:])) for color in ramp]
        for first, second in zip(stops, stops[1:]):
            for step in range(12):
                color = tuple(round(a + (b - a) * step / 11) for a, b in zip(first, second))
                if color not in colors:
                    colors.append(color)
    palette = Image.new('P', (1, 1))
    palette.putpalette([channel for color in colors for channel in color] + list(colors[-1]) * (256 - len(colors)))
    return palette, colors


# Treat substantial edge coverage as clipping, allowing only contracted floor edges.
def validate_image(image, size, allow_floor, threshold, label):
    if image.mode != 'RGBA':
        raise ValueError(f'{label}: expected RGBA, received {image.mode}')
    if image.size != size:
        raise ValueError(f'{label}: expected {size}, received {image.size}')
    mask = image.getchannel('A').point(lambda value: 255 if value >= threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        raise ValueError(f'{label}: empty frame at alpha threshold {threshold}')
    left, top, right, bottom = bbox
    if left == 0 or top == 0 or right == size[0] or (bottom == size[1] and not allow_floor):
        raise ValueError(f'{label}: clipped silhouette at canvas edge, bbox={bbox}')
    return list(bbox)


# Resize once in premultiplied alpha, then choose palette colors and hard alpha.
def finish_frame(image, size, palette, threshold):
    frame = image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
    alpha = frame.getchannel('A').point(lambda value: 255 if value >= threshold else 0)
    rgb = frame.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE).convert('RGB')
    result = Image.new('RGBA', size)
    rgb.putalpha(alpha)
    result.paste(rgb, (0, 0), alpha)
    return result


# Hash files so the manifest identifies exactly which inputs and outputs were used.
def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Preserve alpha while removing color for readability comparisons.
def grayscale(image):
    result = ImageOps.grayscale(image.convert('RGB')).convert('RGBA')
    result.putalpha(image.getchannel('A'))
    return result


# Draw dark checkerboard panels with nearest-neighbor scaling only for review.
def gallery(rows, path):
    width = max(640, max(sum(image.width + 12 for image in images) + 16 for _, images in rows))
    height = sum(max(image.height for image in images) + 32 for _, images in rows) + 8
    canvas = Image.new('RGB', (width, height), '#10141d')
    draw = ImageDraw.Draw(canvas)
    y = 8
    for label, images in rows:
        draw.text((8, y), label, fill='#E5D6B3')
        y += 20
        x = 8
        for sprite in images:
            for cy in range(0, sprite.height, 16):
                for cx in range(0, sprite.width, 16):
                    color = '#1C2230' if (cx // 16 + cy // 16) % 2 else '#151924'
                    draw.rectangle((x + cx, y + cy, x + min(cx + 15, sprite.width - 1),
                                    y + min(cy + 15, sprite.height - 1)), fill=color)
            canvas.paste(sprite, (x, y), sprite)
            x += sprite.width + 12
        y += max(image.height for image in images) + 12
    canvas.save(path)


# Validate the full batch before creating any output or touching installed sprites.
def pack(frames_dir, output_dir, project_root, install=False, alpha_threshold=110):
    if not 1 <= alpha_threshold <= 255:
        raise ValueError('alpha threshold must be between 1 and 255')
    if (project_root / 'Sprites').resolve() in [output_dir.resolve(), *output_dir.resolve().parents]:
        raise ValueError('output directory cannot be inside Sprites; use --install explicitly')
    palette, colors = material_palette()
    batch = []
    for actor, action, width, height, count, destination in SHEETS:
        folder = frames_dir / actor / action
        paths = [folder / f'{frame:03}.png' for frame in range(count)]
        actual = sorted(folder.glob('*.png'))
        if actual != paths:
            raise ValueError(f'{folder}: expected exactly 000.png through {count - 1:03}.png; found {len(actual)} PNG files')
        frames, inputs, bboxes = [], [], []
        allow_floor = actor != 'abad'
        for source in paths:
            with Image.open(source) as image:
                validate_image(image, (width * 4, height * 4), allow_floor, alpha_threshold, source)
                frame = finish_frame(image, (width, height), palette, alpha_threshold)
            bboxes.append(validate_image(frame, (width, height), allow_floor, alpha_threshold, source))
            frames.append(frame)
            inputs.append({'file': str(source), 'sha256': sha256(source)})
        original = project_root / BASE / 'before' / destination
        if not original.exists():
            original = project_root / 'Sprites' / destination
        with Image.open(original) as image:
            if image.size != (width * count, height):
                raise ValueError(f'{original}: original sheet has unexpected dimensions {image.size}')
            before = image.convert('RGBA')
        batch.append((actor, action, width, height, destination, frames, before, inputs, bboxes))

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {'source_scale': 4, 'resize': 'LANCZOS in premultiplied RGBa; one resize; no recenter',
                'alpha_threshold': alpha_threshold, 'alpha_output': '0 or 255',
                'palette_rgb': colors, 'dither': 'NONE', 'installed': install, 'sheets': []}
    gallery_rows, comparison_rows = [], []
    for actor, action, width, height, destination, frames, before, inputs, bboxes in batch:
        target = output_dir / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        sheet = Image.new('RGBA', (width * len(frames), height))
        for index, frame in enumerate(frames):
            sheet.paste(frame, (index * width, 0))
        sheet.save(target)
        manifest['sheets'].append({'file': destination, 'size': list(sheet.size), 'frames': len(frames),
                                   'frame_bboxes': bboxes, 'sha256': sha256(target), 'inputs': inputs})
        for scale, gray in [(1, False), (3, False), (3, True)]:
            columns = max(1, 2048 // (width * scale + 12))
            for start in range(0, len(frames), columns):
                images = [(grayscale(frame) if gray else frame).resize((width * scale, height * scale), Image.Resampling.NEAREST)
                          for frame in frames[start:start + columns]]
                label = f'{actor}/{action} | {scale}x {"grayscale" if gray else "color"} | frames {start}-{start + len(images) - 1}'
                gallery_rows.append((label, images))
        selected = [0]
        if action == 'Attack':
            selected += [4]
        elif action == 'poses':
            selected += [1, 2] if actor != 'abad' else [1, 2, 4, 6, 8]
        for index in selected:
            old = before.crop((index * width, 0, (index + 1) * width, height))
            images = [old, frames[index], grayscale(frames[index])]
            comparison_rows.append((f'{actor}/{action} frame {index} | BEFORE / AFTER / AFTER GRAYSCALE (3x)',
                                    [image.resize((width * 3, height * 3), Image.Resampling.NEAREST) for image in images]))
    gallery(gallery_rows, output_dir.parent / 'gallery.png')
    gallery(comparison_rows, output_dir.parent / 'comparison.png')

    if install:
        for _, _, _, _, destination, _, _, _, _ in batch:
            target = project_root / 'Sprites' / destination
            backup = project_root / BASE / 'before' / destination
            if not backup.exists():
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
            shutil.copy2(output_dir / destination, target)
    (output_dir.parent / 'pack_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


# Keep review generation as the default and report validation failures without a traceback.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=ROOT)
    parser.add_argument('--frames-dir', type=Path, help='Defaults to <project-root>/Art/Meshy/prerendered/frames')
    parser.add_argument('--output-dir', type=Path, help='Defaults to <project-root>/Art/Meshy/prerendered/sprites')
    parser.add_argument('--alpha-threshold', type=int, default=110)
    parser.add_argument('--install', action='store_true', help='Back up original sheets once, then replace installed Sprites')
    args = parser.parse_args()
    try:
        manifest = pack(args.frames_dir or args.project_root / BASE / 'frames',
                        args.output_dir or args.project_root / BASE / 'sprites',
                        args.project_root, args.install, args.alpha_threshold)
    except (ValueError, OSError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    print(f'Packed {len(manifest["sheets"])} sheets; installed={args.install}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
