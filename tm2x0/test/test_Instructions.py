from unittest import TestCase
from tm2x0.instructions import PanelizedBoardInstruction, Comment, OriginOffsetInstruction, FeedSpacingInstruction, \
    SpeedInstruction, StackOffsetInstruction, PartPlacementInstruction, describe_stack

from decimal import Decimal


class TestDescribeReel(TestCase):
    def test_front_tray(self):
        self.assertEqual('The front tray', describe_stack(0))
        self.assertEqual('the front tray', describe_stack(0, capitalize_tray=False))
        self.assertEqual('The front tray', describe_stack(0, capitalize_tray=True))

    def test_reel_1(self):
        self.assertEqual('Reel 1', describe_stack(1))
        self.assertEqual('Reel 1', describe_stack(1, capitalize_tray=False))
        self.assertEqual('Reel 1', describe_stack(1, capitalize_tray=True))


class TestPanelizedBoard(TestCase):
    def setUp(self):
        self.pb = PanelizedBoardInstruction(35.0, 100.2)

    def test_get_x(self):
        self.assertEqual(Decimal('35'), self.pb.x)

    def test_get_y(self):
        self.assertEqual(Decimal('100.2'), self.pb.y)

    def test_output(self):
        panel = PanelizedBoardInstruction(35.0, 100.9)
        self.assertEqual('65535,3,35,100.9,0,0,0,0,', panel.to_csv())

    def test_skip(self):
        panel = PanelizedBoardInstruction(35.0, 100.9, skip=True)
        self.assertEqual('65535,3,35,100.9,1,0,0,0,', panel.to_csv())

    def test_skip_false(self):
        panel = PanelizedBoardInstruction(35.0, 100.9, skip=False)
        self.assertEqual('65535,3,35,100.9,0,0,0,0,', panel.to_csv())


class TestCommentInstruction(TestCase):
    def test_init(self):
        c = Comment("This is a comment!")
        self.assertEqual(c.comment, "This is a comment!")

    def test_output(self):
        c = Comment("This is a comment!")
        self.assertEqual(c.to_csv(), "%This is a comment!")

    def test_empty_comment(self):
        c = Comment()
        self.assertEqual(c.to_csv(), "%")

    def test_describe(self):
        c = Comment("This is a comment!")
        self.assertEqual('Comment of: This is a comment!', c.describe())


class TestOriginOffset(TestCase):
    def test_usage(self):
        t1 = OriginOffsetInstruction(1.0, 1.34)
        self.assertEqual('65535,0,1,1.34,,', t1.to_csv())
        t2 = OriginOffsetInstruction(1, 3)
        self.assertEqual('65535,0,1,3,,', t2.to_csv())
        t3 = OriginOffsetInstruction(1.0303, 1.39)
        self.assertEqual('65535,0,1.03,1.39,,', t3.to_csv())

    def test_description(self):
        t1 = OriginOffsetInstruction(1.0, 1.34)
        self.assertEqual('The origin is offset by (1 mm, 1.34 mm).', t1.describe())


class TestFeedSpacing(TestCase):
    def test_usage(self):
        fs1 = FeedSpacingInstruction(stack=1, feed_spacing=1.3)
        self.assertEqual('65535,2,1,1.3,', fs1.to_csv())

    def test_describe(self):
        fs1 = FeedSpacingInstruction(stack=1, feed_spacing=1.3)
        self.assertEqual('There are 1.3 mm between components on Reel 1.', fs1.describe())


class TestSpeed(TestCase):
    def test_speed(self):
        s = SpeedInstruction(speed=10)
        self.assertEqual('0,10,0,0,0,0,0,0,', s.to_csv())

    def test_faster_speed(self):
        s = SpeedInstruction(speed=150)
        self.assertEqual('0,150,0,0,0,0,0,0,', s.to_csv())

    def test_describe(self):
        s = SpeedInstruction(speed=90)
        self.assertEqual('The machine is now set to 90% speed.', s.describe())


