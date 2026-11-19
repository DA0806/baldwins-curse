#!/usr/bin/env python3
"""Render body-only animation and evaluated hand poses for independent equipment."""
import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from baldwin_arm_poses import arm_pose

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'Art/Meshy/animation_v2'
SOURCE = ROOT / 'Art/Meshy/prerendered'
spec = importlib.util.spec_from_file_location('previous_render', ROOT / 'tools/render_characters.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
CONFIG = {'baldwin': (128,128,32,127,64,1.75), 'custodio': (128,96,64,95,60,1.75),
          'custodio_sellado': (128,96,64,95,60,1.75), 'acolito': (96,96,48,95,56,1.75),
          'abad': (256,160,128,151,88,2.0)}
PLAYER = {'Idle':8,'Walk':16,'Run':16,'Jump':10,'Hurt':6,'Dead':12,'Dash':12,
          'AttackSwordStartup':6,'AttackSwordActive':4,'AttackSwordRecovery':6,
          'AttackMaceStartup':8,'AttackMaceActive':4,'AttackMaceRecovery':8}
GUARD = {'Idle':6,'Walk':12,'Startup':6,'Active':4,'Recovery':8}
ACOLYTE = {'Idle':8,'Tell':8,'Throw':6,'Recover':8}
BOSS = {'Idle':8,'Advance':12,'SweepTell':8,'Sweep':6,'SweepRecover':10,
        'RainTell':8,'Rain':6,'Exhausted':10,'Stagger':8,'Dead':12}


# Return the ordered clip contract consumed by Godot's presentation components.
def clips(actor):
    return PLAYER if actor=='baldwin' else BOSS if actor=='abad' else ACOLYTE if actor=='acolito' else GUARD


# Freeze a sampled Meshy pose before adding deterministic grip and weight adjustments.
def sample_pose(rig, action_name, progress):
    action = bpy.data.actions[action_name] if action_name else rig.animation_data.action
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    lo,hi = action.frame_range
    position=lo+(hi-lo)*progress
    bpy.context.scene.frame_set(int(position),subframe=position-int(position))
    matrices = {bone.name:bone.matrix_basis.copy() for bone in rig.pose.bones}
    rig.animation_data_clear()
    for name,mat in matrices.items():
        rig.pose.bones[name].matrix_basis=mat
    bpy.context.view_layer.update()
    hips=rig.matrix_world @ rig.pose.bones['Hips'].head
    rig.location.x-=hips.x
    rig.location.y-=hips.y
    bpy.context.view_layer.update()


# Translate the whole solved pose, including constraints, onto a shared ground plane.
def ground(rig):
    dg=bpy.context.evaluated_depsgraph_get()
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.vertex_groups]
    floor=min((o.matrix_world @ v.co).z for o in meshes for v in o.evaluated_get(dg).data.vertices)
    correction=Vector((0,0,-floor))
    rig.location+=correction
    targets={obj for b in rig.pose.bones for c in b.constraints if c.type=='IK' for obj in (c.target,c.pole_target) if obj}
    for target in targets:target.location+=correction
    bpy.context.view_layer.update()


# Turn the gripping hand with the shaft and export the middle of the palm.
def orient_gripping_hand(rig,angle):
    bone=rig.pose.bones['RightHand']
    current=rig.matrix_world @ bone.matrix
    direction=base.RIGHT*math.cos(angle)+Vector((0,0,1))*math.sin(angle)
    side=base.TOWARD
    normal=side.cross(direction).normalized()
    rotation=Matrix((side,direction,normal)).transposed().to_quaternion()
    world=Matrix.LocRotScale(current.translation,rotation,current.to_scale())
    bone.matrix=rig.matrix_world.inverted() @ world
    bpy.context.view_layer.update()
    return current.translation+direction*.055


