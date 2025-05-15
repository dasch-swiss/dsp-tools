# These are ANSI escape codes which can be used to configure the print output on the terminal
# http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
# The semicolon separates different configurations

# All codes must start with an escape sequence, it may differ in different languages, in Python "\u001b[" works
SEQUENCE_START = "\u001b["

# the "m" at the end signals,
# that the configuration code is finished and after that the string that should be printed starts
SEQUENCE_END = "m"

# reset to the default setting of the console
RESET_TO_DEFAULT = f"{SEQUENCE_START}0{SEQUENCE_END}"

# If you want to change for example both the text color and the background color you can combine the sequences
# for example: BACKGROUND_BOLD_MAGENTA + YELLOW -> magenta background with yellow text

# Colored Text
BOLD_GREEN = f"{SEQUENCE_START}1;32{SEQUENCE_END}"  # 1 (bold) ; 32 (green)
BOLD_RED = f"{SEQUENCE_START}1;31{SEQUENCE_END}"  # 1 (bold) ; 31 (red)
BOLD_CYAN = f"{SEQUENCE_START}1;36{SEQUENCE_END}"  # 1 (bold) ; 36 (cyan)
BOLD_YELLOW = f"{SEQUENCE_START}1;33{SEQUENCE_END}"  # 1 (bold) ; 33 (yellow)
YELLOW = f"{SEQUENCE_START}0;33{SEQUENCE_END}"  # 0 (normal font) ; 33 (yellow)
RED = f"{SEQUENCE_START}0;31{SEQUENCE_END}"  # 0 (normal font) ; 31 (red)

# Colored Background
BACKGROUND_BOLD_RED = f"{SEQUENCE_START}1;41{SEQUENCE_END}"  # 1 (bold) ; 41 (background red)
BACKGROUND_BOLD_YELLOW = f"{SEQUENCE_START}1;43{SEQUENCE_END}"  # 1 (bold) ; 43 (background yellow)
BACKGROUND_BOLD_GREEN = f"{SEQUENCE_START}1;42{SEQUENCE_END}"  # 1 (bold) ; 42 (background green)
BACKGROUND_BOLD_CYAN = f"{SEQUENCE_START}1;46{SEQUENCE_END}"  # 1 (bold) ; 46 (background cyan)
