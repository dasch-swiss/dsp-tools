from pathlib import Path

ERROR_EXCERPT_LINES = 10
NEXT_STEP = "Correct the XML file and run 'ingest-xmlupload' again."


def report_failed_import(error_message: str | None, target: Path) -> None:
    """
    Tells the user why a bulk data import failed.
    The console shows the first lines of the server's error message and the next step.
    The full message goes to the target file. An empty message writes no file.
    """
    if not error_message:
        print(f"The bulk data import failed. The server sent no error message.\n{NEXT_STEP}")
        return
    target.write_text(error_message, encoding="utf-8")
    print(
        f"The bulk data import failed. The server sent this error message:\n"
        f"{_excerpt(error_message)}\n"
        f"The full error message is in: {target}\n"
        f"{NEXT_STEP}"
    )


def _excerpt(error_message: str) -> str:
    lines = error_message.splitlines()
    excerpt = "\n".join(lines[:ERROR_EXCERPT_LINES])
    if len(lines) > ERROR_EXCERPT_LINES:
        excerpt += f"\n({len(lines) - ERROR_EXCERPT_LINES} more lines)"
    return excerpt
