from tm2x0.instructions import PlacementInstructions
from tm2x0.kicad import KicadPartPositions
from tm2x0.placement import Placement
from tm2x0.placementcli import PlacementCLI

import sys
import argparse
import logging


def parse_command_line(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--kicad-file",
                        required=True,
                        help=".pos file from KiCad to convert")
    parser.add_argument("--side",
                        default="front",
                        help="Set the side to convert.  Defaults to front.  Can be either front or back.")
    parser.add_argument("--reels-from",
                        dest="csv_file",
                        help="Load reel configurations from CSV file")
    parser.add_argument("--output-file",
                        dest="output_filename",
                        help="File to store the CSV output")
    arguments = parser.parse_args(argv[1:])

    if arguments.side not in ["front", "back"]:
        raise argparse.ArgumentError('Side must be either "front" or "back"')

    # check input files
    for attribute in ("kicad_file", "csv_file"):
        if arguments.__dict__[attribute]:
            try:
                with open(arguments.__dict__[attribute]) as fh:
                    pass
            except IOError:
                logging.error("Issue opening input file {0}".format(arguments.__dict__[attribute]))
                raise

    return arguments

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='(%(levelname)s): %(message)s')
    try:
        arguments = parse_command_line(sys.argv)
        with open(arguments.kicad_file) as kicad_handle:
            if arguments.csv_file:
                try:
                    csv_handle = open(arguments.csv_file)
                    instructions = PlacementInstructions.from_file(csv_handle)
                    p = Placement.from_instructions(instructions)
                    csv_handle.close()
                except IOError:
                    raise
            else:
                p = Placement()

            kicad_parts = KicadPartPositions.from_file(kicad_handle)

            if arguments.side == "front":
                side = "Front"
            elif arguments.side == "back":
                side = "Back"
            else:
                raise Exception("Unknown side")

            p.clear_parts()

            cli = PlacementCLI(placement=p,
                               unassigned_parts=kicad_parts.instructions[side],
                               output_filename=arguments.output_filename)
            cli.run()

    finally:
        logging.shutdown()


if __name__ == "__main__":
    main()