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


class XmllibUserMessage(Warning):
    """Protocol for warnings that implement a custom showwarnings() function"""

    @classmethod
    def showwarning(cls, msg: str) -> None:
        """Functionality that should be executed when a warning of this class is emitted"""


class XmllibUserInfo(XmllibUserMessage):
    @classmethod
    def showwarning(cls, msg: str) -> None:
        logger.opt(depth=5).info(msg)
