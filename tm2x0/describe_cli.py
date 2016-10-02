from tm2x0.placement import PlacementInstructions

import sys
import argparse
import logging


def parse_command_line(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--placement-file",
                        required=True,
                        help="Placement file")
    arguments = parser.parse_args(argv[1:])
    return arguments


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(name)s (%(levelname)s): %(message)s')
    try:
        arguments = parse_command_line(sys.argv)
        with open(arguments.placement_file) as f:
            placement_instructions = PlacementInstructions.from_file(f)
        print placement_instructions.describe()
    finally:
        logging.shutdown()

if __name__ == "__main__":
    main()