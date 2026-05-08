from yaspin import yaspin
from yaspin.spinners import Spinners


def get_default_spinner(text: str) -> Spinners:
    return yaspin(Spinners.dots, text=text, timer=True)
