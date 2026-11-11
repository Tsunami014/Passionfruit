import os
import shutil
from collections import deque
PTH = '/' # Must end with / and start with /
def nicePth():
    if PTH == '/':
        return '/'
    return PTH[:-1]

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

def getpths(args, dirsonly=False):
    cur = args[-1]
    if not cur or cur[-1] == '/':
        return ""
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
            isdir = os.path.isdir(os.path.join(d, name))
            if not isdir and dirsonly:
                continue
            if not name.endswith('/') and isdir:
                name += '/'
            return dir + name
    return None
def getdirpths(args):
    return getpths(args, True)


def cd(a):
    if not a:
        a = ('/',)
    if len(a) > 1:
        print("\033[91mToo many paths provided!\033[0m")
        return
    pth = a[0]
    fpth = parse_pth(pth)
    if fpth is None:
        print("\033[91mPath outside root:\033[0m", pth)
    elif not os.path.exists(fpth):
        print("\033[91mPath does not exist:\033[0m", pth)
    elif not os.path.isdir(fpth):
        print("\033[91mPath is not a directory:\033[0m", pth)
    else:
        global PTH
        PTH = root_pth(fpth)
        if not PTH.endswith('/'):
            PTH += '/'

def ls(a):
    if not a:
        a = ('./',)
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
        elif not os.path.exists(fpth):
            print("\033[91mPath does not exist:\033[0m", pth)
        elif os.path.isdir(fpth):
            fs = os.listdir(fpth)
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
                    if nxt is None:
                        pref = '   '
                        nxt = 0
                    if nxt+ln >= mxln:
                        pref = '\n   '
                        nxt = -1 # Adjust for newline
                    print(pref+t, end='')
                    nxt += len(pref)+ln
                print()
            else:
                print("\033[90m(Nothing here!)\033[0m")
        else:
            print(root_pth(fpth))

def cp(a, mv=False):
    dirs = '-r' in a
    if dirs:
        a.remove('-r')
    if len(a) != 2:
        print("\033[91mNeeds 2 arguments!\033[0m")
        return
    fpths = []
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
            return
        fpths.append(fpth)
    if not os.path.exists(fpths[0]):
        print("\033[91mSource path does not exist:\033[0m", a[0])
        return
    if os.path.isdir(fpths[1]):
        fpths[1] = fpths[1]+('/' if not fpths[1].endswith('/') else '')+os.path.basename(fpths[0])
    if os.path.exists(fpths[1]):
        print("\033[91mDestination path exists:\033[0m", a[1])
        return

    if os.path.isdir(fpths[0]):
        if not dirs:
            cmd = 'move' if mv else 'copy'
            print("\033[91mPath is a directory:\033[0m", a[0]+f"\n  \033[90m(Run with -r to {cmd} directory contents)\033[0m")
            return
        if mv:
            shutil.move(*fpths)
        else:
            shutil.copytree(*fpths)
    else:
        if mv:
            shutil.move(*fpths)
        else:
            shutil.copy(*fpths)
def mv(a):
    cp(a, True)

def rm(a):
    dirs = '-r' in a
    if dirs:
        a.remove('-r')
    if not a:
        print("\033[91mNo files provided!\033[0m")
        return
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
        elif not os.path.exists(fpth):
            print("\033[91mPath does not exist:\033[0m", pth)
        elif os.path.isdir(fpth):
            if dirs:
                if PTH.startswith(root_pth(fpth)):
                    print("\033[91mCannot delete directory you are in!\033[0m")
                else:
                    shutil.rmtree(fpth)
            else:
                print("\033[91mPath is a directory:\033[0m", pth+"\n  \033[90m(Run with -r to delete directory contents)\033[0m")
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
    parents = '-p' in a
    if parents:
        a.remove('-p')
    if not a:
        print("\033[91mNo directories provided!\033[0m")
        return
    for pth in a:
        fpth = parse_pth(pth)
        if fpth is None:
            print("\033[91mPath outside root:\033[0m", pth)
        elif not os.path.exists(fpth):
            if parents:
                os.makedirs(fpth, exist_ok=True)
            elif not os.path.exists(os.path.dirname(fpth)):
                print("\033[91mParent does not exist to:\033[0m", pth+"\n  \033[90m(Run with -p to create parent directories)\033[0m")
            else:
                os.mkdir(fpth)
        elif not os.path.isdir(fpth):
            print("\033[91mPath is not a directory:\033[0m", pth)
        elif not parents:
            print("\033[91mPath already exists:\033[0m", pth+"\n  \033[90m(Run with -p to ignore existing)\033[0m")
