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

def read_key():
    """Returns a single character, or a name like 'up', 'cleft', 'bs', 'cbs'."""
    ch = getch()
    if isinstance(ch, bytes): # Windows
        if ch in (b"\x00", b"\xe0"):
            return {
                b"H": "up", b"P": "down", b"K": "left", b"M": "right",
                b"s": "cleft", b"t": "cright", b"S": "del"
            }.get(getch(), "")
        ch = ch.decode(errors="ignore")
        return {"\x08": "bs", "\x7f": "cbs"}.get(ch, ch)
    if ch == "\x1b" and getch() == "[": # Unix arrow keys etc.
        seq = ""
        while not (seq[-1:].isalpha() or seq[-1:] == "~"):
            seq += getch()
        return {
            "A": "up", "B": "down", "C": "right", "D": "left",
            "1;5C": "cright", "1;5D": "cleft", "3~": "del"
        }.get(seq, "")
    return {"\x7f": "bs", "\x08": "cbs"}.get(ch, ch)
