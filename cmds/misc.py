from random import choice

def assocs(*_):
    with open('data/wordlist.txt') as f:
        WORDS = f.readlines()
    print("Press enter to generate a word, then write down the first thing that comes to your mind when you read it!")
    print("You can write multiple if you want, it's just for you. Also don't worry if you don't know what a word means, just skip it!")
    print("Ctrl+C to quit")
    while True:
        try:
            input("> ")
        except KeyboardInterrupt:
            print()
            break
        print(f'\033[1m{choice(WORDS).strip()}\033[0m')
