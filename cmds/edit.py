from dir import parse_pth
import os

def edit_file(a):
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
        # TODO: This
        import subprocess
        subprocess.run(["nvim", fpth])
