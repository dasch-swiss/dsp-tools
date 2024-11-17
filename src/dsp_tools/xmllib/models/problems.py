from dataclasses import dataclass

from dsp_tools.models.problems import Problem


@dataclass
class IllegalTagProblem(Problem):
    orig_err_msg: str
    pseudo_xml: str

    def execute_error_protocol(self) -> str:
        msg = (
            "The XML tags contained in a richtext property (encoding=xml) must be well-formed. "
            "The special characters <, > and & are only allowed to construct a tag. "
        )
        msg += f"\nOriginal error message: {self.orig_err_msg}"
        msg += f"\nEventual line/column numbers are relative to this text: {self.pseudo_xml}"
        return msg
