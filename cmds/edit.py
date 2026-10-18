from dir import parse_pth
from read import read_key, WrapPrinter
import os


PREF = "\033[90m~ \033[0m"
def edit_text(fc, pref):
    try:
        print(end='\033[?1049h\033[2J\033[H', flush=True)
        if fc.endswith('\n'):
            fc = fc[:-1]
        lines = fc.split('\n')
        wp = WrapPrinter()
        line = 0
        col = 0
        pref = f"\033[37m{pref}\033[0m\n"+PREF
        while True:
            print(end='\033[2J\033[H')
            wp(pref+('\n'+PREF).join(
                ln if idx != line else ln[:col]+'\5'+ln[col:]
                for idx, ln in enumerate(lines)
            ))
            k = read_key()
            if k == "\x03": # Ctrl+C
                return lines
            elif k == "\x04": # Ctrl+D
                return None
            elif k in ("\r", "\n"):
                old = lines[line]
                lines.insert(line+1, old[col:])
                lines[line] = old[:col]
                line += 1
                col = 0
            elif k == "bs":
                if col:
                    curln = lines[line]
                    lines[line], col = curln[:col - 1] + curln[col:], col - 1
                elif line:
                    oldnew = lines[line-1]
                    col = len(oldnew)
                    lines[line-1] = oldnew+lines.pop(line)
                    line -= 1
            elif k == "del":
                curln = lines[line]
                if col == len(curln):
                    if line + 1 < len(lines):
                        lines[line] = curln + lines.pop(line+1)
                else:
                    lines[line] = curln[:col] + curln[col + 1:]
            elif k in ("cbs", "cleft"): # jump / delete back one word
                i = col
                curln = lines[line]
                while i and curln[i - 1] == " ":
                    i -= 1
                while i and curln[i - 1] != " ":
                    i -= 1
                lines[line], col = (curln[:i] + curln[col:], i) if k == "cbs" else (curln, i)
            elif k == "cright":
                curln = lines[line]
                ln = len(curln)
                while col < ln and curln[col] == " ":
                    col += 1
                while col < ln and curln[col] != " ":
                    col += 1
            elif k == "up":
                line = max(0, line - 1)
                col = min(len(lines[line]), col)
            elif k == "down":
                line = min(len(lines)-1, line + 1)
                col = min(len(lines[line]), col)
            elif k == "left":
                col = max(0, col - 1)
            elif k == "right":
                col = min(len(lines[line]), col + 1)
            elif k == "\t":
                curln = lines[line]
                lines[line], col = curln[:col] + '    ' + curln[col:], col + 4
            elif len(k) == 1 and k.isprintable():
                curln = lines[line]
                lines[line], col = curln[:col] + k + curln[col:], col + 1
    finally:
        print(end='\033[?1049l', flush=True)


def edit_file(a, *, extra=""):
    if not a:
        print("\033[91mNo file provided!\033[0m")
        return
    if len(a) > 1:
        print("\033[91mToo many files provided!\033[0m")
        return
    pth = a[0]
    fpth = parse_pth(pth)
    if fpth is None:
        print("\033[91mPath outside root:\033[0m", pth)
    elif os.path.isdir(fpth):
        print("\033[91mPath is a directory:\033[0m", pth)
    else:
        # Create file if does not exist
        os.makedirs(os.path.dirname(fpth), exist_ok=True)
        with open(fpth, "a"):
            pass
        with open(fpth) as f:
            fc = f.read()
        if (outlns := edit_text(fc, "Ctrl+C to save and quit, Ctrl+D to quit without saving"+extra)) is not None:
            with open(fpth, 'w+') as f:
                for ln in outlns:
                    f.write(ln+'\n')
