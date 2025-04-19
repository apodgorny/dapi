# bootstrap.py
import sys
from pathlib import Path

def bootstrap(levels_up=0):
	current_file = Path(__file__).resolve()
	project_root = current_file.parents[levels_up]
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))
