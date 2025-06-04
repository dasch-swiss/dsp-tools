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


def get_xsd_validation_message_dict(msg: XSDValidationMessage) -> dict[str, str]:
    msg_dict = {
        "Line Number": msg.line_number,
        "Element": msg.element,
        "Attribute": msg.attribute,
        "Message": msg.message,
    }
    return {k: str(v) for k, v in msg_dict.items() if v}
