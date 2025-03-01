"""Insert the project root dir and the lib sub-path into PYTHONPATH for easier importing."""

# pylint: disable=C0413,W0611
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if ROOT_DIR not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

sys.path.insert(0, str(Path(__file__).resolve().parent))
