import concurrent.futures
import glob
import json
import shutil
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import regex
import requests
from lxml import etree

from dsp_tools import excel2xml
from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import BaseError
from dsp_tools.utils.shared import try_network_action
from dsp_tools.utils.xml_upload import xml_upload

tmp_location = Path.home() / Path(".dsp-tools")
tmp_location.mkdir(exist_ok=True)

extensions: dict[str, list[str]] = dict()
extensions["image"] = [".jpg", ".jpeg", ".tif", ".tiff", ".jp2", ".png"]
extensions["video"] = [".mp4"]
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


def generate_testdata(size: str) -> bool:
    """
    Creates a test data folder in the user's current working directory.

    Args:
        size: size of test data set: small/medium/big

    Returns:
        success status
    """
    testproject = Path("enhanced-xmlupload-testproject")
    if testproject.exists():
        print("The test project folder is already existing.")
        return False

    all_paths: list[Path] = list()

    # generate multimedia folder
    destinations = [
        testproject / "multimedia",
        testproject / "multimedia" / "nested",
        testproject / "multimedia" / "nested" / "subfolder"
    ]
    for sub in destinations:
        sub.mkdir(parents=True)

    # download small samples of every supported file type
    github_bitstreams_path = "https://github.com/dasch-swiss/dsp-tools/blob/main/testdata/bitstreams"
    for ext in all_extensions:
        file = requests.get(f"{github_bitstreams_path}/test{ext}?raw=true").content
        for dst in destinations:
            dst_file = dst / f"test{ext}"
            all_paths.append(dst_file.relative_to(testproject))
            with open(dst_file, "bw") as f:
                f.write(file)
    print(f"Successfully created folder {testproject}/multimedia")
    
    # download big files of some few file types
    if size != "small":
        big_files_dict = {
            "videos": {
                "https://filesamples.com/samples/video/mp4/sample_960x400_ocean_with_audio.mp4": 16.71,
                "https://filesamples.com/samples/video/mp4/sample_1280x720_surfing_with_audio.mp4": 68.43
            },
            "audios": {
                "https://filesamples.com/samples/audio/mp3/Symphony%20No.6%20(1st%20movement).mp3": 11.11,
                "https://filesamples.com/samples/audio/mp3/sample4.mp3": 3.73,
                "https://filesamples.com/samples/audio/mp3/sample3.mp3": 1.61
            },
            "documents": {
                "https://filesamples.com/samples/document/pdf/sample3.pdf": 1.2
            },
            "images": {
                "https://www.sampledocs.in/DownloadFiles/SampleFile?filename=sampleDocs%20tree%20background%20image&ext=jpg": 10,
                "https://www.sampledocs.in/DownloadFiles/SampleFile?filename=Doctors-Image-22&ext=jpg": 1
            }
        }
        big_files: dict[str, float] = dict()
        [big_files.update(_dict) for _dict in big_files_dict.values()]
        for url, filesize in big_files.items():
            file = requests.get(url).content
            multiplication_rate = 2 if size == "big" else 1
            for i in range(multiplication_rate):
                for dst in destinations:
                    dst_file = dst / f"big_file_{filesize}_mb_{i}.{url[-3:]}"
                    all_paths.append(dst_file.relative_to(testproject))
                    with open(dst_file, "bw") as f:
                        f.write(file)

    # generate an XML file that uses these files
    root = excel2xml.make_root(shortcode="00E0", default_ontology="testonto")
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
        "https://github.com/dasch-swiss/dsp-tools/blob/main/testdata/test-project-enhanced-xmlupload.json?raw=true").text
    json_text = json_text.replace('"cardinality": "1"', '"cardinality": "0-n"')
    json_text = json_text.replace('"cardinality": "1-n"', '"cardinality": "0-n"')
    with open(testproject / "data_model.json", "x") as f:
        f.write(json_text)
    print("Successfully created data_model.json")
    
    return True


def _parse_xml_file(xmlfile: str) -> tuple[etree._ElementTree, list[Path]]:
    """
    Parse XML file 

    Args:
        xmlfile: path to the XML file

    Returns:
        tuple consisting of the lxml.etree.ElementTree of the XML file, and the list of all paths in the <bistream> tags
    """
    tree: etree._ElementTree = etree.parse(xmlfile)
    bitstream_paths = [x.text for x in tree.iter()
                       if etree.QName(x).localname.endswith("bitstream") and x.text is not None]
    return tree, bitstream_paths


def _upload_derivates(
    orig_path: Path, 
    internal_filename: str,
    remote_sipi_server: str,
    con: Connection
) -> None:
    upload_candidates: list[str] = []
    upload_candidates.extend(glob.glob(f"{tmp_location}/tmp/{Path(internal_filename).stem}/**/*.*"))
    upload_candidates.extend(glob.glob(f"{tmp_location}/tmp/{Path(internal_filename).stem}*.*"))
    min_num_of_candidates = 5 if orig_path.suffix == "mp4" else 3
    if len(upload_candidates) < min_num_of_candidates:
        raise BaseError(f"Local SIPI created only the following files for {orig_path}, which is too less: {upload_candidates}")
    for upload_candidate in upload_candidates:
        with open(upload_candidate, "rb") as bitstream:
            response_upload = requests.post(
                url=f"{regex.sub(r'/$', '', remote_sipi_server)}/upload_without_processing?token={con.get_token()}", 
                files={"file": bitstream}
            )
        if not response_upload.json().get("uploadedFiles"):
            raise BaseError(f"File {upload_candidate} ({orig_path!s}) could not be uploaded. The API response was: {response_upload.text}")
    print(f" - Uploaded {len(upload_candidates)} derivates of {orig_path!s}")


