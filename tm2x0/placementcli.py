import logging
from operator import attrgetter
import traceback
import sys

AUTOSET = {"0402": [("feed_spacing", "2.0"),
                    ("stack_x_offset", "0.0"),
                    ("stack_y_offset", "0.05"),
                    ("comment", "0402")],
           "0603": [("feed_spacing", "4.0"),
                    ("stack_x_offset", "-0.04"),
                    ("stack_y_offset", "-0.1"),
                    ("comment", "0603")],
           "0805": [("feed_spacing", "4.0"),
                    ("stack_x_offset", "0.05"),
                    ("stack_y_offset", "0"),
                    ("comment", "0805")],
           "1206": [("feed_spacing", "4.0"),
                    ("stack_x_offset", "0.23"),
                    ("stack_y_offset", "0"),
                    ("comment", "1206")],
}


def get_int(prompt):
    value = raw_input(prompt)

    while True:
        try:
            value = int(value)
        except ValueError:
            value = raw_input(prompt)
        else:
            return value


def get_input(prompt, values=None):
    value = raw_input(prompt)
    if values:
        while value not in values:
            value = raw_input(prompt)
        return value


def choose(title, prompt, choices):
    print title
    for i, pair in enumerate(choices):
        key, _ = pair
        print "\t{0}) {1}".format(i + 1, key)
    index = get_input(prompt, [str(n) for n in range(1, len(choices) + 1)])
    index = int(index)
    index -= 1
    return choices[index][1]


