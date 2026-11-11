import time
from itertools import zip_longest

import dir
from . import choose, chat, groups
from .misc import vague, assocs, react
from .colours import colAssoc
from .edit import edit_file

def sortk(hide, a):
    return (hide, len(a)*(-1 if hide else 1), a)

CATEGORIES = {
    's': ('System', 33),
    'n': ('Navigation', 34),
    'f': ('Editing', 32),
    '!': ('Short Fun', 36),
    '+': ('Longer Fun', 35),
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
    for c, (_, desc, _) in COMMANDS.items():
        chr = desc[0]
        if chr == '-':
            chr = desc[1]
            hide.add(c)
        cats[chr].append(c)
    cols = [[CATEGORIES[k][0], *sorted(cmds, key=lambda x: sortk(x in hide, x))] for k, cmds in cats.items()]
    colours = [CATEGORIES[k][1] for k in cats.keys()]
    mxwids = [max(len(i) for i in c) for c in cols]

    return "Commands: \033[37m(Less useful commands don't have colour)\033[0m\n"+'\n'.join(
        '   '.join(
            f'\033[{'1;3;4;' if cidx == 0 else ''}{37 if i in hide else colours[idx]}m{i.ljust(mxwids[idx])}\033[0m' for idx, i in enumerate(c)
        ) for cidx, c in enumerate(zip_longest(*cols, fillvalue=""))
    )

def helpargf(args):
    a = args[-1]
    if not a:
        return
    for c in sorted(COMMANDS.keys()):
        if c.startswith(a):
            return c

def repeatargf(args):
    if len(args) == 1:
        a = args[-1]
        for c in sorted(COMMANDS.keys()):
            if c.startswith(a):
                return c

def forcenoargs(a):
    if len(a) != 0:
        return "\033[91mToo many arguments!\033[0m"
    return None

def forcenumargs(fn, num=1, ignores=()):
    def fn2(args):
        if ignores:
            filt = [a for a in args if a not in ignores]
        else:
            filt = args
        if len(filt) == num+1 and filt[-1] == '':
            return
        if len(filt) > num:
            return "\3Too many arguments!"
        return fn(args)
    return fn2


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
        "sclear  Clear the display",
        False),
    "exit": (None, "sexit  Exit the terminal", False),

    # Navigation
    "pwd": ((lambda a: forcenoargs(a) or "  "+dir.nicePth()),
        "-npwd  Shows the path to the current directory",
        False),
    "ls": (dir.ls,
        "nls [path]...  List directory contents (without paths, uses the current directory)",
        dir.getpths),
    "cd": (dir.cd,
        "ncd <dir>  Change the current directory",
       forcenumargs(dir.getdirpths)),

    # Editing
    "rm": (dir.rm, "frm [-r] <path>...  Remove files (or directories with -r)", dir.getpths),
    "cp": (dir.cp, "fcp [-r] <src> <dst>  Copies a file (or directory with -r) from src to dst", forcenumargs(dir.getpths, 2, ('-r',))),
    "mv": (dir.mv, "fmv [-r] <src> <dst>  Moves a file (or directory with -r) from src to dst", forcenumargs(dir.getpths, 2, ('-r',))),
    "cat": (dir.cat, "-fcat <path>  Print the contents of a file", forcenumargs(dir.getpths)),
    "edit": (edit_file, "fedit <path>  Edit the contents of a file", forcenumargs(dir.getpths)),
    "touch": (dir.touch, "ftouch <path>...  Ensure files exist, creating them if not", dir.getpths),
    "mkdir": (dir.mkdir, "fmkdir [-p] <path>...  Create directories, with -p creates parents as well", dir.getdirpths),

    # Fun!
    "whoami": ((lambda a: forcenoargs(a) or "Whoever you want to be! <3"),
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
        "+chat [persona]...  Chat with different personas of yourself (opens editor if no personas given)",
        None),
    "choose": (choose.main,
        "+choose [option]...  Pick from options via 1v1 matches (opens editor if no options given)",
        None),
    "groups": (groups.main,
        "+groups [group]...  Place items in groups you make (opens editor if no groups given)",
        None),
}
