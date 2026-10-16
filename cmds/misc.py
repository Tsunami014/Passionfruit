from itertools import batched
from random import choice

def vague(*_):
    with open('data/vague.txt') as f:
        fc = f.read()
    opts = list(batched(fc.split('\n---\n'), 2))
    ays, bs = choice(opts)
    ays, bs = ([i for i in l.split('\n') if i] for l in (ays, bs.lower()))
    a, b = choice(ays), choice(bs)
    try:
        input(f"How many/much do you think is...\n\033[1m{a} {b}\033[0m? > ")
    except KeyboardInterrupt:
        print("^C")

def assocs(*_):
    try:
        print("What is the first thing that comes to mind when you see the word:")
        input("(Enter to reveal word)")
        with open('data/wordlist.txt') as f:
            print("\033[1A\r\033[1m"+choice(f.readlines()).strip()+"\033[0m\033[K")
        input("> ")
    except KeyboardInterrupt:
        pass
