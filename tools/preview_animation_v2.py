#!/usr/bin/env python3
"""Show the independent equipment on the exact rendered hand poses."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'Art/Meshy/animation_v2'
OUT=ROOT/'docs/animation_v2'


# Rotate around the exported grip, preserving its position in body coordinates.
def composite(body,pose,weapon):
    canvas=Image.new('RGBA',(384,192),'#151924');canvas.alpha_composite(body,(96,32))
    if pose.get('weapon_visible',True):
        layer=Image.new('RGBA',(256,256));layer.alpha_composite(weapon,(120,112))
        layer=layer.rotate(-math.degrees(pose['angle']),resample=Image.Resampling.BICUBIC,center=(128,128))
        x=96+32+pose['hand'][0];y=32+96+pose['hand'][1]
        canvas.alpha_composite(layer,(round(x)-128,round(y)-128))
    return canvas.convert('RGB')


# Make direct frame animations; no artificial intermediate motion is added.
def main():
    OUT.mkdir(exist_ok=True,parents=True);data=json.loads((ART/'baldwin_poses.json').read_text())
    jobs={'Sword':['AttackSwordStartup','AttackSwordActive','AttackSwordRecovery'],
          'Mace':['AttackMaceStartup','AttackMaceActive','AttackMaceRecovery'],
          'Dash':['Dash'],'Run':['Run'],'Idle':['Idle']}
    for name,clips in jobs.items():
        weapon=Image.open(ROOT/'Sprites/Equipment'/('mace.png' if name=='Mace' else 'sword.png')).convert('RGBA')
        frames=[];durations=[]
        for clip in clips:
            sheet=Image.open(ROOT/'Sprites/Characters/Baldwin'/f'{clip}.png').convert('RGBA')
            row=data[clip]
            phase=.28 if clip.endswith('Startup') and name=='Mace' else .16 if clip.endswith('Startup') else .10 if clip.endswith('Active') and name=='Mace' else .08 if clip.endswith('Active') else .32 if name=='Mace' else .16
            if name not in ('Sword','Mace'):phase=.20 if name=='Dash' else row['count']/row['fps']
            for i,p in enumerate(row['poses']):
                body=sheet.crop((128*i,0,128*(i+1),128));frame=composite(body,p,weapon)
                frame=frame.resize((768,384),Image.Resampling.NEAREST)
                ImageDraw.Draw(frame).text((16,12),f'{name} · {clip}',fill='#E5D6B3',font=ImageFont.load_default(size=18))
                frames.append(frame);durations.append(max(20,round(phase/len(row['poses'])*1000)))
        frames[0].save(OUT/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2)
    print('Created five animated equipment previews')


if __name__=='__main__':main()
