import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warning import show_warning
from assvcPackage.stage import seeStaged
from assvcPackage.compare import compare
from assvcPackage.utils import find_assvc, get_ignore


def status():
    assvc_path = find_assvc()
    if assvc_path is None:
        show_warning(None, "Repository Error", "not an assvc repository (run `assvc start` first).")
        return
    listStaged = seeStaged(isPrint=False) or []
    listAll = compare("latest", False, False, True) or []
    listUnstaged = [x for x in listAll if x not in listStaged]
    print("\nStatus:")
    if listStaged:
        print("Staged files:")
        for f in listStaged:
            print(f" - {f}")
    else:
        print("No files are currently staged.")
    if listUnstaged:
        print("\nUnstaged files:")
        for f in listUnstaged:
            print(f" - {f}")
    else:
        print("\nNo unstaged changes.")

    return listStaged, listUnstaged
