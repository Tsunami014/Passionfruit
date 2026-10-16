import time
from itertools import zip_longest

from .misc import assocs

def sortk(a):
    return (len(a), a)

CATEGORIES = {
    's': ('System', 33),
    'n': ('Navigation', 32),
    'f': ('Files', 34),
    '!': ('Fun', 35),
}

def help(*_):
    cats = {k: [] for k in CATEGORIES}
    for c, (_, desc) in COMMANDS.items():
        cats[desc[0]].append(c)
    cols = [[CATEGORIES[k][0], *sorted(cmds, key=sortk)] for k, cmds in cats.items()]
    colours = [CATEGORIES[k][1] for k in cats.keys()]
    mxwids = [max(len(i) for i in c) for c in cols]

    return "Commands:\n"+'\n'.join(
        '   '.join(
            f'\033[{'1;3;4;' if cidx == 0 else ''}{colours[idx]}m{i.ljust(mxwids[idx])}\033[0m' for idx, i in enumerate(c)
        ) for cidx, c in enumerate(zip_longest(*cols, fillvalue=""))
    )

COMMANDS = {
    # System
    "help": (help, "sPrint every command"),
    "echo": ((lambda _, a: " ".join(a)),
        "sEchoes text"),
    "date": ((lambda *_: time.strftime("%a %b %d %H:%M:%S %Y")),
        "sShow the current date and time"),
    "clear": ((lambda *_: print("\x1b[2J\x1b[H", end="")),
        "sClear the display"),
    "exit": (None, "sExit the terminal"),

    # Navigation
    "pwd": ((lambda d, _: "  "+d),
        "nShows the path to the current directory"),
    "ls": ((lambda d, a: "documents  downloads  TODO.txt  pictures"),
        "nList the contents of the current directory"),
    "cd": ((lambda d, a: "TODO"),
        "nChange the current directory"),
    "rm": ((lambda d, a: "TODO"),
        "nRemove a file"),

    # Files
    "cp": ((lambda d, a: "TODO"),
        "fCopy a file"),
    "mv": ((lambda d, a: "TODO"),
        "fMove or rename a file"),
    "cat": ((lambda d, a: "TODO"),
        "fDisplay the contents of a file"),
    "edit": ((lambda d, a: "TODO"),
        "fEdit the contents of a file"),

    # Fun!
    "whoami": ((lambda *_: "Whoever you want to be"),
        "!Show who you are logged in as"),
    "associations": (assocs,
        "!Write down the first thing that comes to your mind"),
}
