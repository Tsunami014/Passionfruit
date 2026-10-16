import os
import difflib
from cmds import COMMANDS
from read import read_key

os.system("")  # lets Windows terminals understand ANSI escape codes


print("Run 'help' for a list of all posible commands")
history = []
pth = '/'
while True:
    buf = ""
    pos = 0
    h = len(history)
    while True:
        suggest = None
        if s := buf.strip():
            cmd = s.split(' ')[0]
            desc = COMMANDS[cmd][1][1:] if cmd in COMMANDS else None
            if pos == len(buf):
                for c in sorted(COMMANDS.keys()):
                    if c.startswith(cmd):
                        suggest = c
                        break
        else:
            desc = ""
        sugtxt = suggest[len(s):] if suggest else ''
        col = f"\033[{91 if desc is None else (95 if desc else 37)}m"
        print(
            (f"\n{' '*(3+len(pth))}{col}└─ {desc if desc is not None else "unknown command"}" if desc != "" else "\n")+
            "\033[K\033[0m\033[1A\r"
            f"\033[92m{pth}\033[0m {col}$\033[0m "
            f"{buf}\033[37m{sugtxt}\033[0m\033[K{'\b'*(len(buf) - pos + len(sugtxt))}",
        end="", flush=True)
        k = read_key()
        if k in ("\r", "\n"):
            print()
            break
        elif k == "\x03": # Ctrl+C
            buf = ""
            pos = 0
            h = len(history)
            print("^C")
        elif k == "\x04": # Ctrl+D
            print("^D")
            buf = "exit"
            break
        elif k == "\t":
            if suggest:
                buf = suggest
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


    print(end="\033[2K")
    if buf.strip() == "exit":
        break
    if not buf.strip():
        continue
    history.append(buf)
    cmd, *args = buf.split()
    if cmd in COMMANDS:
        out = COMMANDS[cmd][0](pth, args)
        if out:
            print(out)
    else:
        print("  Command not found:\033[1m",cmd, end="\033[0m\n")
        closest = difflib.get_close_matches(cmd, COMMANDS.keys(), n=1, cutoff=0.6)
        if closest:
            print("  Did you mean:\033[1m", closest[0], end="\033[0m\n")
        else:
            print("  Run 'help' for a list of all posible commands")
