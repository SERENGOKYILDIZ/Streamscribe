# StreamScribe Source Package
import sys
from pathlib import Path

# Automatically ensure 'src' is in sys.path
_SRC_DIR = str(Path(__file__).resolve().parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
