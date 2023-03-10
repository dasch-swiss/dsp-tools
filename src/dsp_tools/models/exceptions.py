from pystrict import strict


@strict
class BaseError(Exception):
    """
    A basic error class for DSP-TOOLS
    """
    message: str

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message
    
    def __str__(self) -> str:
        return self.message


class InternalError(BaseError):
    """
    Class for errors that will be handled by a higher level function
    """
    pass


class UserError(BaseError):
    """
    Class for errors that are intended for user feedback. 
    Typically, a UserError is raised when the execution of a program must be interrupted 
    due to a bad condition in the input data that prevents further processing.
    The message should be as user-friendly as possible.
    """
    pass
