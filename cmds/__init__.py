import time
from itertools import zip_longest

import dir
from .misc import vague, assocs, react
from .colours import colAssoc

def sortk(a):
    return (len(a), a)

CATEGORIES = {
    's': ('System', 33),
    'n': ('Navigation', 32),
    '!': ('Fun', 35),
}

def help(*_):
    cats = {k: [] for k in CATEGORIES}
    hide = set()
    for c, (_, desc) in COMMANDS.items():
        chr = desc[0]
        if chr == '-':
            chr = desc[1]
            hide.add(c)
        cats[chr].append(c)
    cols = [[CATEGORIES[k][0], *sorted(cmds, key=lambda x: (x in hide, *sortk(x)))] for k, cmds in cats.items()]
    colours = [CATEGORIES[k][1] for k in cats.keys()]
    mxwids = [max(len(i) for i in c) for c in cols]

    return "Commands: \033[37m(Less useful commands are in grey)\033[0m\n"+'\n'.join(
        '   '.join(
            f'\033[{'1;3;4;' if cidx == 0 else ''}{37 if i in hide else colours[idx]}m{i.ljust(mxwids[idx])}\033[0m' for idx, i in enumerate(c)
        ) for cidx, c in enumerate(zip_longest(*cols, fillvalue=""))
    )

COMMANDS = {
    # System
    "help": (help, "sPrint every command"),
    "echo": ((lambda a: ' '.join(a)),
        "-sEchoes text"),
    "repeat": (None, "sRepeat a command until Ctrl+C"),
    "date": ((lambda _: time.strftime("%a %b %d %H:%M:%S %Y")),
        "-sShow the current date and time"),
    "clear": ((lambda _: print("\x1b[2J\x1b[H", end="")),
        "-sClear the display"),
    "exit": (None, "sExit the terminal"),

    # Navigation
    "pwd": ((lambda _: "  "+dir.PTH),
        "-nShows the path to the current directory"),
    "ls": (dir.ls, "nList the contents of the current directory"),
    "cd": ((lambda _: "Nowhere to go!"),
        "-nChange the current directory"),
    "rm": (dir.rm, "nRemove a file"),
    "edit": (dir.edit, "nEdit the contents of a file"),

    # Fun!
    "whoami": ((lambda _: "Whoever you want to be"),
        "-!Show who you are logged in as"),
    "vague": (vague,
        "!Come up with concrete amounts of vague quantities"),
    "colassoc": (colAssoc,
        "!Come up with colours for words"),
    "assocs": (assocs,
        "!Write down the first thing that comes to your mind"),
    "react": (react,
        "!Agree/disagree to statements as fast as you can"),
}
