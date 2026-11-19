#!/usr/bin/env python3
"""Render the five Meshy equipment GLBs and build separate equipment/HUD/world sprites.

blender -b --python tools/render_equipment_v2.py -- --render
python3 tools/render_equipment_v2.py --pack
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "Art/Meshy/animation_v2/equipment"
NAMES = ("sword", "mace", "scythe", "censer", "potion")


# Put each model into a reproducible side plane using its principal geometry axes.
def align_model(name, objects):
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector
    vertices = np.array([tuple(obj.matrix_world @ vertex.co) for obj in objects for vertex in obj.data.vertices])
    mean = vertices.mean(axis=0)
    _, vectors = np.linalg.eigh(np.cov((vertices - mean).T))
    major, second, depth = vectors[:, 2], vectors[:, 1], vectors[:, 0]
    coordinates = (vertices - mean) @ major
    transverse = (vertices - mean) @ second
    lo, hi = np.percentile(coordinates, [2, 98])
    low = np.abs(transverse[coordinates < lo + (hi - lo) * 0.12])
    high = np.abs(transverse[coordinates > hi - (hi - lo) * 0.12])
    low_size = np.percentile(low, 95) if len(low) else 0
    high_size = np.percentile(high, 95) if len(high) else 0
    horizontal = name in ("sword", "mace", "scythe")
    want_large_at_high = name in ("mace", "scythe")
    if (high_size > low_size) != want_large_at_high:
        major = -major
    rows = [major, depth, second] if horizontal else [second, depth, major]
    rotation = np.array(rows)
    if np.linalg.det(rotation) < 0:
        rotation[1] *= -1
    matrix = Matrix(rotation.tolist()).to_4x4() @ Matrix.Translation(-Vector(mean))
    for obj in objects:
        obj.matrix_world = matrix @ obj.matrix_world
    bpy.context.view_layer.update()
    if name == "scythe":
        pts = np.array([tuple(obj.matrix_world @ v.co) for obj in objects for v in obj.data.vertices])
        head = pts[pts[:, 0] > np.percentile(pts[:, 0], 80)]
        shaft = pts[pts[:, 0] < np.percentile(pts[:, 0], 35)]
        shaft_height = np.median(shaft[:, 2])
        if abs(head[:, 2].max() - shaft_height) > abs(head[:, 2].min() - shaft_height):
            flip = Matrix.Rotation(math.pi, 4, "X")
            for obj in objects:
                obj.matrix_world = flip @ obj.matrix_world
        # Keep the hook readable inside its fixed grip canvas without clipping it.
        shape = Matrix.Diagonal((1.0, 1.0, 0.78, 1.0))
        for obj in objects:
            obj.matrix_world = shape @ obj.matrix_world
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ v.co for obj in objects for v in obj.data.vertices]
    return [(min(v[i] for v in points), max(v[i] for v in points)) for i in range(3)]


# Render a neutral side view with enough margin for a clean alpha cutout.
def render(name):
    import bpy
    from mathutils import Vector
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ART / "models" / f"{name}.glb"))
    objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not objects:
        raise ValueError(f"No mesh in {name}")
    bounds = align_model(name, objects)
    for obj in objects:
        for poly in obj.data.polygons:
            poly.use_smooth = True
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Roughness"].default_value = 0.48 if name == "potion" else 0.72
                    if name == "potion":
                        bsdf.inputs["Coat Weight"].default_value = 0.30
    center = Vector([(a + b) / 2 for a, b in bounds])
    width, height = bounds[0][1] - bounds[0][0], bounds[2][1] - bounds[2][0]
    aspect = 3 if name in ("sword", "mace", "scythe") else 0.8
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_EEVEE_NEXT"
    scn.render.film_transparent = True
    scn.render.resolution_x = 1536 if aspect == 3 else 768
    scn.render.resolution_y = round(scn.render.resolution_x / aspect)
    scn.render.resolution_percentage = 100
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGBA"
    scn.view_settings.view_transform = "Standard"
    scn.view_settings.look = "Medium High Contrast"
    world = bpy.data.worlds.new("Cool abbey ambient")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.34, 0.43, 0.54, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.70
    scn.world = world
    span = max(width, height)
    bpy.ops.object.camera_add(location=center + Vector((0, -span * 4, 0)))
    camera = bpy.context.object
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(width, height * aspect) * 1.08
    scn.camera = camera
    for label, offset, energy, color in [
        ("Ivory key", (-1, -2, 3), 450, (1, 0.88, 0.72)),
        ("Steel rim", (1, 1, 2), 600, (0.52, 0.70, 1)),
        ("Fill", (2, -2, 1), 150, (0.70, 0.78, 0.90)),
    ]:
        bpy.ops.object.light_add(type="AREA", location=center + Vector(offset) * span)
        obj = bpy.context.object
        obj.name = label
        obj.data.energy = energy * span * span
        obj.data.shape, obj.data.size, obj.data.color = "DISK", span * 3, color
        obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()
    out = ART / "renders"
    out.mkdir(parents=True, exist_ok=True)
    scn.render.filepath = str(out / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    return {"bounds": bounds, "source": str((ART / "models" / f"{name}.glb").relative_to(ROOT))}


# Reduce once with premultiplied alpha and the established material ramps.
def resize(image, size):
    from PIL import Image
    from pack_prerendered import material_palette
    frame = image.convert("RGBa").resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    alpha = frame.getchannel("A").point(lambda a: 255 if a >= 100 else 0)
    palette, colors = material_palette()
    # The future healing liquid gets a restrained red ramp distinct from copper.
    red_stops = [(34,17,28),(65,26,38),(104,34,45),(145,48,58),(185,65,69),(219,104,90)]
    for first, second in zip(red_stops,red_stops[1:]):
        for step in range(5):
            color = tuple(round(a+(b-a)*step/4) for a,b in zip(first,second))
            if color not in colors:
                colors.append(color)
    palette.putpalette([channel for color in colors for channel in color] + list(colors[-1])*(256-len(colors)))
    rgb = frame.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE).convert("RGBA")
    rgb.putalpha(alpha)
    return rgb


# Fit the whole prop within a physical icon box without distorting proportions.
def fitted(image, canvas, content):
    from PIL import Image
    crop = image.crop(image.getchannel("A").getbbox())
    ratio = min(content[0] / crop.width, content[1] / crop.height)
    small = resize(crop, (max(1, round(crop.width * ratio)), max(1, round(crop.height * ratio))))
    result = Image.new("RGBA", canvas)
    result.alpha_composite(small, ((canvas[0] - small.width) // 2, (canvas[1] - small.height) // 2))
    return result


# Normalize equipment grip positions separately from inventory and pickup sizes.
def equipment(name, image):
    from PIL import Image
    crop = image.crop(image.getchannel("A").getbbox())
    if name in ("sword", "mace", "scythe"):
        canvas, grip, full_width = ((64, 32), (8, 16), 56) if name == "sword" else ((64, 32), (8, 16), 40) if name == "mace" else ((128, 64), (16, 32), 112)
        height = max(1, round(crop.height * full_width / crop.width))
        if height > canvas[1] - 4:
            full_width = round(full_width * (canvas[1] - 4) / height)
            height = canvas[1] - 4
        small = resize(crop, (full_width, height))
        # Grip center lies near the left end; PCA puts pommel on that end.
        grip_fraction = 0.13 if name == "sword" else 0.18 if name == "mace" else 0.12
        left = round(grip[0] - full_width * grip_fraction)
        if name == "scythe":
            # Locate the actual shaft, rather than treating the silhouette top as grip.
            alpha = small.getchannel("A")
            rows = [(y, sum(alpha.getpixel((x,y)) for x in range(0,max(1,full_width//3)))) for y in range(height)]
            shaft_y = max(rows,key=lambda item:item[1])[0]
            top = grip[1] - shaft_y
        else:
            top = grip[1] - height // 2
        result = Image.new("RGBA", canvas)
        result.alpha_composite(small, (left, top))
        return result, list(grip)
    if name == "censer":
        result = Image.new("RGBA", (48, 64))
        height = 52
        width = min(40, max(1, round(crop.width * height / crop.height)))
        small = resize(crop, (width, height))
        result.alpha_composite(small, ((48 - width) // 2, 6))
        return result, [24, 8]
    raise ValueError(name)


# Save RGBA sprites and record exact file hashes for downstream integration.
def save(image, rel, manifest):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    manifest[rel] = {"size": list(image.size), "bbox": list(image.getbbox()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


# Build equipment, HUD icons, world pickups, and a compact visual review sheet.
def pack():
    from PIL import Image, ImageDraw, ImageFont
    manifest = {}
    equipment_metadata = {}
    images = {name: Image.open(ART / "renders" / f"{name}.png").convert("RGBA") for name in NAMES}
    icon_images = {name: image.rotate(45, resample=Image.Resampling.BICUBIC, expand=True)
                   if name in ("sword", "mace") else image for name,image in images.items()}
    for name in ("sword", "mace", "scythe", "censer"):
        output, grip = equipment(name, images[name])
        rel = f"Sprites/Equipment/{name}.png"
        save(output, rel, manifest)
        equipment_metadata[name] = {"texture": rel, "grip": grip, "canvas": list(output.size)}
    for name, icon in [("sword", "Baldwin_Sword"), ("mace", "Crypt_Mace"), ("mace", "Test_Mace")]:
        output = fitted(icon_images[name], (64, 64), (48, 48))
        if icon == "Test_Mace":
            # Reuse geometry with a cooler test finish rather than charging a variant.
            pixels = output.load()
            for y in range(output.height):
                for x in range(output.width):
                    r, g, b, a = pixels[x, y]
                    pixels[x, y] = (round(r * 0.80), round(g * 0.93), min(255, round(b * 1.14)), a)
        save(output, f"Sprites/Items/Weapons/{icon}.png", manifest)
    save(fitted(images["potion"], (64, 64), (44, 48)), "Sprites/Items/Consumables/Healing_Potion.png", manifest)
    for name, canvas, content in [("sword", (32, 32), (30, 26)), ("mace", (28, 28), (26, 24)), ("potion", (16, 20), (14, 16))]:
        save(fitted(icon_images[name], canvas, content), f"Sprites/Items/World/{name}.png", manifest)
    for name in ("vow", "ember"):
        source = ROOT / f"Sprites/Items/Masks/Mask_{name.title()}.png"
        save(fitted(Image.open(source).convert("RGBA"), (20, 24), (16, 20)), f"Sprites/Items/World/mask_{name}.png", manifest)
    (ART / "sprite_manifest.json").write_text(json.dumps({"equipment": equipment_metadata, "files": manifest}, indent=2) + "\n")
    font = ImageFont.load_default(size=16)
    canvas = Image.new("RGB", (1300, 580), "#151924")
    draw = ImageDraw.Draw(canvas)
    for i, (rel, meta) in enumerate(manifest.items()):
        x, y = (i % 5) * 260, (i // 5) * 190
        image = Image.open(ROOT / rel).convert("RGBA")
        image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)
        canvas.paste(image, (x + 12, y + 35), image)
        draw.text((x + 8, y + 8), Path(rel).stem, font=font, fill="#E5D6B3")
    canvas.save(ART / "sprites_review.png")
    print(f"Packed {len(manifest)} equipment, icon and pickup files")


# Blender performs the 3D pass; regular Python can independently repack PNG assets.
def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--pack", action="store_true")
    parser.add_argument("--name", choices=NAMES)
    options = parser.parse_args(args)
    if options.render:
        result = {name: render(name) for name in ([options.name] if options.name else NAMES)}
        (ART / "render_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    if options.pack:
        pack()


if __name__ == "__main__":
    main()
