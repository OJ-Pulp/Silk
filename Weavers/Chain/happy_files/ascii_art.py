
import pyfiglet

GREEN = "\033[92m"
RESET = "\033[0m"

# Converts the string into ASCII art using the standard font
ascii_art = pyfiglet.figlet_format("ChainWeaver")
print(ascii_art)

title_art = pyfiglet.figlet_format("ChainWeaver", font="slant")
print(GREEN + title_art + RESET)
