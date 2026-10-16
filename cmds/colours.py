from read import read_key
from random import choice, randint

def choose_col(prompt):
    print("""
Up/down - Redness  |  Left/right - Blueness
Comma/dot - Brightness  |  Enter - Confirm
"""[1:-1])
    print(prompt)
    r, b, w = (randint(0, 5) for _ in range(3))
    while True:
        col = f'\033[48;5;{16+b+w*6+r*36}m   \033[0m'
        print("|  "+col, end='\r')
        k = read_key()
        if k in ("\r", "\n", "\x03", "\x04"):
            break
        elif k == "up":
            r = max(r-1, 0)
        elif k == "down":
            r = min(r+1, 5)
        elif k == "left":
            b = max(b-1, 0)
        elif k == "right":
            b = min(b+1, 5)
        elif k == ",":
            w = max(w-1, 0)
        elif k == ".":
            w = min(w+1, 5)
    print(f"\033[3A{prompt}\033[K\n> {col}\033[K")

def colAssoc(*_):
    with open('data/colourables.txt') as f:
        choose_col(f"What colour would fit \033[1m{choice(f.readlines()).strip()}\033[0m?")
