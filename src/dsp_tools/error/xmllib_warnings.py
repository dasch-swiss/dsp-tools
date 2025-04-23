from abc import ABC
from dataclasses import dataclass

from loguru import logger


@dataclass
class MessageInfo:
    resource_id: str
    message: str
    prop_name: str | None = None


def get_message_string(msg: MessageInfo) -> str:
    str_list = [f"Resource ID '{msg.resource_id}'"]
    if msg.prop_name:
        str_list.append(f"Property '{msg.prop_name}'")
    str_list.append(msg.message)
    return " | ".join(str_list)


class XmllibUserMessage(ABC):
    """Class for general user-facing warnings"""

    @staticmethod
    def showwarning(message: str, depth: int) -> None:
        """Base method for print-outs"""


class XmllibUserInfo(XmllibUserMessage):
    @staticmethod
    def showwarning(msg_info: MessageInfo, depth: int) -> None:
        logger.opt(depth=depth).info(get_message_string(msg_info))
