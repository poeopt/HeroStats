import sys
from src.utils.single_instance import ensure_single_instance, release

if not ensure_single_instance():
    sys.exit(0)

from src import run
from src.engine.logger import _init_logger
_init_logger()

try:
    run()
finally:
    release()
