import sys
from tm2x0.kicad import KicadPartPositions

from contextlib import contextmanager
from StringIO import StringIO

@contextmanager
def captured_output():
    """capture_output is a context manager, useful with 'with', for testing standard output.

    This is from:
    https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python"""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
