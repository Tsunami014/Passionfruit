import os
import difflib
from cmds import COMMANDS
from read import read_key, WrapPrinter
import dir
import re

os.chdir(os.path.abspath(os.path.join(__file__, "..")))
os.system("")  # lets Windows terminals understand ANSI escape codes

PARSE_CMD_RE = re.compile(r'"((?:\\\\|\\"|[^"])+)"|([^ ]+)')
def parse_cmd(buf):
    return [it for m in PARSE_CMD_RE.finditer(buf) for it in m.groups() if it is not None]

print("Run 'help' for a list of all posible commands")
history = []
while True:
    buf = ""
    pos = 0
    h = len(history)
    wp = WrapPrinter()
    while True:
        suggest = ''
        fail = False
        if s := buf.lstrip():
            cmd, *args = parse_cmd(s)
            if cmd in COMMANDS:
                desc = COMMANDS[cmd][1].lstrip('-')[1:]
            else:
                desc = "Unknown command!"
                fail = True
            if pos == len(buf):
                if s[-1] == ' ' or len(args) > 0:
                    if not fail:
                        argopts = COMMANDS[cmd][2]
                        if argopts is False:
                            if len(args) != 0:
                                desc = "Too many arguments!"
                                fail = True
                        elif argopts is not None:
                            xtra = len(args) == 0 or s[-1] == ' '
                            curarg = "" if xtra else args[-1]
                            out = argopts(len(args)+int(xtra)-1, curarg)
                            if out and out[0] == '\3':
                                desc = out
                                fail = True
                            else:
                                suggest = (out or '')[len(curarg):]
                else:
                    for c in sorted(COMMANDS.keys()):
                        if c.startswith(cmd):
                            suggest = c[len(cmd):]
                            break
        else:
            desc = None
        col = f"\033[{91 if fail else (95 if desc is not None else 37)}m"
        command = (
            f"\033[92m{dir.PTH}\033[0m {col}$\033[0m "
            f"{buf[:pos]}\5{buf[pos:]}\033[37m{suggest}\033[0m"
        )
        suff = f"\n{' '*(3+len(dir.PTH))}{col}└─ "+desc if desc is not None else "\n"
        wp(command+suff, end="")
        k = read_key()
        if k in ("\r", "\n"):
            wp(command.replace('\5', '', 1))
            break
        elif k == "\x03": # Ctrl+C
            wp(command.replace('\5', '^C', 1))
            buf = ""
            break
        elif k == "\x04": # Ctrl+D
            wp(command.replace('\5', '^D', 1))
            buf = "exit"
            break
        elif k == "\t":
            if suggest:
                buf += suggest
                pos = len(buf)
        elif k == "bs" and pos:
            buf, pos = buf[:pos - 1] + buf[pos:], pos - 1
        elif k == "del":
            buf = buf[:pos] + buf[pos + 1:]
        elif k in ("cbs", "cleft"): # jump / delete back one word
            i = pos
            while i and buf[i - 1] == " ":
                i -= 1
            while i and buf[i - 1] != " ":
                i -= 1
            buf, pos = (buf[:i] + buf[pos:], i) if k == "cbs" else (buf, i)
        elif k == "cright":
            while pos < len(buf) and buf[pos] == " ":
                pos += 1
            while pos < len(buf) and buf[pos] != " ":
                pos += 1
        elif k == "left":
            pos = max(0, pos - 1)
        elif k == "right":
            pos = min(len(buf), pos + 1)
        elif k == "up" and h:
            h -= 1
            buf = history[h]
            pos = len(buf)
        elif k == "down" and h < len(history):
            h += 1
            buf = history[h] if h < len(history) else ""
            pos = len(buf)
        elif len(k) == 1 and k.isprintable():
            buf, pos = buf[:pos] + k + buf[pos:], pos + 1


    buf = buf.strip()
    if not buf:
        continue
    cmd, *args = parse_cmd(buf)
    if cmd == "exit":
        break
    history.append(buf)

    try:
        repeated = False
        if cmd == "repeat":
            if len(args) == 0:
                print("\033[91mNo command provided!\033[0m")
            elif args[0] not in COMMANDS:
                cmd = args[0] # To make it error below with that as the command
            else:
                fn = COMMANDS[args[0]][0]
                args = args[1:]
                if out := fn(args):
                    print(out)
                if fn.__code__.co_argcount > 1:
                    nfn = lambda a: fn(a, False)
                else:
                    nfn = fn
                while True:
                    if out := nfn(args):
                        print(out)

        if not repeated:
            if cmd in COMMANDS:
                if out := COMMANDS[cmd][0](args):
                    print(out)
            else:
                print("  Command not found:\033[1m",cmd, end="\033[0m\n")
                closest = difflib.get_close_matches(cmd, COMMANDS.keys(), n=1, cutoff=0.6)
                if closest:
                    print("  Did you mean:\033[1m", closest[0], end="\033[0m\n")
                else:
                    print("  Run 'help' for a list of all posible commands")
    except (KeyboardInterrupt, EOFError):
        pass
