from decimal import Decimal
from tm2x0.partplacement import PartPlacement
from os import linesep as platform_linesep


def detect_units(s):
    for line in s.split('\n'):
        if line.startswith("## Unit = "):
            if line.startswith("## Unit = mm"):
                return "mm"
            elif line.startswith("## Unit = inches"):
                return "in"
            else:
                raise ValueError("Unexpected units specified: {0}".format(line))


class KicadPartPositions():
    def __init__(self,
                 units):
        self.instructions = {}
        self.lines = []
        self.units = units

    @classmethod
    def from_string(cls, s):
        units = detect_units(s)
        out = cls(units=units)
        for line in s.split(platform_linesep):
            line = line.strip()
            out.add_from_line(line)
        return out

    @classmethod
    def from_file(cls, fp):
        # ugh, all this just for autodetecting units?
        s = fp.read()
        return cls.from_string(s)

    def add(self, part, side):
        if side not in self.instructions:
            self.instructions[side] = []
        self.instructions[side].append(part)

    def add_from_line(self, line):
        self.lines.append(line)
        if line.startswith("#") or not line:
            return
        else:
            tokens = line.split()
            try:
                side = tokens[6]

                reference = tokens[0]
                value = tokens[1]
                footprint = tokens[2]

                if self.units == "in":
                    conversion = Decimal("25.4")
                else:
                    conversion = 1
                x = Decimal(tokens[3]) * conversion
                y = Decimal(tokens[4]) * conversion

                # KiCad rotation is clockwise, from 0 to 360.
                #PartPlacement rotation is counterclockwise, from -180 to 180.
                #Kicad rotation is from "normal orientation"
                #PartPlacement rotation is from how it comes on the reel!
                #We're going to assume that Kicad rotation refers to rotation from reel norm.

                rotation = int(-1 * (Decimal(tokens[5]) - 180))

                self.add(PartPlacement(reference=tokens[0],
                                       value=tokens[1],
                                       footprint=tokens[2],
                                       x=tokens[3],
                                       y=tokens[4],
                                       rotation=rotation), side)
            except IndexError, e:
                print "Unable to parse line {0}".format(line)
                raise e
