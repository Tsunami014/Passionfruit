from .edit import edit_file
from read import newinp, WrapPrinter
from random import randint
import dir
import re

NAME_RE = re.compile(r'^\s*(.+?)\s*(?:\(([^()]+)\)\s*)?$')
PERSONAS_FILE = '/personas.txt'
COLS = [166, 209, 220, 112, 37, 69, 63, 98, 169]
def main(personas, init=True):
    if not personas:
        edit_file((PERSONAS_FILE,), extra="\nPut all personas on new lines")
        items = dir.cat((PERSONAS_FILE,))
        if items is None:
            return
        personas = items.split('\n')

    personas = [t for i in personas if (t := i.strip())]
    if len(personas) == 0:
        print("\033[91mNo items!\033[0m")
        return

    name_lookup = {
        nam.lower(): idx for idx, it in enumerate(personas) for m in NAME_RE.finditer(it) for nam in m.groups() if nam is not None
    }
    names = [NAME_RE.match(it).group(1) for it in personas]

    if init:
        print("\033[37m\\help to list commands\033[0m")
    per = 0
    wp = WrapPrinter()
    pref = ""
    offs = randint(0, len(COLS)-1)
    while True:
        prompt = f"\033[1;38;5;{COLS[(per+offs)%len(COLS)]}m{names[per]} > \033[0m"
        inp = newinp(pref+prompt, wp)
        if inp.startswith('\\'):
            fail = False
            inf = ""
            cmd, _, args = inp[1:].partition(' ')
            match cmd.lower():
                case "help":
                    inf = """
\\switch <name>  Switches persona to <name>
\\list  Lists all personas
\\hint  Get a hint to make your life easier
"""[1:-1]
                case "list":
                    inf = "\n".join(personas)
                case "switch":
                    idx = name_lookup.get(args, None)
                    if idx is None:
                        fail = True
                        inf = f"Unknown persona '{args}'! Try running \\list"
                    else:
                        per = idx
                case "hint":
                    inf = """
You can end a name with (nickname) and use the nickname when switching to switch faster!
This can even be one letter long to make it very fast!
"""[1:-1]
                case _:
                    fail = True
                    inf = f"Unknown command '\\{cmd}'! Try running \\help"
            pref = f'\033[{31 if fail else 36}m{inf}\033[0m\n' if inf else ''
        else:
            wp(prompt+inp)
            wp = WrapPrinter()
            pref = ""
