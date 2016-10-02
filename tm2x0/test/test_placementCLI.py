from unittest import TestCase
from tm2x0.kicad import KicadPartPositions
from tm2x0.placement import Placement
from tm2x0.placementcli import PlacementCLI
from helpers import captured_output

sample_kicad_pos = """
### Module positions - created on Wed 07 May 2014 11:43:48 PM JST ###
### Printed by Pcbnew version pcbnew (2013-mar-13)-testing
## Unit = mm, Angle = deg.
## Side : Front
# Ref    Val                  Package         PosX       PosY        Rot     Side
R1       1K                SM0805-SS         141.7320   -64.5160     270.0    Front
R2       10K               SM0805-SS-POL     156.5910   -77.9780     270.0    Front
R3       1M                SM0805-SS         144.7800   -64.5160      90.0    Front
D1       LED                SO14              135.3820   -64.5160     180.0    Front
## End"""

class TestPlacementCLI(TestCase):
    def setUp(self):
        self.placement = Placement()
        self.kicad_part_positions = KicadPartPositions.from_string(sample_kicad_pos)

        self.placement_cli = PlacementCLI(placement=self.placement,
                                          unassigned_parts=self.kicad_part_positions.instructions['Front'])

    def test_assign_part_to_reel(self):
        #self.placement_cli._assign_part_to_reel()
        pass