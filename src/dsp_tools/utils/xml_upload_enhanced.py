import concurrent.futures
import copy
import json
import os
import shutil
import warnings
from itertools import repeat
from pathlib import Path
import regex

import requests
from lxml import etree

from dsp_tools import excel2xml
from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import BaseError
from dsp_tools.utils.shared import try_network_action
from dsp_tools.utils.xml_upload import xml_upload

extensions: dict[str, list[str]] = dict()
extensions["image"] = [".jpg", ".jpeg", ".tif", ".tiff", ".jp2", ".png"]
# extensions["video"] = ["mp4"]
extensions["archive"] = [".7z", ".gz", ".gzip", ".tar", ".tar.gz", ".tgz", ".z", ".zip"]
extensions["text"] = [".csv", ".txt", ".xml", ".xsd", ".xsl"]
extensions["document"] = [".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx"]
extensions["audio"] = [".mp3", ".wav"]
all_extensions: list[str] = list()
[all_extensions.extend(ext) for ext in extensions.values()]
extension2restype = dict()
for ext in all_extensions:
    if ext in extensions.get("image", []):
        restype = ":ImageThing"
    elif ext in extensions.get("video", []):
        restype = ":MovieThing"
    elif ext in extensions.get("archive", []):
        restype = ":ZipThing"
    elif ext in extensions.get("text", []):
        restype = ":TextThing"
    elif ext in extensions.get("document", []):
        restype = ":DocumentThing"
    elif ext in extensions.get("audio", []):
        restype = ":AudioThing"
    else:
        raise BaseError("Invalid extension")
    extension2restype[ext] = restype


def generate_testdata() -> None:
    """
    Creates a test data folder in the user's current working directory.

    Returns:
        None
    """
    testproject = Path("enhanced-xmlupload-testproject")
    if testproject.exists():
        print("The test project folder is already existing.")
        return

    all_paths: list[Path] = list()

    # generate multimedia folder
    destinations = [
        testproject / "multimedia",
        testproject / "multimedia" / "nested",
        testproject / "multimedia" / "nested" / "subfolder"
    ]
    for sub in destinations:
        sub.mkdir(parents=True)
    github_bitstreams_path = "https://github.com/dasch-swiss/dsp-tools/blob/main/testdata/bitstreams"
    for ext in all_extensions:
        file = requests.get(f"{github_bitstreams_path}/test{ext}?raw=true").content
        for dst in destinations:
            dst_file = dst / f"test{ext}"
            all_paths.append(dst_file.relative_to(testproject))
            with open(dst_file, "bw") as f:
                f.write(file)
    print(f"Successfully created folder {testproject}")

    # generate an XML file that uses these files
    root = excel2xml.make_root(shortcode="4123", default_ontology="testonto")
    root = excel2xml.append_permissions(root)
    for filepath in all_paths:
        resource = excel2xml.make_resource(
            label=str(filepath),
            restype=extension2restype[filepath.suffix],
            id=excel2xml.make_xsd_id_compatible(str(filepath))
        )
        warnings.filterwarnings("ignore")
        resource.append(excel2xml.make_bitstream_prop(filepath))
        root.append(resource)
    excel2xml.write_xml(root, str(testproject / "data.xml"))

    # download and adapt JSON project file from dsp-tools testdata
    json_text = requests.get(
        "https://github.com/dasch-swiss/dsp-tools/blob/main/testdata/test-project-systematic.json?raw=true").text
    json_text = json_text.replace('"cardinality": "1"', '"cardinality": "0-n"')
    json_text = json_text.replace('"cardinality": "1-n"', '"cardinality": "0-n"')
    with open(testproject / "data_model.json", "x") as f:
        f.write(json_text)


def parse_and_check_xml_file(
    xmlfile: str,
    multimedia_folder: str
) -> etree.ElementTree:   # type: ignore
    """
    Parse XML file and verify that all multimedia files referenced in it are contained in multimedia_folder
    (or one of its subfolders), and that all files contained in multimedia_folder are referenced in the XML file.

    Args:
        xmlfile: path to the XML file
        multimedia_folder: path to the multimedia folder

    Returns:
        lxml.etree.ElementTree of the XML file
    """
    tree = etree.parse(xmlfile)
    bitstream_paths = [x.text for x in tree.iter()
                       if etree.QName(x).localname.endswith("bitstream") and x.text is not None]
    filesystem_paths = [str(x) for x in Path().glob(f"{multimedia_folder}/**/*.*") if x.name != ".DS_Store"]
    if sorted(bitstream_paths) != sorted(filesystem_paths):
        print("The multimedia folder and the XML file don't contain the same files!")
        # exit(1)
    else:
        print("Check passed: Your XML file contains the same multimedia files than your multimedia folder.")

    return tree