def _preprocess_file(
    path: Path,
    local_sipi_port: int,
) -> tuple[Path, str]:
    """
    Sends a multimedia file to the /upload route of the local SIPI instance.

    Args:
        batch: list of paths to image files
        local_sipi_port: port number of SIPI

    Returns:
        tuple consisting of the original path and the SIPI-internal filename
    """
    with open(path, "rb") as bitstream:
        response_raw = requests.post(url=f"http://localhost:{local_sipi_port}/upload", files={"file": bitstream})
    response = json.loads(response_raw.text)
    if response.get("uploadedFiles", [{}])[0].get("internalFilename"):
        internal_filename: str = response["uploadedFiles"][0]["internalFilename"]
        print(f" - Successfully preprocessed {path}")
    elif response.get("message") == "server.fs.mkdir() failed: File exists":
        _, internal_filename = _preprocess_file(path=path, local_sipi_port=local_sipi_port)
    else:
        raise BaseError(f"File {path} couldn't be handled by the /upload route of the local SIPI. Error message: {response['message']}")
    return path, internal_filename


def enhanced_xml_upload(
    local_sipi_port: int,
    remote_dsp_server: str,
    remote_sipi_server: str,
    num_of_threads_for_preprocessing: int,
    num_of_threads_for_uploading: int,
    user: str,
    password: str,
    xmlfile: str,
    verbose: bool,
    incremental: bool
) -> bool:
    """
    Before starting the regular xmlupload, 
    preprocess the multimedia files with a local SIPI instance in multithreading, 
    and send the preprocessed files to the DSP server.

    Args:
        local_sipi_port: 5-digit port number of the local SIPI instance, can be found in the "Container" view of Docker Desktop
        remote_dsp_server: the DSP server where the data should be imported
        remote_sipi_server: URL of the remote SIPI IIIF server
        num_of_threads_for_preprocessing: number of threads used for sending requests to the local SIPI
        num_of_threads_for_uploading: number of threads used for uploading the preprocessed files to the remote SIPI
        user: username used for authentication with the DSP-API
        password: password used for authentication with the DSP-API
        xmlfile: path to xml file containing the data
        verbose: If set, more information about the process is printed to the console.
        incremental: If true, IRIs instead of internal IDs are expected as reference to already existing resources on DSP

    Returns:
        success status
    """
    start_time = datetime.now()

    xml_file_tree, all_paths = _parse_xml_file(xmlfile=xmlfile)

    con = Connection(remote_dsp_server)
    try_network_action(failure_msg="Unable to login to DSP server", action=lambda: con.login(user, password))

    print(f"{datetime.now()}: Start preprocessing and uploading the multimedia files...")
    start_multithreading_time = datetime.now()
    orig_filepath_2_uuid: dict[str, str] = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_threads_for_preprocessing) as executor:
        futures: list[concurrent.futures.Future[Any]] = list()
        for path in all_paths:
            futures.append(
                executor.submit(
                    _preprocess_file, 
                    path=path, 
                    local_sipi_port=local_sipi_port, 
                )
            )
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_threads_for_uploading) as executor2:
            for future in concurrent.futures.as_completed(futures):
                orig_path, internal_filename = future.result()
                orig_filepath_2_uuid[str(orig_path)] = internal_filename
                executor2.submit(
                    _upload_derivates,
                    orig_path=orig_path, 
                    internal_filename=internal_filename,
                    remote_sipi_server=remote_sipi_server,
                    con=con
                )
    end_multithreading_time = datetime.now()
    multithreading_duration = end_multithreading_time - start_multithreading_time
    print(f"Time of multithreading: {multithreading_duration.seconds} seconds")

    for tag in xml_file_tree.iter():
        if tag.text in orig_filepath_2_uuid:
            tag.text = orig_filepath_2_uuid[tag.text]

    print("Preprocessing sucessfully finished! Start with regular xmlupload...")

    xml_upload(
        input_file=xml_file_tree,
        server=remote_dsp_server,
        user=user,
        password=password,
        imgdir=".",
        sipi=remote_sipi_server,
        verbose=verbose,
        incremental=incremental,
        save_metrics=False,
        preprocessing_done=True
    )

    duration = datetime.now() - start_time
    print(f"Total time of enhanced xmlupload: {duration.seconds} seconds")
    print(f"Time of multithreading: {multithreading_duration.seconds} seconds")

    shutil.rmtree(tmp_location / "tmp", ignore_errors=True)

    return True
