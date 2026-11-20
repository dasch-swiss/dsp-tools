from dataclasses import dataclass


@dataclass
class XSDValidationMessage:
    line_number: int
    element: str | None
    attribute: str | None
    message: str


def get_xsd_validation_message_str(msg: XSDValidationMessage) -> str:
    msg_list = [f"Line Number {msg.line_number}"]
    if msg.element:
        msg_list.append(f"Element '{msg.element}'")
    if msg.attribute:
        msg_list.append(f"Attribute '{msg.attribute}'")
    msg_list.append(msg.message)
    return " | ".join(msg_list)
