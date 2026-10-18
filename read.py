import builtins
import shutil
import math
import re

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
        import sys
        import tty

    def __call__(self):
        import termios
        import sys
        import tty
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

def wait(*prints, wait_for='\r\n'):
    if prints:
        print(*prints, end="", flush=True)
    while True:
        k = read_key()
        if len(k) == 1 and k in wait_for:
            return k
        elif k == "\x03": # Ctrl+C
            print("^C")
            raise KeyboardInterrupt
        elif k == "\x04": # Ctrl+D
            print("^D")
            raise EOFError

WP_Repl_Re = re.compile(r'\033\[[0-9;]+m')
class WrapPrinter:
    """Prints multiple lines of text and remembers how much they wrapped.
    \5 inserts the cursor at that position.
    This only works if this is the last thing being printed, there are no ansi in the text apart from colours, and there is no text on the same line as where this starts.
    This handles clearing old text, no need for you to do that manually
    """
    def __init__(self):
        self.oldtxt = ""

    @staticmethod
    def _getlndiff(txt, curidx, mxwid):
        lastnl = txt.rfind('\n', 0, curidx)
        col = (curidx-lastnl-1) % mxwid
        lndiff = -1
        for ln in txt[curidx-col:].replace('\5', '', 1).split('\n'):
            lndiff += max(math.ceil(len(ln)/mxwid), 1)
        return lndiff, col

    def __call__(self, *parts, end="\n"):
        mxwid = shutil.get_terminal_size().columns
        if (cursidx := self.oldtxt.rfind('\5')) != -1:
            lndiff, _ = self._getlndiff(self.oldtxt, cursidx, mxwid)
            lndiff = -1-lndiff
        else:
            if (lastln := len(self.oldtxt) - self.oldtxt.rfind('\n') - 1) > 0:
                lndiff = int(lastln % mxwid == 0)-1
            else:
                lndiff = -1

        for ln in self.oldtxt.replace('\5', '', 1).split('\n'):
            lndiff += max(math.ceil(len(ln)/mxwid), 1)

        up = '' if lndiff <= 0 else f'\033[{lndiff}A'
        pref = up+'\r\033[J'

        ntxt = ' '.join(parts)+end
        ntxt = ntxt.replace('\5', '', ntxt.count('\5')-1)
        vis = WP_Repl_Re.sub('', ntxt).rstrip('\5')
        if (cursidx := vis.rfind('\5')) != -1:
            curslndiff, col = self._getlndiff(vis, cursidx, mxwid)
            up = '' if curslndiff <= 0 else f'\033[{curslndiff}A'
            right = '' if col <= 0 else f'\033[{col}C'
            print(pref+ntxt.replace('\5', '', 1)+'\r'+up+right, end="", flush=True)
        else:
            if (lastln := len(vis) - vis.rfind('\n') - 1) > 0:
                wrap = ' \r' if lastln % mxwid == 0 else ''
            else:
                wrap = ''
            print(pref+ntxt+wrap, end="", flush=True)

        self.oldtxt = vis


def newinp(prompt="", wp=None, start="", *, tabforcexit=False):
    if wp is None:
        wp = WrapPrinter()
    buf = start
    pos = len(start)
    while True:
        full = prompt+buf[:pos]+'\5'+buf[pos:]
        wp(full, end="")
        k = read_key()
        if k in ("\r", "\n"):
            wp(full.replace('\5', '', 1))
            break
        elif k == "\x03": # Ctrl+C
            wp(full.replace('\5', '^C', 1))
            raise KeyboardInterrupt
        elif k == "\x04": # Ctrl+D
            wp(full.replace('\5', '^D', 1))
            raise EOFError
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
        elif k == "\t":
            if tabforcexit:
                wp(end="")
                return buf+'\t'
            buf, pos = buf[:pos] + '    ' + buf[pos:], pos + 4
        elif len(k) == 1 and k.isprintable():
            buf, pos = buf[:pos] + k + buf[pos:], pos + 1
    return buf

builtins.input = newinp
