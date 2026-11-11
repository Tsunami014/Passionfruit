from dir import parse_pth, root_pth
from read import read_key, WrapPrinter, wait
import os


PREF = "\033[90m~ \033[0m"
def edit_text(fc, pref='', savefn=None):
    if fc.endswith('\n'):
        fc = fc[:-1]
    saved = fc
    try:
        print(end='\033[?1049h\033[2J\033[H', flush=True)
        lines = saved.split('\n')
        isrecent = True
        wp = WrapPrinter()
        line = 0
        col = 0
        if pref:
            pref = '\n'+pref
        pref = f"\033[37mCtrl+S - Save, Ctrl+X - Exit, Ctrl+G - More help{pref}\033[0m\n"
        while True:
            print(end='\033[2J\033[H')
            ppref = '' if isrecent else '\033[93m*\033[0m'
            wp(ppref+pref+'\n'.join(
                PREF+ln if idx != line else PREF+ln[:col]+'\5'+ln[col:]
                for idx, ln in enumerate(lines)
            ))
            k = read_key()
            if k == "\x07": # Ctrl+G - Help
                wp("""\033[1mHELP\033[0m

Ctrl+S - Save
Ctrl+X - Exit
Ctrl+Z - Reset contents to last saved
Ctrl+C - Delete current line
Ctrl+D - Clear everything

Press Enter to close help""")
                wait()
            elif k == "\x13": # Ctrl+S - Save
                if not isrecent:
                    if savefn is not None:
                        savefn(lines)
                    saved = '\n'.join(lines)
                    isrecent = True
            if k == "\x18": # Ctrl+X - Exit
                if (not isrecent) and savefn is not None:
                    wp("Save before exiting? [Y/n] > \5\n"+'\n'.join(PREF+ln for ln in lines))
                    if wait(wait_for='yn\n\r') != 'n':
                        savefn(lines)
                return lines
            elif k == "\x1A": # Ctrl+Z - Reset contents to last saved
                if not isrecent:
                    wp("Reset buffer? [y/N] > \5\n"+'\n'.join(PREF+ln for ln in lines))
                    if wait(wait_for='yn\n\r') == 'y':
                        lines = saved.split('\n')
                        isrecent = True
                        line = 0
                        col = 0
            elif k == "\x03": # Ctrl+C - Delete single line
                if len(lines) <= 1:
                    if lines != [""]:
                        isrecent = False
                        lines = [""]
                        line = 0
                        col = 0
                else:
                    isrecent = False
                    lines.pop(line)
                    line = min(line, len(lines)-1)
                    col = min(len(lines[line]), col)
            elif k == "\x04": # Ctrl+D - Clear
                if lines != [""]:
                    wp("Clear buffer? [y/N] > \5\n"+'\n'.join(PREF+ln for ln in lines))
                    if wait(wait_for='yn\n\r') == 'y':
                        isrecent = False
                        lines = [""]
                        line = 0
                        col = 0
            elif k in ("\r", "\n"):
                isrecent = False
                old = lines[line]
                lines.insert(line+1, old[col:])
                lines[line] = old[:col]
                line += 1
                col = 0
            elif k == "bs":
                if col:
                    isrecent = False
                    curln = lines[line]
                    lines[line], col = curln[:col - 1] + curln[col:], col - 1
                elif line:
                    isrecent = False
                    oldnew = lines[line-1]
                    col = len(oldnew)
                    lines[line-1] = oldnew+lines.pop(line)
                    line -= 1
            elif k == "del":
                curln = lines[line]
                if col == len(curln):
                    if line + 1 < len(lines):
                        lines[line] = curln + lines.pop(line+1)
                        isrecent = False
                else:
                    lines[line] = curln[:col] + curln[col + 1:]
                    isrecent = False
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
                isrecent = False
            elif len(k) == 1 and k.isprintable():
                curln = lines[line]
                lines[line], col = curln[:col] + k + curln[col:], col + 1
                isrecent = False
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
        rpth = root_pth(fpth)
        def save(outlns):
            with open(fpth, 'w+') as f:
                for ln in outlns:
                    f.write(ln+'\n')
        edit_text(fc, (rpth+'\n'+extra if extra else rpth), save)
