import time
from itertools import zip_longest

import dir
from . import choose, chat
from .misc import vague, assocs, react
from .colours import colAssoc
from .edit import edit_file

def sortk(a):
    return (len(a), a)

CATEGORIES = {
    's': ('System', 33),
    'n': ('Navigation', 32),
    '!': ('Fun', 35),
}

def help(a):
    if a:
        for cmd in a:
            if cmd in COMMANDS:
                print(COMMANDS[cmd][1].lstrip('-')[1:])
            else:
                print("\033[91mCommand does not exist:\033[0m", cmd)
        return
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

def helpargf(_, last):
    for c in sorted(COMMANDS.keys()):
        if c.startswith(last):
            return c

def repeatargf(idx, last):
    if idx == 0:
        for c in sorted(COMMANDS.keys()):
            if c.startswith(last):
                return c

def forcenoargs(a):
    if len(a) != 0:
        return "\033[91mToo many arguments!\033[0m"
    return None

# Commands are (function, description, arg func|None (any args allowed)|False (no args allowed))
COMMANDS = {
    # System
    "help": (help,
        "shelp [cmd]...  Show help for all/specified commands",
        helpargf),
    "echo": ((lambda a: ' '.join(a)),
        "-secho [text]...  Prints text",
        None),
    "repeat": (None,
        "srepeat <cmd> [arg]...  Repeat a command until Ctrl+C",
        repeatargf),
    "date": ((lambda a: forcenoargs(a) or time.strftime("%a %b %d %H:%M:%S %Y")),
        "-sdate  Show the current date and time",
        False),
    "clear": ((lambda a: forcenoargs(a) or print("\x1b[2J\x1b[H", end="")),
        "-sclear  Clear the display",
        False),
    "exit": (None, "sexit  Exit the terminal", False),

    # Navigation
    "pwd": ((lambda a: forcenoargs(a) or "  "+dir.PTH),
        "-npwd  Shows the path to the current directory",
        False),
    "ls": (dir.ls,
        "nls [path]...  List the contents of the current directory",
        dir.getpths),
    "cd": ((lambda _: "Nowhere to go!"),
        "-ncd <dir>  Change the current directory",
        dir.getpths),
    "rm": (dir.rm, "nrm <path>...  Remove a file", dir.getpths),
    "cat": (dir.cat, "ncat <path>  Print the contents of a file", dir.getpths),
    "edit": (edit_file, "nedit <path>  Edit the contents of a file", dir.getpths),

    # Fun!
    "whoami": ((lambda a: forcenoargs(a) or "Whoever you want to be"),
        "-!whoami  Show who you are logged in as",
        False),
    "vague": (vague,
        "!vague  Come up with concrete amounts of vague quantities",
        False),
    "colassoc": (colAssoc,
        "!colassoc  Come up with colours for words",
        False),
    "assocs": (assocs,
        "!assocs  Write down the first thing that comes to your mind",
        False),
    "react": (react,
        "!react  Agree/disagree to statements as fast as you can",
        False),
    "chat": (chat.main,
        "!chat [persona]...  Chat with different personas (opens editor if no personas given)",
        None),
    "choose": (choose.main,
        "!choose [option]...  Pick from options via 1v1 matches (opens editor if no options given)",
        None),
}
