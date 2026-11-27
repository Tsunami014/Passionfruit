from read import WrapPrinter, wait, read_key
from .edit import edit_file
from string import ascii_lowercase
import dir

from random import shuffle

GROUPS_FILE = '/groups.txt'
ITEMS_FILE = '/items.txt'
ALL_LETTERS = ascii_lowercase
def main(grps):
    groups = []
    items = None
    def editItems():
        nonlocal items
        edit_file((ITEMS_FILE,), extra="Put all items/people/objects to categorise on new lines")
        its = dir.cat((ITEMS_FILE,))
        if its is None:
            print("\033[91mNo items!\033[0m")
            raise KeyboardInterrupt
        items = [t for i in its.split('\n') if (t := i.strip())]
        if len(items) == 0:
            print("\033[91mNo items!\033[0m")
            raise KeyboardInterrupt
        itset = set(items)
        for i in range(len(groups)):
            groups[i][1] = [it for it in groups[i][1] if it in itset]
    editItems()

    def end(groups, items):
        nones = [i for i in items if all(i not in li for _, li in groups)]
        displgs = groups
        if nones:
            displgs = groups.copy()+[('No group', nones)]
        return '\n'.join(
            f" \033[1m{nam}\033[0m\n"+(
                '\n'.join(
                    f"  {'└' if idx == mx else '├'}─ "+i for idx, i in enumerate(conts)
                ) if (mx := len(conts)-1) >= 0 else "   \033[37m(No items)\033[0m"
            ) for nam, conts in displgs
        )

    wp = WrapPrinter()
    def chooseItems(grp, origcur):
        shuffle(items)
        sel = 0
        curs = set(origcur)
        while True:
            print(end='\033[2J\033[H')
            wp(
                f"Select items for '{grp}' (tab/space to toggle, enter to save and return, ctrl+c to return without saving)\n"
                +'\n'.join([
                    ('>\5' if idx == sel else ' ')+('*' if it in curs else ' ')+it
                    for idx, it in enumerate(items)
                ])
            )
            k = read_key()
            if k == "\x03": # Ctrl+C
                return origcur
            elif k == "\x04": # Ctrl+D
                return origcur
            elif k in ('down', 'right'):
                sel = min(len(items)-1, sel+1)
            elif k in ('up', 'left'):
                sel = max(0, sel-1)
            elif k in ('\t', ' '):
                if (curit := items[sel]) in curs:
                    curs.remove(curit)
                else:
                    curs.add(curit)
            elif k in ('\n', '\r'):
                return tuple(curs)

    try:
        print(end='\033[?1049h\033[2J\033[H', flush=True)
        cmd = ''
        while True:
            conts = [f"{idx+1}: {nam}" for idx, (nam, _) in enumerate(groups)]
            if cmd == '':
                print(end='\033[2J\033[H')
                wp(
                    f"> {cmd}\5"
                    "\n  n: New group     d: Delete group"
                    "\n  r: Rename group  i: Edit items"
                    "\n  q: Quit (with preview)"
                    "\n  Or type group number to edit selections"
                    +('\n'+'\n'.join(conts) if conts else '')
                )
                k = wait(wait_for='1234567890drniq')
                if k == 'n':
                    try:
                        nname = input("New group name (Ctrl+C to cancel)\n> ", wp=wp)
                        groups.append([nname, []])
                        groups.sort(key=lambda x: x[0])
                    except (KeyboardInterrupt, EOFError):
                        pass
                elif k == 'i':
                    editItems()
                elif k == 'q':
                    wp('> q\5\nQuitting (on enter)\nPreview:\n'+end(groups, items))
                    k = wait(wait_for=('\r', '\n', 'bs'), special=True)
                    if k != 'bs':
                        break
                elif k != '0':
                    cmd += k
            else:
                conts = [n for n in conts if n.startswith(cmd.lstrip('dr'))]
                act = cmd[0]
                wp(
                    f"> {cmd}\5\n" + {
                        'd': "Deleting",
                        'r': "Renaming"
                    }.get(act, 'Edit selection for') + (
                        ' ...'+('\n'+'\n'.join(conts) if conts else '')
                        if len(conts) != 1 else
                        conts[0][conts[0].index(':'):]+' (on enter)'
                    )
                )
                k = wait(wait_for=list('1234567890\r\n')+['bs'], special=True)
                if k == 'bs':
                    cmd = cmd[:-1]
                elif k in '\r\n':
                    if len(conts) != 1:
                        continue
                    cmd = ''
                    idx = int(conts[0][:conts[0].index(':')])-1

                    if act == 'd':
                        groups.pop(idx)
                    elif act == 'r':
                        try:
                            nname = input(f"New group name for '{groups[idx][0]}' (Ctrl+C to cancel)\n> ", wp=wp)
                            groups[idx][0] = nname
                            groups.sort(key=lambda x: x[0])
                        except (KeyboardInterrupt, EOFError):
                            pass
                    else:
                        nam, curits = groups[idx]
                        try:
                            groups[idx] = (nam, chooseItems(nam, curits))
                        except (KeyboardInterrupt, EOFError):
                            pass
                elif act in '123456789' or len(cmd) != 1 or k != '0':
                    cmd += k
    finally:
        print(end='\033[?1049l', flush=True)
        if len(items) == 0:
            return
        wp(end(groups, items))
