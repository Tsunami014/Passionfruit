from read import WrapPrinter, wait
from .edit import edit_file, edit_text
import dir

from random import shuffle

GROUPS_FILE = '/groups.txt'
ITEMS_FILE = '/items.txt'
ALL_LETTERS = '1234567890qwertyuiopasdfghjklzxcvbnm'
def main(grps):
    if not grps:
        edit_file((GROUPS_FILE,), extra="\nPut all groups on new lines")
        grpits = dir.cat((GROUPS_FILE,))
        if grpits is None:
            return
        grps = grpits.split('\n')

    grps = [t for i in grps if (t := i.strip())]
    if len(grps) == 0:
        print("\033[91mNo groups!\033[0m")
        return
    if len(grps) > len(ALL_LETTERS):
        print("\033[91mNo groups!\033[0m")
        return

    edit_file((ITEMS_FILE,), extra="\nPut all items/people/objects to categorise on new lines")
    its = dir.cat((ITEMS_FILE,))
    if its is None:
        return
    items = [t for i in its.split('\n') if (t := i.strip())]
    shuffle(items)

    grpletters = {
        l: nam for l, nam in zip(ALL_LETTERS, grps)
    }
    used_letters = ALL_LETTERS[:len(grps)]+'\r\n'
    outs = {nam: [] for nam in grps}
    nones = []
    wp = WrapPrinter()
    try:
        for it in items:
            sel = set()
            while True:
                wp(
                    "Choose categories for the following item (press enter when done):\n"
                    f"  \033[95;1m{it}\033[0m\n"+
                    '\n'.join(('\033[92;1m> ' if nam in sel else '  ')+l+'  '+nam+'\033[0m' for l, nam in grpletters.items())
                )
                k = wait(wait_for=used_letters)
                if k in '\r\n':
                    break
                nam = grpletters[k]
                if nam in sel:
                    sel.remove(nam)
                else:
                    sel.add(nam)
            if sel:
                for s in sel:
                    outs[s].append(it)
            else:
                nones.append(it)
    finally:
        if nones:
            outs["No Category"] = nones

        wp('\n'.join(
            f"  \033[1m{nam}\033[0m\n"+(
                '\n'.join(
                    f"  {'└' if idx == mx else '├'}─ "+i for idx, i in enumerate(conts)
                ) if (mx := len(conts)-1) >= 0 else "   \033[37m(No items)\033[0m"
            ) for nam, conts in outs.items()
        ))
