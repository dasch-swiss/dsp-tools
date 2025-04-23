from abc import ABC
from abc import abstractmethod

from loguru import logger


class XmllibUserMessage(Warning, ABC):
    """Class for general user-facing warnings"""

    @classmethod
    @abstractmethod
    def showwarning(cls, message: str, depth: int) -> None:
        """Base method for print-outs"""


class XmllibUserInfo(XmllibUserMessage):
    @classmethod
    def showwarning(cls, message: str, depth: int) -> None:
        logger.opt(depth=cls.args[1]).info(cls.args[0])
