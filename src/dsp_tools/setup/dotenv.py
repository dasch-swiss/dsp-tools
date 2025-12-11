from dotenv import find_dotenv
from dotenv import load_dotenv


def read_dotenv_if_exists() -> None:
    """
    Load .env file only if it exists in the current working directory
    This allows CI to set environment variables directly without interference
    """
    dotenv_file = find_dotenv(usecwd=True)
    if dotenv_file:
        load_dotenv(dotenv_path=dotenv_file, override=False)
