import unittest
from baldwin_arm_poses import arm_pose


class ArmPoseTests(unittest.TestCase):
    # Grip and elbow must stay on the visible side of the cape for the whole attack.
    def test_entire_attack_keeps_both_hands_and_elbow_in_foreground(self):
        for family in ('Sword','Mace'):
            for phase in ('Startup','Active','Recovery'):
                for i in range(21):
                    p=arm_pose(family,phase,i/20)
                    self.assertGreaterEqual(p['hand'][2],.30)
                    self.assertGreaterEqual(p['other'][2],.20)
                    self.assertGreater(p['pole'][2],p['hand'][2])
                    self.assertGreaterEqual(p['hand'][0],.15)

    # A phase change must not teleport either hand or the held weapon.
    def test_phase_boundaries_and_return_to_guard_are_continuous(self):
        for family in ('Sword','Mace'):
            pairs=[(arm_pose(family,'Startup',1),arm_pose(family,'Active',0)),
                   (arm_pose(family,'Active',1),arm_pose(family,'Recovery',0)),
                   (arm_pose(family,'Recovery',1),arm_pose(family,'Startup',0))]
            for a,b in pairs:
                for key in ('hand','other','pole','angle','lean','lower'):
                    self.assertEqual(a[key],b[key])


if __name__=='__main__':unittest.main()
