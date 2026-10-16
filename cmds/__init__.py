import time

COMMANDS = {
    "help": ((lambda a: "Commands: help, echo, date, whoami, ls, clear, exit"), "Print help info"),
    "echo": ((lambda a: " ".join(a)), "Echoes text"),
    "date": ((lambda a: time.strftime("%a %b %d %H:%M:%S %Y")), "Print date stuff"),
    "whoami": ((lambda a: "guest"), "Print who you are logged in as"),
    "ls": ((lambda a: "documents  downloads  notes.txt  pictures"), "Display the current directory"),
    "clear": ((lambda a: print("\x1b[2J\x1b[H", end="") or ""), "Clear the display"),

    "exit": (None, "Exit the terminal"),
}
