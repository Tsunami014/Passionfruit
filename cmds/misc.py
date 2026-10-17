from itertools import batched
from random import choice
from read import wait

def vague(_, first=True):
    with open('data/vague.txt') as f:
        fc = f.read()
    opts = list(batched(fc.split('\n---\n'), 2))
    ays, bs = choice(opts)
    ays, bs = ([i for i in l.split('\n') if i] for l in (ays, bs.lower()))
    a, b = choice(ays), choice(bs)
    if first:
        print("How many/much do you think is...")
    input(f"\033[1m{a} {b}\033[0m? > ")

def assocs(_, first=True):
    if first:
        print("What is the first thing(s) that come to mind when you see the word:")
    wait("(Enter to reveal word)")
    with open('data/wordlist.txt') as f:
        word = choice(f.readlines()).strip()
    word = word[0].upper()+word[1:]
    print("\r\033[1m"+word+"\033[0m\033[K")
    input("> ")

def react(_):
    wait("(Enter to reveal statement, then press Y or N as fast as you can)")
    with open('data/reacts.txt') as f:
        print("\r\033[1m"+choice(f.readlines()).strip()+"\033[0m\033[K")
    print(wait("> ", wait_for="yn").upper())
