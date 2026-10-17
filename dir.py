import os
PTH = '/' # When I implement this, a lot of things will break :P

root = os.path.abspath(os.path.join(os.getcwd(), "config"))
if not os.path.exists(root):
    os.mkdir(root)

def parse_pth(pth):
    if pth.startswith('/'):
        pth = '.'+pth
    full = os.path.abspath(os.path.join(root, pth))
    if os.path.commonpath([root, full]) != root:
        return None
    return full

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
            print(f"{pth}  - total {len(fs)}")
            if fs:
                print("   "+'  '.join(fs))
        else:
            print(pth)

def rm(a):
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
