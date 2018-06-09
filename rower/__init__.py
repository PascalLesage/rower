__all__ = [
    "Rower",
    "RowerDatapackage",
    "DATAPATH",
    "DEFAULT_EXCLUSIONS",
    "USERPATH"
]

__version__ = (0, 1)

import appdirs
import os

DATAPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
USERPATH = os.path.abspath(appdirs.user_data_dir("rower", "pylca"))

if not os.path.isdir(USERPATH):
    os.makedirs(USERPATH)

from .data_package import RowerDatapackage
from .base import Rower, DEFAULT_EXCLUSIONS