class TestStackOffset(TestCase):
    def test_usage_no_comment(self):
        so = StackOffsetInstruction(stack=1, x=1.3, y=0)
        self.assertEqual('65535,1,1,1.3,0,', so.to_csv())

    def test_usage_comment(self):
        so1 = StackOffsetInstruction(stack=2, x=1.9, y=1.3, comment="what up")
        self.assertEqual('65535,1,2,1.9,1.3,what up', so1.to_csv())

    def test_describe(self):
        so1 = StackOffsetInstruction(stack=2, x=1.9, y=1.3, comment="what up")
        self.assertEqual('Reel 2 has an offset of (1.9, 1.3), with a comment of: what up.',
                         so1.describe())
        so1.comment = None
        self.assertEqual('Reel 2 has an offset of (1.9, 1.3).',
                         so1.describe())


class TestPartPlacement(TestCase):
    def test_usage_no_ref_no_comment(self):
        pp = PartPlacementInstruction(part_number=1,
                                      pickup_head=2,
                                      stack=1,
                                      x=1033.3,
                                      y=99.99,
                                      rotation=-45,
                                      height=2.2,
        )
        self.assertEqual('1,2,1,1033.3,99.99,-45,2.2,0,,', pp.to_csv())

    def test_ref_no_comment(self):
        pp1 = PartPlacementInstruction(part_number=2,
                                       pickup_head=1,
                                       stack=1,
                                       x=33.21,
                                       y=234234.32,
                                       rotation=45,
                                       height=1.0,
                                       reference='LED1'
        )
        self.assertEqual('2,1,1,33.21,234234.32,45,1,0,LED1,', pp1.to_csv())

    def test_ref_and_comment(self):
        pp2 = PartPlacementInstruction(part_number=15,
                                       pickup_head=2,
                                       stack=234,
                                       x=123.3,
                                       y=1,
                                       rotation=0,
                                       height=1,
                                       reference="U1",
                                       comment="P18F4520",
        )
        self.assertEqual('15,2,234,123.3,1,0,1,0,U1,P18F4520', pp2.to_csv())

    def test_describe(self):
        pp1 = PartPlacementInstruction(part_number=15,
                                       pickup_head=2,
                                       stack=234,
                                       x=123.3,
                                       y=1,
                                       rotation=0,
                                       height=1,
                                       reference="U1",
                                       comment="P18F4520"
        )

        self.assertEqual('Part #15 (U1) will be picked up by Head 2 from Reel 234 '
                         'and placed at (123.3 mm, 1 mm) after being rotated 0 '
                         'degrees with comment: P18F4520', pp1.describe())
        pp1.skip = True
        self.assertEqual('SKIPPED: Part #15 (U1) will be picked up by Head 2 '
                         'from Reel 234 and placed at (123.3 mm, 1 mm) after being '
                         'rotated 0 degrees with comment: P18F4520',
                         pp1.describe())
        pp1.comment = None
        self.assertEqual("SKIPPED: Part #15 (U1) will be picked up by Head 2 "
                         "from Reel 234 and placed at (123.3 mm, 1 mm) after "
                         "being rotated 0 degrees", pp1.describe())
        pp1.skip = False
        self.assertEqual("Part #15 (U1) will be picked up by Head 2 "
                         "from Reel 234 and placed at (123.3 mm, 1 mm) after "
                         "being rotated 0 degrees", pp1.describe())


    def test_skip(self):
        pp1 = PartPlacementInstruction(part_number=15,
                                       pickup_head=2,
                                       stack=234,
                                       x=123.3,
                                       y=1,
                                       rotation=0,
                                       height=1,
                                       reference="U1",
                                       comment="P18F4520"
        )
        self.assertEqual('15,2,234,123.3,1,0,1,0,U1,P18F4520', pp1.to_csv())
        pp1.skip = True
        self.assertEqual('15,2,234,123.3,1,0,1,1,U1,P18F4520', pp1.to_csv())
        pp2 = PartPlacementInstruction(part_number=15,
                                       pickup_head=2,
                                       stack=234,
                                       x=123.3,
                                       y=1,
                                       rotation=0,
                                       height=1,
                                       reference="U1",
                                       comment="P18F4520",
                                       skip=True
        )
        self.assertEqual('15,2,234,123.3,1,0,1,1,U1,P18F4520', pp2.to_csv())
        pp3 = PartPlacementInstruction(part_number=15,
                                       pickup_head=2,
                                       stack=234,
                                       x=123.3,
                                       y=1,
                                       rotation=0,
                                       height=1,
                                       reference="U1",
                                       comment="P18F4520",
                                       skip=False
        )
        self.assertEqual('15,2,234,123.3,1,0,1,0,U1,P18F4520', pp3.to_csv())




