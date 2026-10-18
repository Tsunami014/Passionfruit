from .edit import edit_file
from read import newinp, WrapPrinter
from random import choice, randint
import dir
import re

NAME_RE = re.compile(r'^\s*(.+?)\s*(?:\(([^()]+)\)\s*)?$')
PERSONAS_FILE = '/personas.txt'
COLS = [166, 209, 220, 112, 37, 69, 63, 98, 169]
def main(personas, init=True):
    with open('data/convtopics.txt') as f:
        TOPICS = [o for i in f.readlines() if (o := i[:-1])]

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
            args = args.strip()
            match cmd.lower():
                case "help"|"h":
                    inf = """
\\what  If you are confused about what this is (\\w)
\\switch <name>  Switches persona to <name> (\\s)
\\list  Lists all personas (\\l)
\\hint  Some info that may help make using this easier (\\h)
\\topic  Get suggested a random topic of conversation (\\t)
\\col [col]  Switch colour scheme for future messages (randomly, or to provided number) (\\c)
"""[1:-1]
                case "what"|"w":
                    inf = """
This is for you to chat with different 'personas' of yourself!
They could be anything, e.g. "happiness", "anger", or even just random names you like.
The aim is to role-play as the persona of yourself.
You can use this just for fun, or use some of the questions in \\topic (or think of your own questions) to have a chat with yourself about yourself!
"""[1:-1]
                case "col"|"c":
                    if args:
                        try:
                            offs = int(args)
                        except ValueError:
                            fail = True
                            inf = f"Input not a number: '{args}'!"
                    else:
                        offs = randint(0, len(COLS)-1)
                case "list"|"l":
                    inf = "\n".join(personas)
                case "switch"|"s":
                    idx = name_lookup.get(args.lower(), None)
                    if idx is None:
                        fail = True
                        inf = f"Unknown persona '{args}'! Try running \\list"
                    else:
                        per = idx
                case "topic"|"t":
                    inf = choice(TOPICS)
                case "hint"|"h":
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
