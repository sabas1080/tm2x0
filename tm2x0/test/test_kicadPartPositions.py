import StringIO
from unittest import TestCase

from tm2x0.kicad import KicadPartPositions


class TestKicadPartPositions(TestCase):
    sample_mm = """### Module positions - created on Wed 07 May 2014 11:43:48 PM JST ###
### Printed by Pcbnew version pcbnew (2013-mar-13)-testing
## Unit = mm, Angle = deg.
## Side : Front
# Ref    Val                  Package         PosX       PosY        Rot     Side
C1       C                SM1206-SS         141.7320   -64.5160     270.0    Front
D1       LED              SM1206-SS-POL     156.5910   -77.9780     270.0    Front
R1       10K              SM1206-SS         144.7800   -64.5160      90.0    Front
U1       PIC16F1823       SO14              135.3820   -64.5160     180.0    Front
## End"""


    # Please note that Kicad here appears to have completely botched the unit conversion...

    sample_in = """### Module positions - created on Thu 08 May 2014 12:24:13 AM JST ###
### Printed by Pcbnew version pcbnew (2013-mar-13)-testing
## Unit = inches, Angle = deg.
## Side : Front
# Ref    Val                  Package         PosX       PosY        Rot     Side
C1       C                SM1206-SS         141.7320   -64.5160     270.0    Front
D1       LED              SM1206-SS-POL     156.5910   -77.9780     270.0    Front
R1       10K              SM1206-SS         144.7800   -64.5160      90.0    Front
U1       PIC16F1823       SO14              135.3820   -64.5160     180.0    Front
## End"""

    sample_twosides_mm = """### Module positions - created on Thu 08 May 2014 12:24:48 AM JST ###
### Printed by Pcbnew version pcbnew (2013-mar-13)-testing
## Unit = mm, Angle = deg.
## Side : All
# Ref    Val                  Package         PosX       PosY        Rot     Side
C1       C                SM1206-SS         141.7320   -64.5160     270.0    Front
D1       LED              SM1206-SS-POL     156.5910   -77.9780     270.0    Front
R1       10K              SM1206-SS         144.7800   -64.5160      90.0    Back
U1       PIC16F1823       SO14              135.3820   -64.5160     180.0    Back
## End"""

    def test_one_side_mm_from_string(self):
        kpp = KicadPartPositions.from_string(TestKicadPartPositions.sample_mm)

    #C1       C                SM1206-SS         141.7320   -64.5160     270.0    Front
    #D1       LED              SM1206-SS-POL     156.5910   -77.9780     270.0    Front
    #R1       10K              SM1206-SS         144.7800   -64.5160      90.0    Front
    #U1       PIC16F1823       SO14              135.3820   -64.5160     180.0    Front
    #self.fail()

    def test_two_side_mm_from_string(self):
        kpp = KicadPartPositions.from_string(TestKicadPartPositions.sample_twosides_mm)
        #self.fail() #TODO actually test

    def test_one_side_in_from_string(self):
        kpp = KicadPartPositions.from_string(TestKicadPartPositions.sample_in)
        #self.fail() #TODO actually test

    def test_from_file(self):
        stringio = StringIO.StringIO(self.sample_mm)
        kpp = KicadPartPositions.from_file(stringio)


    def test_original_file_stored_in_lines(self):
        kpp = KicadPartPositions.from_string(TestKicadPartPositions.sample_mm)
        orig_lines = '\n'.join(kpp.lines)
        self.assertEqual(TestKicadPartPositions.sample_mm, orig_lines)


