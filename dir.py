import os
PTH = '/'

root = os.path.abspath(os.path.join(os.getcwd(), "config"))
if not os.path.exists(root):
    os.mkdir(root)

def ls(a):
    if not a:
        a = ('./',)
    for pth in a:
        fpth = os.path.abspath(os.path.join(root, pth))
        if not fpth.startswith(root):
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
        fpth = os.path.abspath(os.path.join(root, pth))
        if not fpth.startswith(root):
            print("\033[91mPath outside root:\033[0m", pth)
        elif not os.path.exists(fpth):
            print("\033[91mPath does not exist:\033[0m", pth)
        elif os.path.isdir(fpth):
            print("\033[91mPath is a directory:\033[0m", pth)
        else:
            os.remove(fpth)

def edit(a):
    if not a:
        print("\033[91mNo file provided!\033[0m")
        return
    if len(a) > 1:
        print("\033[91mToo many files provided!\033[0m")
        return
    pth = a[0]
    fpth = os.path.abspath(os.path.join(root, pth))
    if not fpth.startswith(root):
        print("\033[91mPath outside root:\033[0m", pth)
    elif not os.path.exists(fpth):
        print("\033[91mPath does not exist:\033[0m", pth)
    elif os.path.isdir(fpth):
        print("\033[91mPath is a directory:\033[0m", pth)
    else:
        print("TODO: This")
