import logging
from unittest import TestCase
from decimal import Decimal
from tm2x0.instructions import represent_decimal, Instruction, PlacementInstructions
from testfixtures import log_capture, LogCapture
from StringIO import StringIO


class TestRepresentDecimal(TestCase):
    def rd_from_number(self, number):
        return str(represent_decimal(Decimal(str(number))))

    def test_represent_decimal(self):
        # cuts down to 2 decimals
        self.assertEqual('1.34', self.rd_from_number(1.3399999))

        # removes extra right zeros
        self.assertEqual('1.3', self.rd_from_number(1.30))
        self.assertEqual('1.3', self.rd_from_number(1.30000))
        self.assertEqual('1', self.rd_from_number(1.00000))

        # works wth numbers bigger than one digit
        self.assertEqual('34', self.rd_from_number(34))
        self.assertEqual('100000.3', self.rd_from_number(100000.3))
        self.assertEqual('100000.33', self.rd_from_number(100000.334234))


class TestWhatIWillDoForCoverage(TestCase):
    def test_instruction(self):
        i = Instruction()

    def test_instruction_from_string(self):
        i = Instruction.from_string("")

    def test_instruction_to_csv(self):
        i = Instruction()
        self.assertFalse(i.to_csv())

    def test_add_to_string(self):
        with self.assertRaises(NotImplementedError):
            pi = PlacementInstructions.from_string("655535,69,69,69,69")


class TestPlacementInstructions(TestCase):
    def test_from_string_only_comments(self):
        s = """%This is the first comment.
%This is the second comment."""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(2, len(p.instructions))
        self.assertEqual("This is the first comment.", p.instructions[0].comment)
        self.assertEqual("This is the second comment.", p.instructions[1].comment)

    def test_from_string_origin_offset(self):
        s = """%,OriginOffsetCommand,X,Y,,
65535,0,0,0,,"""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(s, p.to_csv())

    def test_from_string_blank_line(self):
        s = """
"""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(s, p.to_csv())

    def test_from_string_stack_offset(self):
        s = """%,StackOffsetCommand,Stack,X,Y,Comment
65535,1,0,0,0,
65535,1,1,-0.04,-0.1,0603"""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(s, p.to_csv())

    def test_from_string_stack_offset_no_comment(self):
        s = """%,StackOffsetCommand,Stack,X,Y,Comment
65535,1,0,0,0
65535,1,1,-0.04,-0.1"""

        normalized = """%,StackOffsetCommand,Stack,X,Y,Comment
65535,1,0,0,0,
65535,1,1,-0.04,-0.1,"""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(normalized, p.to_csv())


    def test_from_string_feed_spacing(self):
        s = """%,FeedSpacingCommand,Stack,FeedSpacing,
65535,2,0,18,
65535,2,1,4,"""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(s, p.to_csv())


    def test_from_string_panelized_boards(self):
        s = """%,JointedBoardCommand,X,Y
65535,3,1,0,0,0,0,0,"""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(s, p.to_csv())

    def test_from_string_part_placement(self):
        s = """%,Head,Stack,X,Y,R,H,skip,Ref,Comment,
1,1,1,4,22,-45,1,0,LED7,-LED-805
2,2,1,4,19,-45,1,0,LED8,-LED-805
3,1,1,4,16,-45,1,0,LED9,-LED-805"""
        p = PlacementInstructions.from_string(s)
        self.assertEqual(s, p.to_csv())

    def test_from_file(self):

        s = """%,Head,Stack,X,Y,R,H,skip,Ref,Comment,
1,1,1,4,22,-45,1,0,LED7,-LED-805
2,2,1,4,19,-45,1,0,LED8,-LED-805
3,1,1,4,16,-45,1,0,LED9,-LED-805"""
        f = StringIO(s)

        p = PlacementInstructions.from_file(f)
        self.assertEqual(s, p.to_csv())


    def test_from_file_parse_error(self):
        s = """%,Head,Stack,X,Y,R,H,skip,Ref,Comment,
1,1,1,4,22,-45,1,0,LED7,-LED-805
2,2,1,4,19,-45,1,0,LED8,-LED-805
PARSE ERROR NOT IN YOUR FAVOR"""
        f = StringIO(s)

        with LogCapture() as logs:
            try:
                p = PlacementInstructions.from_file(f)
            except:
                pass
            else:
                self.fail()

            logs.check(('root', 'ERROR',
                        "Error parsing line: PARSE ERROR NOT IN YOUR FAVOR"))

    def test_copies(self):
        s = """65535,0,0,0,,
65535,1,1,0,0.05,0402
65535,2,1,2,
0,1,1,141.73,-64.52,-90,0,0,,
1,1,1,156.59,-77.98,-90,0,0,,
2,1,1,144.78,-64.52,90,0,0,,
3,1,1,135.38,-64.52,0,0,0,,"""

        f = StringIO(s)
        p = PlacementInstructions.from_file(f)
        self.assertEqual(p.get_copies(), [])
