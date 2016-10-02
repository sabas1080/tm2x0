from operator import attrgetter

from tm2x0.instructions import PlacementInstructions, OriginOffsetInstruction, PanelizedBoardInstruction, \
    StackOffsetInstruction, FeedSpacingInstruction, PartPlacementInstruction
from tm2x0.partplacement import PartPlacement
from tm2x0.reel import Reel
import logging


class Placement():
    """A Placement is a combination of Reels and Parts().  It also has panelization and
    a global offset."""

    def __init__(self,
                 parts=None,
                 reels=None,
                 copies=None,
                 offset_x=0,
                 offset_y=0,
    ):

        if parts is None:
            self.clear_parts()
        else:
            self.parts = parts

        if reels is None:
            self.reels = {}
        else:
            self.reels = reels

        self.offset_x = offset_x
        self.offset_y = offset_y

        if copies is None:
            self.copies = []
        else:
            self.copies = copies

    def get_reel_for_part(self, part):
        return self.reels[part.reel]

    def get_parts_for_reel(self, reel):
        return self.parts[reel.reel_number]

    @classmethod
    def from_instructions(cls, instructions):
        out = cls()

        offset_x, offset_y = instructions.global_offset()
        out.offset_x = offset_x
        out.offset_y = offset_y

        out.copies = instructions.get_copies()

        for instruction in instructions:
            if isinstance(instruction, StackOffsetInstruction):
                if instruction.stack not in out.reels:
                    out.reels[instruction.stack] = Reel(instruction.stack)
                out.reels[instruction.stack].stack_x_offset = instruction.x
                out.reels[instruction.stack].stack_y_offset = instruction.y
            elif isinstance(instruction, FeedSpacingInstruction):
                if instruction.stack not in out.reels:
                    out.reels[instruction.stack] = Reel(instruction.stack)
                out.reels[instruction.stack].feed_spacing = instruction.feed_spacing
            elif isinstance(instruction, PartPlacementInstruction):
                if not instruction.skip:
                    p = PartPlacement(rotation=instruction.rotation,
                                      height=instruction.height,
                                      x=instruction.x,
                                      y=instruction.y,
                                      reference=instruction.reference,
                                      comment=instruction.comment,
                                      reel=instruction.stack,
                                      head=instruction.pickup_head
                    )

                if p.reel not in out.parts:
                    out.parts[p.reel] = []
                out.assign_part_to_reel(p, p.reel)
                if p.reel not in out.reels:
                    out.reels[instruction.stack] = Reel(instruction.stack)

        # check heights
        part_heights = {}
        for reel_number, part_list in out.parts.items():
            for part in part_list:
                if part.reel not in part_heights:
                    part_heights[reel_number] = set()
                part_heights[reel_number].add(part.height)

        for reel_number, heights in part_heights.items():
            if len(heights) > 1:
                logging.warning("Multiple heights assigned to different parts for Reel {0}".format(reel_number))
            else:
                out.reels[reel_number].height = heights[0]

        return out

    def get_parts_sorted_by_reference(self, reel_number):
        return sorted(self.parts[reel_number], key=attrgetter("reference"))

    def generate_instructions(self):
        logging.info("Generating instructions.")
        instructions = PlacementInstructions()
        logging.info("Adding offset instruction.")
        instructions.instructions.append(OriginOffsetInstruction(x=self.offset_x,
                                                                 y=self.offset_y))

        for x_offset, y_offset in self.copies:
            logging.info("Adding copy at ({0}, {1})".format(x_offset, y_offset))
            instructions.instructions.append(PanelizedBoardInstruction(x=x_offset,
                                                                       y=y_offset))

        for reel_number in sorted(self.reels.keys()):
            reel = self.reels[reel_number]
            logging.info("Setting stack offset for Reel {0}".format(reel_number))
            instructions.instructions.append(StackOffsetInstruction(stack=reel.reel_number,
                                                                    x=reel.stack_x_offset,
                                                                    y=reel.stack_y_offset,
                                                                    comment=reel.comment))
            logging.info("Setting feed spacing for Reel {0}".format(reel_number))
            instructions.instructions.append(FeedSpacingInstruction(stack=reel.reel_number,
                                                                    feed_spacing=reel.feed_spacing))

        logging.info("Collecting all parts.")
        all_parts = []
        for reel_number in sorted(self.parts.keys()):
            for part in self.parts[reel_number]:
                if part.reel != reel_number:
                    logging.warning("Part reel number doesn't match the Reel reel number.")
                all_parts.append(part)

        for index, part in enumerate(all_parts):
            logging.info("Processing Part {0}".format(part.reference))
            total_rotation = part.rotation + self.get_reel_for_part(part).rotation
            instructions.instructions.append(PartPlacementInstruction(part_number=index+1,
                                                                      pickup_head=part.head,
                                                                      rotation=total_rotation,
                                                                      stack=part.reel,
                                                                      x=part.x,
                                                                      y=part.y,
                                                                      height=self.get_reel_for_part(part).height))
        return instructions


    def clear_parts(self):
        self.parts = {}

    def unassign_part_from_reel(self, part, reel_number):
        self.parts[reel_number].remove(part)

    def assign_part_to_reel(self, part, reel_number):
        part.reel = reel_number

        if reel_number not in self.reels:
            self.reels[reel_number] = Reel(reel_number)
        if reel_number not in self.parts:
            self.parts[reel_number] = [part]
        else:
            self.parts[reel_number].append(part)