# Pose each frame with body mechanics; weapons are never burned into this render.
def render_frame(actor,clip,index,count):
    base.CONFIG=CONFIG
    ppu=base.setup_scene(actor)
    source_actor='custodio' if actor=='custodio_sellado' else actor
    locomotion=clip in ('Walk','Run','Advance','Dash')
    library=actor=='baldwin' and not locomotion and clip!='Hurt'
    source=SOURCE/'rigs'/source_actor/('run.glb' if clip=='Run' else 'walk.glb' if locomotion else 'actions/animation_glb.glb' if library else 'rigged_character.glb')
    rig=base.load_character(actor,source)
    cyclic=clip in ('Idle','Walk','Run','Advance')
    t=index/count if cyclic else index/max(1,count-1)
    if locomotion:
        sample_pose(rig,None,t if clip!='Dash' else .18+.45*t)
    elif library:
        action='Idle'
        progress=t
        if clip=='Jump':action='Regular_Jump'
        elif clip=='Dead':action='dying_backwards'
        elif clip.startswith('Attack'):
            # Keep the same readable torso orientation through the entire attack.
            action='Idle'
            progress=0
        sample_pose(rig,action,progress)
    else:
        rig.animation_data_clear()
    hand=base.screen(.25,.91,.32) if actor=='baldwin' else base.screen(.25,.91)
    other=base.screen(.10,1.05,.28) if actor=='baldwin' else base.screen(-.18,.90,-.10)
    angle=-.55
    weapon='sword'
    scale=1.0
    visible=True
    if actor=='baldwin':
        if clip=='Idle':
            base.bend(rig,'Spine01',math.sin(t*math.tau)*1.4)
            hand=base.screen(.25,.91+.016*math.sin(t*math.tau),.32)
        elif clip=='Jump':
            hand=base.screen(.22,1.0,.32);angle=.35
        elif clip=='Hurt':
            envelope=math.sin(t*math.pi)
            base.lower_hips(rig,.10*envelope)
            base.bend(rig,'Spine01',-18*envelope)
            base.bend(rig,'Head',-12*envelope*t)
            hand=base.screen(.15,.90-.15*envelope,.32);angle=-.3
        elif clip=='Dash':
            envelope=math.sin(t*math.pi)**.5
            base.lower_hips(rig,.24*envelope)
            base.bend(rig,'Spine01',48*envelope)
            base.bend(rig,'Head',-20*envelope)
            hand=base.screen(-.15,.95-.10*envelope,.32);angle=-.55+3.45*envelope
        elif clip=='Dead':
            rig.location+=base.RIGHT*(.65*t)
            visible=index<7
        elif clip.startswith('Attack'):
            family='Mace' if 'Mace' in clip else 'Sword'
            phase=clip.removeprefix('Attack'+family)
            pose=arm_pose(family,phase,t)
            hand=base.screen(*pose['hand'])
            other=base.screen(*pose['other'])
            angle=pose['angle']
            base.bend(rig,'Spine01',pose['lean'])
            if pose['lower']:base.lower_hips(rig,pose['lower'])
    elif actor.startswith('custodio'):
        scale=.65
        if clip=='Idle':
            base.bend(rig,'Spine01',2*math.sin(t*math.tau))
        elif clip=='Startup':
            hand=base.screen(.18-.08*t,1.05+.35*t);angle=.4+1.15*t
            base.bend(rig,'Spine01',-8*t)
        elif clip=='Active':
            hand=base.screen(.28,.85);angle=.08-.16*t
            base.bend(rig,'Spine01',10+4*t)
        elif clip=='Recovery':
            base.lower_hips(rig,.12*(1-t));base.bend(rig,'Spine01',14*(1-t))
            hand=base.screen(.32-.07*t,.73+.18*t);angle=-.7+.15*t
    elif actor=='acolito':
        weapon='censer';scale=.45;angle=0
        if clip=='Idle':
            hand=base.screen(.22+.025*math.sin(t*math.tau),.90)
            base.bend(rig,'Spine01',3*math.sin(t*math.tau))
        elif clip=='Tell':
            hand=base.screen(.18,.95+.72*t);base.bend(rig,'Spine01',-6*t)
        elif clip=='Throw':
            hand=base.screen(14/ppu,31/ppu)
            base.lower_hips(rig,.05)
            hips=rig.pose.bones['Hips']
            shift=rig.matrix_world.inverted().to_3x3() @ (base.RIGHT*(.16+.03*t))
            hips.matrix=Matrix.Translation(shift)@hips.matrix
            bpy.context.view_layer.update();base.bend(rig,'Spine01',25+4*t)
        else:
            hand=base.screen(.30-.08*t,1.16-.26*t);base.bend(rig,'Spine01',15*(1-t))
    else:
        weapon='scythe';scale=.90
        hand=base.screen(.3,1.08);angle=1.1
        if clip=='Idle':base.bend(rig,'Spine01',1.3*math.sin(t*math.tau))
        elif clip=='SweepTell':
            hand=base.screen(.15-.43*t,1.08+.20*t);angle=1.1+.8*t
            base.bend(rig,'Spine01',-10*t)
        elif clip=='Sweep':
            base.lower_hips(rig,.56);base.bend(rig,'Spine01',20+6*t)
            hand=base.screen(.28+.05*t,.53);angle=0
        elif clip in ('SweepRecover','Exhausted','Dead'):
            dead=clip=='Dead';depth=(.48-.15*t if clip=='SweepRecover' else .60-.04*math.sin(t*math.pi) if not dead else .25+.65*t)
            base.lower_hips(rig,depth)
            base.bend(rig,'Spine01',(18-9*t if clip=='SweepRecover' else 35+3*math.sin(t*math.tau) if not dead else 20+35*t))
            if clip=='Exhausted':base.bend(rig,'Head',-4*math.sin(t*math.pi))
            hand=base.screen(.25,.5 if clip=='SweepRecover' else .38);angle=-.1
            visible=not dead or index<8
        elif clip in ('RainTell','Rain'):
            weapon='censer';scale=.60;angle=0
            hand=base.screen(.20+.16*(t if clip=='Rain' else 0),1.1+.9*t if clip=='RainTell' else 1.9)
            if clip=='Rain':base.bend(rig,'Spine01',6*t)
        elif clip=='Stagger':
            hand=base.screen(.4+.10*t,1.35+.15*t);other=base.screen(-.5,1.5)
            base.bend(rig,'Spine01',-12*math.sin(t*math.pi));visible=False
    ground(rig)
    if clip!='Dead':
        base.hand_target(rig,'Right',hand);base.hand_target(rig,'Left',other)
        if actor=='baldwin':
            right_pole=pose['pole'] if clip.startswith('Attack') else (-.45,.85,.60) if clip=='Dash' else (.60,1.00,.60)
            for side,point in [('Right',right_pole),('Left',(-.25,.95,.50))]:
                bpy.ops.object.empty_add(location=base.screen(*point))
                pole=bpy.context.object
                pole.name=side+' visible attack elbow pole'
                rig.pose.bones[side+'ForeArm'].constraints[-1].pole_target=pole
        bpy.context.view_layer.update();ground(rig)
    wrist=rig.matrix_world @ rig.pose.bones['RightHand'].head
    if actor=='baldwin' and clip!='Dead':wrist=orient_gripping_hand(rig,angle)
    if actor=='custodio_sellado' or actor=='abad':
        mats={'copper':base.material('copper',(.3,.12,.055),.45),
              'ivory':base.material('ivory',(.8,.73,.58),.2),
              'ember':base.material('ember',(1,.43,.12),0,1.4)}
        chest=rig.matrix_world @ rig.pose.bones['Spine'].head
        base.seal(chest,.13 if actor!='abad' else .16,mats,
                  active=(clip=='Startup' if actor!='abad' else clip in ('SweepRecover','Exhausted')),
                  sealed=actor!='abad')
    w,h,px,py,_,_=CONFIG[actor]
    root_y=96 if actor in ('baldwin','abad') else 72
    row={'hand':[round(wrist.dot(base.RIGHT)*ppu,4),round(py-root_y-wrist.z*ppu,4)],
         'angle':round(-angle,5),'weapon':weapon,'weapon_scale':scale,'weapon_visible':visible}
    if actor=='baldwin' and clip=='Dead' and index>=7:
        row['hand']=[30,29];row['angle']=0;row['weapon_visible']=False
    folder=ART/'frames'/actor/clip;folder.mkdir(parents=True,exist_ok=True)
    bpy.context.scene.render.filepath=str(folder/f'{index:03d}.png')
    bpy.ops.render.render(write_still=True)
    return row


# Write one actor's pose data atomically after all its frame renders succeed.
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--actor',choices=CONFIG,required=True);parser.add_argument('--clip')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);actor=args.actor
    datafile=ART/f'{actor}_poses.json'
    rows=json.loads(datafile.read_text()) if args.clip and datafile.exists() else {}
    for clip,count in clips(actor).items():
        if args.clip and args.clip!=clip:continue
        poses=[render_frame(actor,clip,i,count) for i in range(count)]
        rows[clip]={'count':count,'fps':16.0 if clip in ('Walk','Advance') else 8.0 if clip=='Idle' else 24.0,
                    'loop':clip in ('Idle','Walk','Run','Advance'),'poses':poses}
        if clip=='Dash':rows[clip]['fps']=60.0
        if clip=='Idle':rows[clip]['fps']=4.0 if actor=='baldwin' else 3.0 if actor=='acolito' else 2.0
        # Twice the measured in-place foot range, projected through the side camera.
        if clip in ('Walk','Run') and actor=='baldwin':rows[clip]['stride_px']=54.5 if clip=='Walk' else 64.4
    (ART/f'{actor}_poses.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__':main()
