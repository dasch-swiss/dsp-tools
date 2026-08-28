from yaspin import yaspin
from yaspin.spinners import Spinners


def get_default_spinner(text: str) -> Spinners:
    return yaspin(Spinners.dots, text=text, timer=True)


def get_green_bouncy_ball_spinner(text: str) -> Spinners:
    return yaspin(
        Spinners.bouncingBall,
        text=text,
        color="light_green",
        attrs=["bold", "blink"],
        timer=True,
    )
