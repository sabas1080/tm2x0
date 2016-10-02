"""Most of this file is extremely Neoden TM-220A or TM-240A specific."""

from operator import attrgetter
from tm2x0.partplacement import PartPlacement
from tm2x0.reel import Reel
from os import linesep as platform_linesep
from decimal import Decimal
import logging

logger = logging.getLogger()

TWOPLACES = Decimal(10) ** -2  # same as Decimal('0.01')


def represent_decimal(d):
    return d.quantize(TWOPLACES).normalize()


def describe_stack(stack_number, capitalize_tray=True):
    if stack_number == 0 and capitalize_tray:
        return "The front tray"
    elif stack_number == 0 and not capitalize_tray:
        return "the front tray"
    else:
        return "Reel {0}".format(stack_number)


class Instruction():
    @classmethod
    def from_string(cls, line):
        pass

    def __init__(self):
        pass

    def _get_csv_tokens(self):
        return ""

    def to_csv(self):
        tokens = self._get_csv_tokens()
        if tokens:
            return ','.join(self._get_csv_tokens())


class Blank(Instruction):
    """Blank is an instruction that maintains blank lines in your input files."""

    @classmethod
    def from_tokens(cls, tokens):
        if len(tokens) == 1 and tokens[0] == '':
            return cls()

    def to_csv(self):
        return ''

    def describe(self):
        return "(This line intentionally left blank.)"


class Comment(Instruction):
    def __init__(self, comment=None):
        Instruction.__init__(self)
        if not comment:
            self.comment = ''
        else:
            self.comment = comment

    @classmethod
    def from_tokens(cls, tokens):
        if tokens[0].startswith('%'):
            full_line = ','.join(tokens)
            return cls(full_line[1:])

    def to_csv(self):
        return "%" + self.comment

    def describe(self):
        return "Comment of: {0}".format(self.comment)


class OriginOffsetInstruction(Instruction):
    def __init__(self,
                 x,
                 y):
        self._x = Decimal(str(x))
        self._y = Decimal(str(y))
        Instruction.__init__(self)


    @classmethod
    def from_tokens(cls, tokens):
        flags = int(tokens[0]), int(tokens[1])
        if flags[0] == 65535 and flags[1] == 0:
            return cls(x=tokens[2],
                       y=tokens[3])

    @property
    def x(self):
        return represent_decimal(self._x)

    @property
    def y(self):
        return represent_decimal(self._y)

    def _get_csv_tokens(self):
        return [str(token) for token in (65535,
                                         0,
                                         self.x,
                                         self.y,
                                         '',
                                         '',
        )
        ]

    def describe(self):
        return "The origin is offset by ({0} mm, {1} mm).".format(self.x, self.y)


class StackOffsetInstruction(Instruction):
    def __init__(self, stack, x, y, comment=None):
        Instruction.__init__(self)
        self.stack = int(stack)
        if not comment:
            self.comment = ''
        else:
            self.comment = comment
        self._x = Decimal(str(x))
        self._y = Decimal(str(y))

    @classmethod
    def from_tokens(cls, tokens):
        flags = int(tokens[0]), int(tokens[1])
        if flags[0] == 65535 and flags[1] == 1:
            out = cls(stack=int(tokens[2]),
                      x=tokens[3],
                      y=tokens[4])
            if len(tokens) > 5:
                out.comment = tokens[5]
            return out

    @property
    def x(self):
        return represent_decimal(self._x)

    @property
    def y(self):
        return represent_decimal(self._y)

    def _get_csv_tokens(self):
        return [str(token) for token in (65535,
                                         1,
                                         self.stack,
                                         self.x,
                                         self.y,
                                         self.comment,
        )
        ]

    def describe(self):
        out = "{0} has an offset of ({1}, {2})".format(describe_stack(self.stack),
                                                       self.x,
                                                       self.y)
        if self.comment:
            out += ", with a comment of: {0}".format(self.comment)

        out += "."
        return out


class FeedSpacingInstruction(Instruction):
    def __init__(self, stack, feed_spacing):
        Instruction.__init__(self)
        self.stack = int(stack)
        self._feed_spacing = Decimal(str(feed_spacing))

    @classmethod
    def from_tokens(cls, tokens):
        flags = int(tokens[0]), int(tokens[1])
        if flags[0] == 65535 and flags[1] == 2:
            return cls(stack=tokens[2],
                       feed_spacing=tokens[3])

    @property
    def feed_spacing(self):
        return represent_decimal(self._feed_spacing)

    def _get_csv_tokens(self):
        return [str(token) for token in (65535,
                                         2,
                                         self.stack,
                                         self.feed_spacing,
                                         '',
        )
        ]

    def describe(self):
        return "There are {0} mm between components on {1}.".format(self.feed_spacing,
                                                                    describe_stack(self.stack, capitalize_tray=False))


class PanelizedBoardInstruction(Instruction):
    def __init__(self, x, y, skip=False):
        Instruction.__init__(self)
        self._x = Decimal(str(x))
        self._y = Decimal(str(y))
        self.skip = skip

    @classmethod
    def from_tokens(cls, tokens):
        flags = int(tokens[0]), int(tokens[1])
        if flags[0] == 65535 and flags[1] == 3:
            return cls(x=tokens[2],
                       y=tokens[3],
                       skip=int(tokens[4]))

    @property
    def x(self):
        return represent_decimal(self._x)

    @property
    def y(self):
        return represent_decimal(self._y)

    def _get_csv_tokens(self):
        return [str(token) for token in (65535,
                                         3,
                                         self.x,
                                         self.y,
                                         1 if self.skip else 0,
                                         0,
                                         0,
                                         0,
                                         ''
        )
        ]

    def describe(self):
        if self.skip:
            out = "SKIPPED: "
        else:
            out = ""

        out += "Another copy of the board will be placed at ({0} mm, {1} mm)".format(self.x(), self.y())
        return out


