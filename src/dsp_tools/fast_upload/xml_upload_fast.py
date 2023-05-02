import pickle
from datetime import datetime
from pathlib import Path

from lxml import etree

from dsp_tools.utils.xml_upload import xml_upload


def _get_paths_from_pkl_file(pkl_file: Path) -> list[tuple[Path, Path]]:
    with open(pkl_file, 'rb') as file:
        orig_paths_2_processed_paths: list[tuple[Path, Path]] = pickle.load(file)
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
    This function reads an XML file 
    and imports the data described in it onto the DSP server, 
    using the fast XML upload method.
    Before using this method, 
    the original files must be processed by the processing step, 
    and uploaded by the upoad step.

    Args:
        xml_file: path to XML file containing the resources
        pkl_file: pickle file containing the mapping between the original files and the processed files,
                  e.g. Path('multimedia/nested/subfolder/test.tif'), Path('tmp/0b22570d-515f-4c3d-a6af-e42b458e7b2b.jp2')
        user: the user's e-mail for login into DSP
        password: the user's password for login into DSP
        dsp_url: URL to the DSP server
        sipi_url: URL to the Sipi server
    
    Returns:
        success status
    """

    xml_tree = etree.parse(xml_file)
    orig_paths_2_processed_paths = _get_paths_from_pkl_file(pkl_file=Path(pkl_file))

    paths_dict = dict()
    for orig_path, processed_path in orig_paths_2_processed_paths:
        orig_path_str = str(orig_path)
        orig_path_name_str = str(orig_path.name)
        processed_path_str = str(processed_path.name)
        if orig_path_name_str != processed_path_str:
            paths_dict[orig_path_str] = processed_path_str

    for tag in xml_tree.iter():
        if tag.text in paths_dict:
            tag.text = paths_dict[str(tag.text)]

    start_time = datetime.now()
    print(f"{start_time}: Start with fast XML upload...")

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

    end_time = datetime.now()
    print(f"{end_time}: Total time of fast xml upload: {end_time - start_time}")
    return True