def make_batches(multimedia_folder: str) -> list[list[Path]]:
    """
    Read all multimedia files contained in multimedia_folder and its subfolders,
    take the images and divide them into batches.

    Args:
        multimedia_folder: path to the folder containing the multimedia files

    Returns:
        a list of batches, each batch being a list of Paths
    """
    # collect all paths
    path_to_size: dict[Path, float] = dict()
    for pth in Path().glob(f"{multimedia_folder}/**/*.*"):
        path_to_size[pth] = round(pth.stat().st_size / 1_000_000, 1)
    all_paths = sorted(path_to_size.keys(), key=lambda x: path_to_size[x])

    # concurrent.futures.ThreadPoolExecutor() works with min(32, os.cpu_count() + 4) threads
    # (see https://docs.python.org/3.10/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor),
    # so the ideal number of batches is equal to the number of available threads
    num_of_batches = min(32, os.cpu_count() + 4, len(all_paths))  # type: ignore

    # make batches
    average_batch_size = sum(path_to_size.values()) / num_of_batches
    undistributed_paths = copy.copy(all_paths)
    batches: list[tuple[list[Path], float]] = [(([]), 0.0) for _ in range(num_of_batches)]
    for i in range(num_of_batches):
        next_path = all_paths[i]
        batches[i] = ([next_path, ], path_to_size[next_path])
        undistributed_paths.remove(next_path)
    i=0
    while undistributed_paths:
        if batches[i][1] < average_batch_size:
            next_path = undistributed_paths[0]
            pathlist, size = batches[i]
            pathlist.append(next_path)
            size += path_to_size[next_path]
            batches[i] = (pathlist, size)
            undistributed_paths.remove(next_path)
        i = (i + 1) % num_of_batches

    # verify that content of batches is equal to the originally found paths
    finished_batches = [batch[0] for batch in batches]
    paths_in_batches = list()
    [paths_in_batches.extend(batch) for batch in finished_batches]
    assert sorted(paths_in_batches) == sorted(all_paths)

    print(f"Found {len(all_paths)} files in folder '{multimedia_folder}'. Prepared {num_of_batches} batches as follows:")
    for number, batch in enumerate(batches):
        pathlist, size = batch
        print(f" - Batch no. {number + 1:2d}: {len(pathlist)} files with a total size of {size:.1f} MB")

    return finished_batches


def make_preprocessing(
    batch: list[Path],
    local_sipi_port: int,
    remote_sipi_server: str,
    con: Connection
) -> tuple[dict[str, str], list[Path]]:
    """
    Sends the multimedia files contained in batch to the /upload route of the local SIPI instance,
    creates a mapping of the original filepath to the SIPI-internal filename and the checksum,
    and returns the mapping for the successfully processed files,
    together with a list of the failed original filepaths.

    Args:
        batch: list of paths to image files
        local_sipi_port: port number of SIPI
        remote_sipi_server: str

    Returns:
        mapping, failed_batch_items
    """
    mapping: dict[str, str] = dict()
    failed_batch_items = list()
    for pth in batch:
        with open(pth, "rb") as bitstream:
            response_raw = requests.post(url=f"http://localhost:{local_sipi_port}/upload", files={"file": bitstream})
        response = json.loads(response_raw.text)
        if response.get("message") == "server.fs.mkdir() failed: File exists":
            failed_batch_items.append(pth)
            continue
        internal_filename = response["uploadedFiles"][0]["internalFilename"]
        mapping[str(pth)] = internal_filename
        original_extension = pth.suffix
        deriv = ".jp2" if original_extension in extensions["image"] else original_extension
        for ext in [".info", deriv, f"{original_extension}.orig"]:
            upload_candidate = f"tmp/{Path(internal_filename).stem}{ext}"
            with open(upload_candidate, "rb") as bitstream:
                response_upload = requests.post(url=f"{regex.sub(r'/$', '', remote_sipi_server)}/upload_without_transcoding?token={con.get_token()}", files={"file": bitstream})
            if not response_upload.json().get("uploadedFiles"):
                raise BaseError(f"File {upload_candidate} ({pth!s}) could not be uploaded. The API response was: {response_upload.text}")
        print(f"Uploaded {pth!s}")

    return mapping, failed_batch_items