class SpeedInstruction(Instruction):
    def __init__(self, speed):
        Instruction.__init__(self)
        self.speed = speed

    @classmethod
    def from_tokens(cls, tokens):
        if int(tokens[0]) == 0:
            return cls(speed=int(tokens[1]))

    def _get_csv_tokens(self):
        return [str(token) for token in (0,
                                         self.speed,
                                         0,
                                         0,
                                         0,
                                         0,
                                         0,
                                         0,
                                         ''
        )
        ]

    def describe(self):
        return "The machine is now set to {0}% speed.".format(self.speed)


class PartPlacementInstruction(Instruction):
    def __init__(self,
                 part_number,
                 pickup_head,
                 stack,
                 x,
                 y,
                 rotation,
                 height,
                 skip=False,
                 reference=None,
                 comment=None):
        Instruction.__init__(self)
        self.part_number = int(part_number)
        self.pickup_head = int(pickup_head)
        self.stack = int(stack)
        self._x = Decimal(str(x))
        self._y = Decimal(str(y))
        self.rotation = int(rotation)
        self._height = Decimal(str(height))
        self.skip = skip
        if not reference:
            self.reference = ''
        else:
            self.reference = reference
        if not comment:
            self.comment = ''
        else:
            self.comment = comment

    @classmethod
    def from_tokens(cls, tokens):
        flag = int(tokens[0])
        if 0 < flag < 65535:
            return cls(part_number=tokens[0],
                       pickup_head=tokens[1],
                       stack=tokens[2],
                       x=tokens[3],
                       y=tokens[4],
                       rotation=tokens[5],
                       height=tokens[6],
                       skip=int(tokens[7]),
                       reference=tokens[8],
                       comment=tokens[9])

    @property
    def x(self):
        return represent_decimal(self._x)

    @property
    def y(self):
        return represent_decimal(self._y)

    @property
    def height(self):
        return represent_decimal(self._height)

    def _get_csv_tokens(self):
        return [str(token) for token in (self.part_number,
                                         self.pickup_head,
                                         self.stack,
                                         self.x,
                                         self.y,
                                         self.rotation,
                                         self.height,
                                         1 if self.skip else 0,
                                         self.reference,
                                         self.comment,
        )
        ]

    def describe(self):
        out = []
        if self.skip:
            out = ["SKIPPED:"]
        else:
            out = []

        out.append("Part #{0}".format(self.part_number))
        if self.reference:
            out.append("({0})".format(self.reference))
        out.append("will be picked up by Head {0}".format(self.pickup_head))
        out.append("from {0}".format(describe_stack(self.stack, capitalize_tray=False)))
        out.append("and placed at ({0} mm, {1} mm)".format(self.x, self.y))
        if self.rotation > 0:
            suffix = " counter-clockwise"
        elif self.rotation < 0:
            suffix = " clockwise"
        else:
            suffix = ""
        out.append("after being rotated {0} degrees{1}".format(self.rotation, suffix))
        if self.comment:
            out.append("with comment: {0}".format(self.comment))
        return " ".join(out)


class PlacementInstructions():
    def __init__(self):
        self.instructions = []

    def get_copies(self):
        panelized_boards = []
        for instruction in self.instructions:
            if isinstance(instruction, PanelizedBoardInstruction):
                if not instruction.skip:
                    panelized_boards.append((instruction.x, instruction.y))
        return panelized_boards

    def global_offset(self):
        offset_x = 0
        offset_y = 0
        offsets = [instruction for instruction in self.instructions if isinstance(instruction, OriginOffsetInstruction)]
        if len(offsets) > 1:
            raise Exception("Multiple global offsets specified")
        elif len(offsets) == 0:
            offset_x = offsets[0].x
            offset_y = offsets[0].y

        return offset_x, offset_y

    def add_from_line(self, line):
        tokens = line.split(",")
        instructions = [Comment,
                        Blank,
                        SpeedInstruction,
                        OriginOffsetInstruction,
                        StackOffsetInstruction,
                        FeedSpacingInstruction,
                        PanelizedBoardInstruction,
                        PartPlacementInstruction,
        ]
        for instruction in instructions:
            val = instruction.from_tokens(tokens)
            if val:
                self.instructions.append(val)
                return
        raise NotImplementedError("Unrecognized instruction type in line: {0}".format(line))

    @classmethod
    def from_file(cls, f):
        out = cls()
        for line in f:
            line = line.strip()
            try:
                out.add_from_line(line)
            except:
                logging.error("Error parsing line: {0}".format(line))
                raise
        return out

    @classmethod
    def from_string(cls, s):
        out = cls()
        for line in s.split(platform_linesep):
            line = line.strip()
            out.add_from_line(line)
        return out

    def to_csv(self, line_ending=None):
        if line_ending is None:
            line_ending = "\n"
        return line_ending.join([instruction.to_csv() for instruction in self.instructions])

    def describe(self):
        out = []
        for instruction in self.instructions:
            out.append(instruction.describe())
        return out