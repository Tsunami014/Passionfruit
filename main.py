import os, time

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
os.system("")  # lets Windows terminals understand ANSI escape codes


def read_key():
    """Returns a single character, or a name like 'up', 'cleft', 'bs', 'cbs'."""
    ch = getch()
    if isinstance(ch, bytes): # Windows
        if ch in (b"\x00", b"\xe0"):
            return {b"H": "up", b"P": "down", b"K": "left", b"M": "right",
                    b"s": "cleft", b"t": "cright", b"S": "del"
            }.get(getch(), "")
        ch = ch.decode(errors="ignore")
        return {"\x08": "bs", "\x7f": "cbs"}.get(ch, ch)
    if ch == "\x1b" and getch() == "[": # Unix arrow keys etc.
        seq = ""
        while not (seq[-1:].isalpha() or seq[-1:] == "~"):
            seq += getch()
        return {"A": "up", "B": "down", "C": "right", "D": "left",
                "1;5C": "cright", "1;5D": "cleft", "3~": "del"
        }.get(seq, "")
    return {"\x7f": "bs", "\x08": "cbs"}.get(ch, ch)

def readline(prompt, history):
    buf = ""
    pos = 0
    h = len(history)
    while True:
        print(f"\r{prompt}{buf}\x1b[K{'\b'*(len(buf) - pos)}", end="", flush=True)
        k = read_key()
        if k in ("\r", "\n"):
            print()
            return buf
        elif k == "\x03": # Ctrl+C
            buf = ""
            pos = 0
            h = len(history)
            print("^C")
        elif k == "\x04": # Ctrl+D
            print()
            return None
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


COMMANDS = {
    "help":   lambda a: "Commands: help, echo, date, whoami, ls, clear, exit",
    "echo":   lambda a: " ".join(a),
    "date":   lambda a: time.strftime("%a %b %d %H:%M:%S %Y"),
    "whoami": lambda a: "guest",
    "ls":     lambda a: "documents  downloads  notes.txt  pictures",
    "clear":  lambda a: print("\x1b[2J\x1b[H", end="") or "",
}

history = []
while True:
    line = readline("guest@pretend:~$ ", history)
    if line is None or line.strip() == "exit":
        break
    if not line.strip():
        continue
    history.append(line)
    cmd, *args = line.split()
    out = COMMANDS[cmd](args) if cmd in COMMANDS else f"{cmd}: command not found"
    if out:
        print(out)
