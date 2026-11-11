import os
import shutil
from collections import deque
PTH = '/' # Must end with / and start with /

root = os.path.abspath(os.path.join(os.getcwd(), "config"))
if not os.path.exists(root):
    os.mkdir(root)

def parse_pth(pth):
    if pth.startswith('/'):
        pth = '.'+pth
    else:
        pth = '.'+PTH+pth
    full = os.path.abspath(os.path.join(root, pth))
    if os.path.commonpath([root, full]) != root:
        return None
    return full

def root_pth(fpth):
    rpth = os.path.relpath(fpth, root)
    if rpth == '.':
        return '/'
    return '/'+rpth

def ensure_exists(pth):
    fpth = parse_pth(pth)
    if os.path.isdir(fpth):
        os.makedirs(fpth, exist_ok=True)
    else:
        os.makedirs(os.path.dirname(fpth), exist_ok=True)
        with open(fpth, "a"):
            pass

def getpths(_, cur):
    cur = cur or ''
    head, sep, prefix = cur.rpartition('/')
    dir = head + sep

    d = parse_pth(dir or './')
    if d is None or not os.path.isdir(d):
        return None

    names = sorted(os.listdir(d))
    if prefix.startswith('.'):
        names = ['./'] + ([] if d == root else ['../']) + names
    else: # Hide dotfiles unless prefix starts with '.'
        names = [n for n in names if not n.startswith('.')]

    for name in names:
        if name.startswith(prefix):
            if not name.endswith('/') and os.path.isdir(os.path.join(d, name)):
                name += '/'
            return dir + name
    return None


def ls(a):
    if not a:
        a = ('/',)
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
        elif not os.path.exists(fpth):
            print("\033[91mPath does not exist:\033[0m", pth)
        elif os.path.isdir(fpth):
            fs = os.listdir(fpth)
            print(f"{root_pth(fpth)}   total {len(fs)}", end='')
            if fs:
                parsedfs = deque(
                    (f'\033[94m{f}/\033[0m', len(f)+1) if os.path.isdir(os.path.join(fpth, f)) else (f, len(f))
                    for f in fs
                )
                nxt = None
                mxln = shutil.get_terminal_size().columns
                while parsedfs:
                    t, ln = parsedfs.popleft()
                    pref = '  '
                    if nxt is None or nxt+ln >= mxln:
                        pref = '\n   '
                        nxt = -1 # Adjust for newline
                    print(pref+t, end='')
                    nxt += len(pref)+ln
                print()
        else:
            print(root_pth(fpth))

def rm(a):
    if not a:
        print("\033[91mNo files provided!\033[0m")
        return
    dirs = '-r' in a
    if dirs:
        a.remove('-r')
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
        elif not os.path.exists(fpth):
            print("\033[91mPath does not exist:\033[0m", pth)
        elif os.path.isdir(fpth):
            if dirs:
                if root_pth(fpth) == '/':
                    print("\033[91mCannot delete root!\033[0m")
                else:
                    shutil.rmtree(fpth)
            else:
                print("\033[91mPath is a directory:\033[0m", pth)
        else:
            os.remove(fpth)

def cat(a):
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
    elif not os.path.exists(fpth):
        print("\033[91mPath does not exist:\033[0m", pth)
    elif os.path.isdir(fpth):
        print("\033[91mPath is a directory:\033[0m", pth)
    else:
        with open(fpth) as f:
            return f.read()

def touch(a):
    if not a:
        print("\033[91mNo files provided!\033[0m")
        return
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
        elif os.path.isdir(fpth):
            print("\033[91mPath is a directory:\033[0m", pth)
        else:
            if not os.path.exists(fpth):
                if not os.path.exists(os.path.dirname(fpth)):
                    print("\033[91mParent does not exist to:\033[0m", pth)
                    continue
            with open(fpth, 'a'):
                os.utime(fpth, None)

def mkdir(a):
    if not a:
        print("\033[91mNo directories provided!\033[0m")
        return
    parents = '-p' in a
    if parents:
        a.remove('-p')
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
        elif not os.path.exists(fpth):
            if parents:
                os.makedirs(fpth, exist_ok=True)
            elif not os.path.exists(os.path.dirname(fpth)):
                print("\033[91mParent does not exist to:\033[0m", pth, "\033[90m(Run with -p to create parent directories)\033[0m")
            else:
                os.mkdir(fpth)
        elif not os.path.isdir(fpth):
            print("\033[91mPath is not a directory:\033[0m", pth)
        elif not parents:
            print("\033[91mPath already exists:\033[0m", pth, "\033[90m(Run with -p to ignore existing)\033[0m")
