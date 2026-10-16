from itertools import batched
from random import choice

def mkWriter(OPTS, info):
    info = info.strip()
    def fn(*_):
        print(info)
        input("Ctrl+C to quit, enter to begin")
        print(end="\033[1A\033[K")
        while True:
            print(f'\033[1m{choice(OPTS).strip()}\033[0m')
            try:
                input("> ")
            except KeyboardInterrupt:
                print()
                break
    return fn

OPTS = []
with open('data/vague.txt') as f:
    fc = f.read()
    for ays, b in batched(fc.split('\n---\n'), 2):
        bs = [i for i in b.lower().split('\n') if i]
        for a in ays.split('\n'):
            if not a:
                continue
            OPTS.extend([a+' '+i for i in bs])

vague = mkWriter(OPTS, """
Press enter to generate a "vague amount", then write down how much/many you would associate with that.
""")

with open('data/wordlist.txt') as f:
    OPTS = f.readlines()
assocs = mkWriter(OPTS, """
Press enter to generate a word, then write down the first thing that comes to your mind when you read it!
You can write multiple if you want, it's just for you. Also don't worry if you don't know what a word means, just skip it.
""")

del OPTS
