import sys

from dsp_tools.error.exceptions import UserError


def stdin_is_interactive() -> bool:
    """Return whether stdin is an interactive terminal that input() can safely read from."""
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except (AttributeError, ValueError, OSError):
        return False


def prompt_until_valid_answer(
    prompt: str,
    valid_answers: list[str],
    non_interactive_answer: str,
    non_interactive_notice: str,
) -> str:
    """Ask the user until they enter one of the valid answers, and return the answer.

    In a non-interactive session (no TTY, e.g. CI, cron, piped stdin, or Docker without a TTY),
    print the notice and return non_interactive_answer instead of calling input(), which would
    raise there.

    Args:
        prompt: text shown to the user before reading their answer
        valid_answers: the answers that end the prompt loop
        non_interactive_answer: the answer to assume when stdin is not interactive
        non_interactive_notice: message printed when stdin is not interactive,
            so a non-interactive run records which branch was taken

    Returns:
        the answer entered by the user, or non_interactive_answer in a non-interactive session
    """
    if not stdin_is_interactive():
        print(non_interactive_notice)
        return non_interactive_answer
    answer = ""
    while answer not in valid_answers:
        answer = input(prompt)
    return answer


def prompt_for_required_value(value_name: str, cli_flag: str) -> str:
    """Read a value that the command requires, from an interactive prompt or raise if there is none.

    In an interactive session, return the user's (stripped) input; the value is not validated
    further, so an empty answer is returned as an empty string. In a non-interactive session
    (no TTY), raise a UserError telling the user to pass the value via cli_flag, instead of
    calling input(), which would raise an unhelpful error there.

    Args:
        value_name: human-readable name of the value, e.g. "project shortcode"
        cli_flag: the CLI flag that can supply the value non-interactively, e.g. "--project-shortcode"
    """
    if not stdin_is_interactive():
        raise UserError(
            f"No {value_name} was provided and dsp-tools is not running in an interactive terminal. "
            f"Provide it via '{cli_flag}'."
        )
    return input(f"Enter the {value_name}: ").strip()
