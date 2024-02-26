from dsp_tools.commands.xmlupload.stash.stash_models import Stash


def get_stash_from_file() -> Stash:
    """
    Get stash from ~/.dsp-tools/xmluploads/localhost/4123/testonto/2024-02-26_151739_stashed_links_localhost.json

    Returns:
        stash
    """
    return Stash(None, None)
