"""Continuous camera-facing arm choreography, shared by every attack phase."""


# Keep wrists and elbow poles on the near side of the torso throughout the swing.
def arm_pose(family, phase, progress):
    heavy=family=='Mace'
    guard={'hand':(.25,.91,.32),'other':(.10,1.05,.28),
           'pole':(.60,1.00,.60),'angle':-.55,'lean':0.0,'lower':0.0}
    raised={**guard,'hand':(.23,1.42 if heavy else 1.25,.32),
            'angle':1.65 if heavy else 1.35,'lean':-10.0 if heavy else -6.0,
            'lower':.07 if heavy else .02}
    ready={**guard,'hand':(.28,1.10 if heavy else 1.02,.32),
           'angle':.4 if heavy else .12,'lean':10.0 if heavy else 8.0,
           'lower':.10 if heavy else .02}
    impact={**guard,'hand':(.32,.90,.32),'angle':-.2 if heavy else -.12,
            'lean':20.0 if heavy else 12.0,'lower':.12 if heavy else .02}
    follow={**guard,'hand':(.31,.84,.32),'angle':-.5,'lean':14.0 if heavy else 8.0,
            'lower':.08 if heavy else .01}
    keys={'Startup':[(0,guard),(.7,raised),(1,ready)],
          'Active':[(0,ready),(1,impact)],
          'Recovery':[(0,impact),(.35,follow),(1,guard)]}[phase]
    t=max(0,min(1,progress))
    for time,pose in keys:
        if t==time:return pose
    for (a,first),(b,last) in zip(keys,keys[1:]):
        if a<t<b:
            u=(t-a)/(b-a);u=u*u*(3-2*u)
            return {k:tuple(x+(y-x)*u for x,y in zip(v,last[k])) if isinstance(v,tuple)
                    else v+(last[k]-v)*u for k,v in first.items()}
    raise ValueError('Invalid attack pose interval')
