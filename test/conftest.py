import pathlib
import sys

# Add the wadas directory to the sys.path in order to be able to import the modules.
__this_dir = pathlib.Path(__file__).absolute().parent
sys.path.append(str(__this_dir.parent))
