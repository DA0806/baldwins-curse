#!/usr/bin/env python3
"""Render Meshy humanoid rigs into the game's fixed sprite cells with Blender.

blender -b --python tools/render_characters.py -- --actor baldwin
The packer reduces the 4x RGBA frames once; this renderer never crops a pose.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "Art/Meshy/prerendered"
RIGHT = Vector((0.4472136, -0.8944272, 0))
TOWARD = Vector((-0.8944272, -0.4472136, 0))
UP = Vector((0, 0, 1))
CONFIG = {
    "baldwin": (128, 128, 32, 127, 64, 1.75),
    "custodio": (96, 48, 48, 47, 44, 1.75),
    "custodio_sellado": (96, 48, 48, 47, 44, 1.75),
    "acolito": (64, 48, 32, 47, 41, 1.75),
    "abad": (224, 128, 112, 120, 108, 2.0),
}


# Creates a readable matte material; luminous signals are rendered without bloom.
def material(name, color, metallic=0.0, glow=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1)
    node.inputs["Roughness"].default_value = 0.68
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Emission Color"].default_value = (*color, 1)
    node.inputs["Emission Strength"].default_value = glow
    return mat


# Uses camera coordinates so weapons land inside the existing damage rectangles.
def screen(x, z, depth=0.0):
    return RIGHT * x + UP * z + TOWARD * depth


# Places a beveled cuboid between two points, retaining specular metal edges.
def bar(name, start, end, width, thickness, mat):
    start, end = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(start + end) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (end - start).to_track_quat("Z", "Y").to_euler()
    obj.scale = (width, thickness, (end - start).length)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Soft forged edge", "BEVEL")
    bevel.width, bevel.segments = min(width, thickness) * 0.22, 2
    return obj


# Builds an original straight medieval sword in the camera plane.
def sword(grip, angle, length, mats):
    direction = RIGHT * math.cos(angle) + UP * math.sin(angle)
    across = RIGHT * -math.sin(angle) + UP * math.cos(angle)
    grip = Vector(grip) + TOWARD * 0.055
    guard = grip + direction * 0.12
    bar("Leather grip", grip - direction * 0.1, guard, 0.055, 0.055, mats["leather"])
    bar("Copper crossguard", guard - across * 0.13, guard + across * 0.13, 0.045, 0.06, mats["copper"])
    points = [guard - across * 0.055, guard + across * 0.055,
              guard + direction * (length - 0.13) + across * 0.035,
              guard + direction * length,
              guard + direction * (length - 0.13) - across * 0.035]
    mesh = bpy.data.meshes.new("Forged blade")
    mesh.from_pydata([tuple(p) for p in points], [], [(0, 1, 2, 3, 4)])
    obj = bpy.data.objects.new("Sword blade", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mats["steel"])
    solid = obj.modifiers.new("Blade thickness", "SOLIDIFY")
    solid.thickness = 0.035
    bar("Ivory bevel", guard + TOWARD * 0.022, guard + direction * length + TOWARD * 0.022,
        0.018, 0.018, mats["ivory"])


# Makes the scythe readable as a shaft and a curved blade rather than a line.
def scythe(grip, angle, length, mats, low_sweep=False):
    direction = RIGHT * math.cos(angle) + UP * math.sin(angle)
    across = RIGHT * -math.sin(angle) + UP * math.cos(angle)
    if low_sweep:
        across = -across
    hook = 0.30 if low_sweep else 0.72
    grip = Vector(grip) + TOWARD * 0.10
    tip = grip + direction * length
    bar("Ashwood scythe shaft", grip - direction * 0.25, tip, 0.07, 0.07, mats["leather"])
    points = [tip - direction * 0.10, tip + direction * 0.08,
              tip + direction * 0.20 + across * hook * 0.22,
              tip + direction * 0.18 + across * hook * 0.62,
              tip - direction * 0.03 + across * hook,
              tip + direction * 0.04 + across * hook * 0.55,
              tip - direction * 0.12 + across * hook * 0.22]
    mesh = bpy.data.meshes.new("Crescent scythe blade")
    mesh.from_pydata([tuple(p) for p in points], [], [tuple(range(7))])
    obj = bpy.data.objects.new("Scythe", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mats["steel"])
    obj.modifiers.new("Blade thickness", "SOLIDIFY").thickness = 0.04


# Suspends an actual modeled censer from the raised hand.
def censer(hand, mats, lit=False):
    hand = Vector(hand) + TOWARD * 0.10
    bowl = hand - UP * 0.28
    for side in (-1, 1):
        bar("Censer chain", hand, bowl + RIGHT * side * 0.09, 0.018, 0.018, mats["copper"])
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=bowl)
    obj = bpy.context.object
    obj.name = "Copper censer"
    obj.scale = (0.13, 0.13, 0.10)
    obj.data.materials.append(mats["copper"])
    if lit:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.07, location=bowl + UP * 0.04 + TOWARD * 0.10)
        bpy.context.object.data.materials.append(mats["ember"])


# Adds distinct geometry and state signals to the sealed variants.
def seal(center, radius, mats, active=False, sealed=False):
    center = Vector(center) + TOWARD * 0.16
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=radius * 0.16,
                                   major_segments=24, minor_segments=6, location=center)
    obj = bpy.context.object
    obj.rotation_euler = TOWARD.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mats["ember"] if active else mats["copper"])
    for sign in (-1, 1):
        bar("Seal binding", center + RIGHT * sign * radius - UP * radius,
            center - RIGHT * sign * radius + UP * radius, radius * 0.20, 0.025,
            mats["ivory"] if active else mats["copper"])
    if sealed:
        bar("Ceremonial left binding", center + RIGHT * -0.17 + UP * 0.22,
            center + RIGHT * -0.26 - UP * 0.48, 0.075, 0.035, mats["ivory"])
        bar("Ceremonial right binding", center + RIGHT * 0.17 + UP * 0.22,
            center + RIGHT * 0.26 - UP * 0.48, 0.075, 0.035, mats["ivory"])


# Configures an orthographic, level camera for the exact existing cell pivot.
def setup_scene(actor):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_EEVEE_NEXT"
    scn.render.film_transparent = True
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGBA"
    scn.render.resolution_percentage = 100
    scn.view_settings.view_transform = "Standard"
    scn.view_settings.look = "Medium High Contrast"
    w, h, px, py, body_px, height = CONFIG[actor]
    ppu = body_px / height
    scn.render.resolution_x, scn.render.resolution_y = w * 4, h * 4
    world = bpy.data.worlds.new("Cool abbey ambient")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.36, 0.43, 0.55, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
    scn.world = world
    target = screen((w / 2 - px) / ppu, (py - h / 2 + 0.5) / ppu)
    bpy.ops.object.camera_add(location=target + TOWARD * 8)
    cam = bpy.context.object
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.type, cam.data.ortho_scale = "ORTHO", w / ppu
    scn.camera = cam
    for name, loc, energy, color, size in [
        ("Ivory key", (-3, -4, 5), 550, (1.0, 0.90, 0.74), 4),
        ("Steel rim", (3, 1, 3), 650, (0.50, 0.68, 1.0), 3),
        ("Camera fill", (-4, -2, 1.5), 100, (0.65, 0.74, 0.92), 4),
    ]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.name, light.data.energy, light.data.color, light.data.shape, light.data.size = name, energy, color, "DISK", size
        light.rotation_euler = (Vector((0, 0, 1)) - light.location).to_track_quat("-Z", "Y").to_euler()
    return ppu


# Imports only the weighted character and retains Meshy's original bind matrices.
def load_character(actor, source=None):
    source_actor = "custodio" if actor == "custodio_sellado" else actor
    source = source or ART / "rigs" / source_actor / "rigged_character.glb"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = set(bpy.data.objects) - before
    rig = next(o for o in imported if o.type == "ARMATURE")
    for obj in list(imported):
        if obj.type == "MESH" and not obj.vertex_groups:
            imported.remove(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for bone in rig.data.edit_bones:
        bone.length /= 100  # Meshy GLB display tails are 100x the joint spacing.
    bpy.ops.object.mode_set(mode="OBJECT")
    for obj in imported:
        if obj.name not in bpy.data.objects or obj.type != "MESH":
            continue
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Roughness"].default_value = 0.85
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return rig


# Moves a joint with a two-bone IK chain; targets are actual world positions.
def hand_target(rig, side, point):
    bpy.ops.object.empty_add(location=point)
    target = bpy.context.object
    target.name = side + " wrist target"
    constraint = rig.pose.bones[side + "ForeArm"].constraints.new("IK")
    constraint.target, constraint.chain_count = target, 2
    constraint.use_tail = True


# Rotates a joint about the camera depth axis without assuming bone-local axes.
def bend(rig, name, degrees):
    bone = rig.pose.bones[name]
    axis = rig.matrix_world.to_quaternion().inverted() @ TOWARD
    transform = bone.matrix.copy()
    rotation = Quaternion(axis, -math.radians(degrees)).to_matrix() @ transform.to_3x3()
    bone.matrix = Matrix.LocRotScale(transform.translation, rotation.to_quaternion(), transform.to_scale())
    bpy.context.view_layer.update()


# Sets a global hip displacement in the armature's coordinates.
def lower_hips(rig, amount):
    for side in ("Right", "Left"):
        leg = rig.pose.bones[side + "Leg"]
        if not leg.constraints:
            foot = rig.matrix_world @ rig.pose.bones[side + "Foot"].head
            bpy.ops.object.empty_add(location=foot)
            constraint = leg.constraints.new("IK")
            constraint.target, constraint.chain_count = bpy.context.object, 2
    bone = rig.pose.bones["Hips"]
    delta = rig.matrix_world.inverted().to_3x3() @ Vector((0, 0, -amount))
    bone.matrix = Matrix.Translation(delta) @ bone.matrix
    bpy.context.view_layer.update()


# Renders one pose using real bone motion plus separately modeled equipment.
def render_pose(actor, anim, index, count, diagnostic=False):
    ppu = setup_scene(actor)
    use_walk = actor == "baldwin" and anim == "Walk"
    use_action = actor == "baldwin" and anim in ("Idle", "Jump", "Dead", "Attack")
    source = ART / "rigs/baldwin/walk.glb" if use_walk else ART / "rigs/baldwin/actions/animation_glb.glb" if use_action else None
    rig = load_character(actor, source)
    if use_walk or use_action:
        if use_action:
            action_name = {"Idle": "Idle", "Jump": "Regular_Jump", "Dead": "dying_backwards", "Attack": "Right_Hand_Sword_Slash"}[anim]
            rig.animation_data.action = bpy.data.actions[action_name]
            rig.animation_data.action_slot = rig.animation_data.action.slots[0]
        action = rig.animation_data.action
        for track in rig.animation_data.nla_tracks:
            track.mute = True
        lo, hi = action.frame_range
        progress = index / count if use_walk or anim == "Idle" else index / (count - 1)
        if anim == "Attack":
            progress = [0, 0.12, 0.20, 0.28, 0.48][index]
        bpy.context.scene.frame_set(int(lo + (hi - lo) * progress))
        sampled = {bone.name: bone.matrix_basis.copy() for bone in rig.pose.bones}
        rig.animation_data_clear()
        for name, transform in sampled.items():
            rig.pose.bones[name].matrix_basis = transform
        bpy.context.view_layer.update()
        # Strip locomotion from the pose; the game owns motion and jump height.
        hip = rig.matrix_world @ rig.pose.bones["Hips"].head
        rig.location.x -= hip.x
        rig.location.y -= hip.y
    else:
        rig.animation_data_clear()
    mats = {name: material(name, color, metal, glow) for name, color, metal, glow in [
        ("steel", (0.20, 0.29, 0.40), 0.30, 0),
        ("ivory", (0.80, 0.73, 0.58), 0.20, 0),
        ("copper", (0.30, 0.12, 0.055), 0.45, 0),
        ("leather", (0.12, 0.085, 0.065), 0, 0),
        ("ember", (1.0, 0.43, 0.12), 0, 1.4),
    ]}
    # Front hand targets are defined in each actor's frame, not in a recropped bbox.
    grip = screen(0.25, 0.87)
    angle, length = -0.6, 0.95
    offhand = screen(-0.20, 0.88, -0.10)
    if actor == "baldwin":
        if anim == "Idle":
            bend(rig, "Spine01", math.sin(index / count * math.tau) * 1.2)
        elif anim == "Jump":
            grip = screen(0.25, 1.00)
            angle = 0.45
        elif anim == "Attack":
            if index < 4:
                grip = screen(-0.08 + index * 0.045, 1.18 + index * 0.055)
                angle = 1.9 - index * 0.15
                bend(rig, "Spine01", -8 - index * 2)
            else:
                grip = screen(0.36, 0.90)
                angle, length = 0, 1.16
                bend(rig, "Spine01", 12)
        elif anim == "Hurt":
            progress = (index + 1) / count
            lower_hips(rig, 0.48 * progress)
            bend(rig, "Spine01", -18 * progress)
            grip = screen(0.30, 0.65 - progress * 0.3)
            angle, length = -0.4, 0.55
        elif anim == "Dead":
            progress = index / (count - 1)
            rig.location += RIGHT * (0.65 * progress)
            grip = screen(0.55 + progress * 0.3, max(0.12, 0.75 - progress * 0.7))
            angle, length = -0.1, 0.85
    elif actor.startswith("custodio"):
        if index == 1:
            grip, angle, length = screen(0.10, 1.20), 1.45, 0.50
            bend(rig, "Spine01", -7)
        elif index == 2:
            grip, angle, length = screen(0.27, 0.90), 0, 1.22
            bend(rig, "Spine01", 10)
        elif index == 3:
            lower_hips(rig, 0.12)
            bend(rig, "Spine01", 14)
            grip, angle, length = screen(0.36, 0.65), -0.85, 0.70
    elif actor == "acolito":
        grip = screen(0.24, 0.94)
        if index == 1:
            grip = screen(0.15, 1.68)
            bend(rig, "Spine01", -6)
        elif index == 2:
            grip = screen(14 / ppu, 31 / ppu)
            lower_hips(rig, 0.05)
            hips = rig.pose.bones["Hips"]
            shift = rig.matrix_world.inverted().to_3x3() @ (RIGHT * 0.18)
            hips.matrix = Matrix.Translation(shift) @ hips.matrix
            bpy.context.view_layer.update()
            bend(rig, "Spine01", 27)
        elif index == 3:
            lower_hips(rig, 0.10)
            bend(rig, "Spine01", 14)
            grip = screen(0.28, 0.78)
    elif actor == "abad":
        grip, angle, length = screen(0.32, 1.08), 1.1, 0.70
        if index == 1:
            grip, angle, length = screen(-0.28, 1.25), 1.85, 0.80
            bend(rig, "Spine01", -8)
        elif index == 2:
            lower_hips(rig, 0.56)
            bend(rig, "Spine01", 22)
            grip, angle, length = screen(0.30, 0.43), -0.05, 1.32
        elif index in (3, 6, 8):
            lower_hips(rig, {3: 0.48, 6: 0.60, 8: 0.90}[index])
            bend(rig, "Spine01", {3: 15, 6: 35, 8: 55}[index])
            grip, angle = screen(0.25, 0.45 if index == 3 else 0.32), -0.20
        elif index in (4, 5):
            grip = screen(0.20 if index == 4 else 0.36, 2.00 if index == 4 else 1.86)
            offhand = screen(-0.25, 1.15)
            if index == 5:
                bend(rig, "Spine01", 6)
        elif index == 7:
            grip, offhand = screen(0.55, 1.50), screen(-0.5, 1.50)
            bend(rig, "Spine01", -12)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.vertex_groups]
    floor = min((obj.matrix_world @ vertex.co).z for obj in meshes for vertex in obj.evaluated_get(depsgraph).data.vertices)
    rig.location.z -= floor
    bpy.context.view_layer.update()
    if anim != "Dead":
        hand_target(rig, "Right", grip)
        hand_target(rig, "Left", offhand)
        bpy.context.view_layer.update()
    elif index < 3:
        grip = rig.matrix_world @ rig.pose.bones["RightHand"].head
    else:
        grip, angle = screen(1.0, 0.15), 0
    # Ground the solved pose as a unit, including IK targets, without changing it.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    floor = min((obj.matrix_world @ vertex.co).z for obj in meshes for vertex in obj.evaluated_get(depsgraph).data.vertices)
    correction = Vector((0, 0, -floor))
    rig.location += correction
    targets = {constraint.target for bone in rig.pose.bones for constraint in bone.constraints
               if constraint.type == "IK" and constraint.target}
    for target in targets:
        target.location += correction
    bpy.context.view_layer.update()
    wrist = rig.matrix_world @ rig.pose.bones["RightHand"].head
    record = {"actor": actor, "animation": anim, "frame": index, "ppu": ppu,
              "wrist_grip_distance": (wrist - grip).length,
              "grip": list(grip), "wrist": list(wrist)}
    if diagnostic:
        print("POSE_DIAGNOSTIC " + json.dumps(record))
        return record
    # Attach equipment to the evaluated hand even when an IK goal is out of reach.
    # The blade endpoint stays at its authored combat coordinate.
    if anim != "Dead" or index < 3:
        if actor in ("baldwin", "custodio", "custodio_sellado", "abad"):
            direction = RIGHT * math.cos(angle) + UP * math.sin(angle)
            sword_guard = 0.12 if actor != "abad" else 0.0
            endpoint = grip + direction * (length + sword_guard)
            delta = endpoint - wrist
            angle = math.atan2(delta.z, delta.dot(RIGHT))
            length = max(0.10, math.hypot(delta.z, delta.dot(RIGHT)) - sword_guard)
        grip = wrist
    record["equipment_grip"] = list(grip)
    if actor in ("baldwin", "custodio", "custodio_sellado"):
        sword(grip, angle, length, mats)
    elif actor == "acolito":
        censer(grip, mats, index in (1, 2))
    elif actor == "abad":
        if index in (4, 5):
            censer(grip, mats, True)
        elif index != 7:
            scythe(grip, angle, length, mats, low_sweep=index == 2)
    if actor == "custodio_sellado":
        chest = rig.matrix_world @ rig.pose.bones["Spine"].head
        seal(chest, 0.13, mats, active=index == 1, sealed=True)
    elif actor == "abad":
        chest = rig.matrix_world @ rig.pose.bones["Spine"].head
        seal(chest, 0.16, mats, active=index in (3, 6))
    bpy.context.view_layer.update()
    equipment = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and not obj.vertex_groups]
    minimum_z = min((obj.matrix_world @ vertex.co).z for obj in equipment for vertex in obj.data.vertices)
    record["equipment_min_z"] = minimum_z
    if minimum_z < -0.005:
        raise ValueError(f"{actor}/{anim}/{index}: equipment extends below floor ({minimum_z:.3f}m)")
    folder = ART / "frames" / actor / anim
    folder.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(folder / f"{index:03d}.png")
    bpy.ops.render.render(write_still=True)
    return record


# Runs all requested fixed-cell poses and records the reproducible camera contract.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--actor", choices=CONFIG, required=True)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--animation", help="Render only this animation when revising a pose")
    parser.add_argument("--frame", type=int, help="Render only this frame when revising a pose")
    parser.add_argument("--diagnostic", action="store_true", help="Print evaluated wrist distance without rendering")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    animations = {"Idle": 4, "Walk": 8, "Jump": 6, "Attack": 5, "Dead": 6, "Hurt": 2} if args.actor == "baldwin" else {"poses": 9 if args.actor == "abad" else 4}
    record = []
    for anim, count in animations.items():
        if args.animation and args.animation != anim:
            continue
        for index in range(count):
            if args.frame is not None and args.frame != index:
                continue
            if args.preview and (anim != next(iter(animations)) or index != 0):
                continue
            record.append(render_pose(args.actor, anim, index, count, args.diagnostic))
    suffix = "_diagnostic" if args.diagnostic else ""
    if args.animation:
        suffix += "_" + args.animation
    if args.frame is not None:
        suffix += "_" + str(args.frame)
    (ART / f"render_{args.actor}{suffix}.json").write_text(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
