from abc import ABC

from loguru import logger


class XmllibUserMessage(ABC):
    """Class for general user-facing warnings"""

    @staticmethod
    def showwarning(message: str, depth: int) -> None:
        """Base method for print-outs"""


class XmllibUserInfo(XmllibUserMessage):
    @staticmethod
    def showwarning(message: str, depth: int) -> None:
        logger.opt(depth=depth).info(message)
