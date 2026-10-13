import os
import sys

# make `import rfcalc` work when pytest is run from anywhere
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
