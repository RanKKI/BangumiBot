import importlib
import os
from pathlib import Path
import sys
from typing import List


def dynamic_get_class(filepath: Path, classes: List[str]):
    cur = os.getcwd()
    os.chdir(filepath)  # change working directory so we know import will work
    filepath, module_name = os.path.split(filepath)
    sys.path.append(filepath)

    module = __import__(module_name)

    ret = [getattr(module, cls) for cls in classes]
    os.chdir(cur)
    return ret
