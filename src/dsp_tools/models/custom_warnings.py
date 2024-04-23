from termcolor import colored


class DspToolsFutureWarning(FutureWarning):
    def __str__(self) -> str:
        return colored(self.args[0], color="red", attrs=["bold"])
