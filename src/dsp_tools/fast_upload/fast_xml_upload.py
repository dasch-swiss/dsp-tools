import pickle
from datetime import datetime
from pathlib import Path

from lxml import etree

from dsp_tools.utils.xml_upload import xml_upload


def _get_paths_from_pkl_file(pkl_file: Path) -> list[tuple[Path, Path]]:
    with open(pkl_file, 'rb') as f:
        orig_paths_2_processed_paths: list[tuple[Path, Path]] = pickle.load(f)
    return orig_paths_2_processed_paths



def fast_xml_upload(
    xml_file: str,
    pkl_file: str,
    user: str,
    password: str,
    dsp_url: str,
    sipi_url: str
) -> bool:
    """
    Reads the paths from the pickle file and uploads all files without processing.

    Args:
        sipi_url ():
        paths_file ():
        xml_file ():
        user: the user's e-mail for login into DSP
        password: the user's password for login into DSP
        dsp_url: URL to the DSP server
    Returns:
        success status
    """

    xml_tree = etree.parse(xml_file)
    paths = _get_paths_from_pkl_file(pkl_file=Path(pkl_file))

    paths_dict = dict()
    for orig_path, processed_path in paths:
        orig_path_str = str(orig_path)
        orig_path_name_str = str(orig_path.name)
        processed_path_str = str(processed_path.name)
        if orig_path_name_str != processed_path_str:
            paths_dict[orig_path_str] = processed_path_str

    for tag in xml_tree.iter():
        if tag.text in paths_dict.keys():
            tag.text = paths_dict[str(tag.text)]

    print("Start with fast XML upload...")
    start_time = datetime.now()

    xml_upload(
        input_file=xml_tree,
        server=dsp_url,
        user=user,
        password=password,
        imgdir=".",
        sipi=sipi_url,
        verbose=False,
        incremental=False,
        save_metrics=False,
        preprocessing_done=True
    )

    print(f"Total time of fast xml upload: {datetime.now() - start_time}")
    return True