class PlacementCLI():
    def __init__(self,
                 placement,
                 unassigned_parts=None,
                 output_filename=None):
        self.placement = placement
        self.unassigned_parts = unassigned_parts
        self.output_filename = output_filename

    def print_reels(self):
        out = []
        if not self.placement.parts.keys():
            return ""
        out.append("Reels with Parts:")
        for reel_number in sorted(self.placement.parts.keys()):
            out.append("\tReel {0} ({1})".format(reel_number,
                                                 ", ".join(
                                                     [part.reference for part in
                                                      self.placement.parts[reel_number]]
                                                 )))
        return "\n".join(out)

    def _assign_part_to_reel(self):
        print self.print_reels()

        choices = []
        for i, part in enumerate(self.unassigned_parts):
            key = "{0} ({1})".format(part, part.reference)
            choices.append((key, i))
        choices.append(("Back", "back"))

        part_index = choose("Unassigned Parts:",
                            "Which part would you like to assign to a reel? ",
                            choices)
        print part_index
        if part_index == "back":
            return True

        part = self.unassigned_parts[part_index]

        reel_index = get_int(
            "Which reel would you like to assign part {0} to? (0 is tray, 1 is closest to front, ...) " \
            .format(part))

        self.placement.assign_part_to_reel(part, reel_index)
        del self.unassigned_parts[part_index]


    def assign_parts_to_reels(self):
        print "Assigning Parts to Reels:"
        back = False
        while self.unassigned_parts and not back:
            back = self._assign_part_to_reel()
        if not self.unassigned_parts:
            print "All parts have been assigned to reels."


    def run(self):
        while True:
            print "PNP CSV Manipulation:"
            choices = []
            if self.unassigned_parts:
                print "Unassigned Parts:"
                for part in self.unassigned_parts:
                    print "\t{0} ({1})".format(part, part.reference)
                choices.append(("Assign Parts to Reels", self.assign_parts_to_reels))

            if self.placement.reels:
                print "Reels:"
                for reel_number in self.placement.reels:
                    print "\tReel {0}".format(reel_number)
                choices.append(("Configure Reels", self.configure_reels))
            if not choices:
                print "Without parts to assign or reels to configure, we can't really do anything!"
                return
            else:
                choices.append(("Save to file", self.export))
            choice = choose("Choose an option:",
                            '? ',
                            choices)
            return_val = choice()
            if choice == self.export and return_val:
                return


    def autoset_reel(self, reel_number):
        reel = self.placement.reels[reel_number]

        footprint_choices = sorted([name for name in AUTOSET])
        footprint_choices = [(name, name) for name in footprint_choices]
        footprint_choices.append(("Back", "back"))
        footprint_choice = choose("Autoset Parameters",
                                  "Which configuration would you like to copy? ",
                                  footprint_choices)
        if footprint_choice == "back":
            return
        else:
            for attr, val in AUTOSET[footprint_choice]:
                reel.__dict__[attr] = val

        if reel.reel_number == 0:
            print "Because this is on Reel 0 (the tray), the feed spacing has been autoset to 18 mm."
            reel.feed_spacing = 18


    def describe_reel_configuration(self, reel):
        out = []
        out.append("Reel {0} is configured as follows:".format(reel.reel_number))
        out.append("\tFeed Spacing (mm): {0}".format(reel.feed_spacing))
        out.append("\tPart X Offset (mm): {0}".format(reel.stack_x_offset))
        out.append("\tPart Y Offset (mm): {0}".format(reel.stack_y_offset))
        out.append("\tPart Height (mm): {0}".format(reel.height))
        out.append("\tExtra Rotation (degrees, positive is counter-clockwise): {0}".format(reel.rotation))
        out.append("\tComment: {0}".format(reel.comment))
        parts = ", ".join(
            [part.reference for part in self.placement.get_parts_sorted_by_reference(reel.reel_number)])
        if not parts:
            parts = None
        out.append("\tParts: {0}".format(parts))

        return "\n".join(out)

    def configure_reels(self):
        done = False
        while not done:
            for reel in sorted(self.placement.reels.values(), key=attrgetter("reel_number")):
                print self.describe_reel_configuration(reel)

            reel_number = None
            while reel_number not in self.placement.reels.keys() and reel_number != "f":
                prompt = "Which reel would you like to configure? ["
                prompt_values = ", ".join([str(key) for key in sorted(self.placement.reels.keys())])
                if prompt_values:
                    prompt += prompt_values
                    prompt += ", "
                prompt += "(f)inished] "
                reel_number = raw_input(prompt)
                if reel_number == "f":
                    done = True
                    continue
                try:
                    reel_number = int(reel_number)
                except ValueError:
                    pass

            if reel_number == "f":
                return

            reel_to_configure = self.placement.reels[reel_number]
            finished_configuring_reel = False
            while not finished_configuring_reel:
                print self.describe_reel_configuration(reel_to_configure)
                print
                choices = [("Autoset parameters", "autoset"),
                           ("Feed Spacing", "feed_spacing"),
                           ("Part X Offset", "stack_x_offset"),
                           ("Part Y Offset", "stack_y_offset"),
                           ("Height", "height"),
                           ("Rotation", "rotation"),
                           ("Comment", "comment")]
                if self.placement.parts[reel_to_configure.reel_number]:
                    choices.append(("Unassign a Part", "remove_parts"))
                choices.append(("Back", "back"))
                choice = choose("Configure Reel",
                                "Which parameter would you like to set? ",
                                choices)
                if choice == "back":
                    finished_configuring_reel = True
                    continue
                elif choice == "autoset":
                    self.autoset_reel(reel_to_configure.reel_number)
                elif choice == "remove_parts":
                    part_choices = [("{0} ({1})".format(part, part.reference), part)
                                    for part in self.placement.parts[reel_to_configure.reel_number]]
                    part_choices.append(("Back", "back"))
                    part_to_remove = choose("Part Unassignment:",
                                            "Which part would you like to remove from Reel {0}? ".format(
                                                reel_to_configure.reel_number),
                                            part_choices)
                    if part == "back":
                        continue
                    else:
                        self.placement.unassign_part_from_reel(part, reel_to_configure.reel_number)
                        self.unassigned_parts.append(part)
                else:
                    self.placement.reels[reel_to_configure.reel_number].__dict__[choice] = raw_input(
                        "Enter the new value: ")

    def export(self):
        try:
            output = self.placement.generate_instructions().to_csv()
        except Exception, e:
            logging.error("Error while creating instructions from configuration.")
            print traceback.print_exc(file=sys.stdout)
            return False

        if self.output_filename:
            try:
                with open(self.output_filename, 'w') as f:
                    f.write(output)
                    return True
            except:
                print "There was an error writing the output file."
                print "Because there was an error, you may want to verify this."
                print output
                return False
        else:
            print output
            return True