def preprocess_batch(batch: list[Path], local_sipi_port: int, remote_sipi_server: str, con: Connection) -> dict[str, str]:
    """
    Create JP2 and sidecar files of the images contained in one batch.

    Args:
        batch: list of paths to image files
        local_sipi_port: port number of SIPI
        remote_sipi_server: the DSP server where the data should be imported
        con: connection to the remote DSP server

    Returns:
        mapping of original filepaths to internal filenames
    """
    mapping, failed_batch_items = make_preprocessing(batch=batch,local_sipi_port=local_sipi_port, remote_sipi_server=remote_sipi_server, con=con)
    while len(failed_batch_items) != 0:
        print(f"\tRetry the following failed files: {[str(x) for x in failed_batch_items]}")
        mapping_addition, failed_batch_items = make_preprocessing(batch=failed_batch_items, local_sipi_port=local_sipi_port, remote_sipi_server=remote_sipi_server, con=con)
        mapping.update(mapping_addition)
    return mapping


def write_preprocessed_xml_file(xml_file_tree: etree.ElementTree, mapping: dict[str, str], xmlfile: str) -> None:   # type: ignore
    """
    Make a copy of the XML file with the filepaths replaced by the UUID.

    Args:
        xml_file_tree: etree representation of the original XML document
        mapping: mapping from the original filepaths to the internal filenames

    Returns:
        None
    """
    for elem in xml_file_tree.iter():  # type: ignore
        if elem.text in mapping:
            elem.text = mapping[elem.text]
    xml_string = etree.tostring(xml_file_tree, encoding="unicode", pretty_print=True)
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
    with open(f"{Path(xmlfile).stem}-preprocessed.xml", "w", encoding="utf-8") as f:
        f.write(xml_string)


def enhanced_xml_upload(
    multimedia_folder: str,
    local_sipi_port: int,
    server: str,
    user: str,
    password: str,
    remote_sipi_server: str,
    verbose: bool,
    incremental: bool,
    xmlfile: str
) -> None:
    """
    Before starting the regular xmlupload, 
    preprocess the multimedia files with a local SIPI instance in multithreading, 
    and send the preprocessed files to the DSP server.

    Args:
        multimedia_folder: name of the folder containing the multimedia files
        local_sipi_port: 5-digit port number of the local SIPI instance, can be found in the "Container" view of Docker Desktop
        server: the DSP server where the data should be imported
        user: username used for authentication with the DSP-API
        password: password used for authentication with the DSP-API
        remote_sipi_server: URL of the remote SIPI IIIF server
        verbose: If set, more information about the process is printed to the console.
        incremental: If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
        xmlfile: path to xml file containing the data

    Returns:
        None
    """
    xml_file_tree = parse_and_check_xml_file(xmlfile=xmlfile, multimedia_folder=multimedia_folder)

    batches = make_batches(multimedia_folder=multimedia_folder)

    con = Connection(server)
    try_network_action(failure_msg="Unable to login to DSP server", action=lambda: con.login(user, password))

    mapping = dict()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        batchgroup_mappings = executor.map(preprocess_batch, batches, repeat(local_sipi_port), repeat(remote_sipi_server), repeat(con))
    for mp in batchgroup_mappings:
        mapping.update(mp)

    write_preprocessed_xml_file(xml_file_tree=xml_file_tree, mapping=mapping, xmlfile=xmlfile)

    print("Preprocessing sucessfully finished! Start with regular xmlupload...")

    xml_upload(
        input_file=f"{Path(xmlfile).stem}-preprocessed.xml",
        server=server,
        user=user,
        password=password,
        imgdir=".",
        sipi=remote_sipi_server,
        verbose=verbose,
        incremental=incremental,
        save_metrics=False,
        preprocessing_done=True
    )

    shutil.rmtree("tmp", ignore_errors=True)
    Path(f"{Path(xmlfile).stem}-preprocessed.xml").unlink()

# Ideas how to improve the multithreading:
# - should the images be distributed into groups according to size?
# - could we optimize it with
#   https://docs.python.org/3.10/library/concurrent.futures.html#concurrent.futures.as_completed?
# - should we use the max_workers argument? See here:
#   https://docs.python.org/3.10/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor:
#   Default value of max_workers is changed to min(32, os.cpu_count() + 4).
#   This default value preserves at least 5 workers for I/O bound tasks.
#   It utilizes at most 32 CPU cores for CPU bound tasks which release the GIL.
#   And it avoids using very large resources implicitly on many-core machines.
#   ThreadPoolExecutor now reuses idle worker threads before starting max_workers worker threads too.
