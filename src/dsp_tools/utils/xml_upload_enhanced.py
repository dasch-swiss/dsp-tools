import glob
import json
import os
import shutil
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import regex
import requests
from lxml import etree

from dsp_tools import excel2xml
from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import BaseError
from dsp_tools.utils.shared import login
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
for extension in extensions.values():
    all_extensions.extend(extension)
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
        big_files_dict: dict[str, dict[str, float]] = {
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
        "https://github.com/dasch-swiss/dsp-tools/blob/main/testdata/json-project/test-project-enhanced-xmlupload.json?raw=true").text
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
    bitstream_paths = [Path(x.text) for x in tree.iter()
                       if etree.QName(x).localname.endswith("bitstream") and x.text is not None]
    return tree, bitstream_paths


def __upload_derivative(
    sipi_processed_path: str,
    orig_file_path: Path,
    internal_filename: str,
    remote_sipi_server: str,
    con: Connection
) -> None:
    """
    Given an internal filename, retrieve all derivatives, and send them to the remote SIPI.

    Args:
        sipi_processed_path: Path to folder containing the processed  files
        orig_file_path: original filepath (for error messages and print statements)
        internal_filename: SIPI internal filename, given by SIPI during preprocessing
        remote_sipi_server: URL of the remote SIPI IIIF server
        con: connection to the remote server

    Raises:
        BaseError: If the number of derivatives is not plausible, or if a derivative could not be uploaded
    """
    # retrieve list of all derivatives 
    upload_candidates: list[str] = []
    upload_candidates.extend(glob.glob(f"{Path(sipi_processed_path)}/{Path(internal_filename).stem}/**/*.*"))
    upload_candidates.extend(glob.glob(f"{Path(sipi_processed_path)}/{Path(internal_filename).stem}*.*"))

    # make a plausibility check
    min_num_of_candidates = 5 if orig_file_path.suffix == ".mp4" else 3
    if len(upload_candidates) < min_num_of_candidates:
        raise BaseError(f"Local SIPI created only the following files for {orig_file_path}, which is too less: {upload_candidates}")

    # send every derivative to the remote SIPI
    for candidate in upload_candidates:
        with open(candidate, "rb") as bitstream:
            response_upload = requests.post(
                url=f"{regex.sub(r'/$', '', remote_sipi_server)}/upload_without_processing?token={con.get_token()}",
                files={"file": bitstream}
            )
        if not response_upload.json().get("uploadedFiles"):
            raise BaseError(f"File {candidate} ({orig_file_path!s}) could not be uploaded. The API response was: {response_upload.text}")

    print(f" - Uploaded {len(upload_candidates)} derivatives of {orig_file_path}")


def __preprocess_file(
    orig_file_path: Path,
    local_sipi_server: str,
) -> tuple[Path, str]:
    """
    Sends a multimedia file to the SIPI /upload_for_processing route of the
    local DSP stack.

    Args:
        orig_file_path: file to process
        local_sipi_server: URL of the local SIPI IIIF server

    Returns:
        tuple consisting of the original path and the SIPI-internal filename
    """

    with open(orig_file_path, "rb") as bitstream:
        response_raw = requests.post(
            url=f"{local_sipi_server}/upload_for_processing",
            files={"file": bitstream}
        )
    response = json.loads(response_raw.text)
    if response.get("uploadedFiles", [{}])[0].get("internalFilename"):
        internal_filename: str = response["uploadedFiles"][0]["internalFilename"]
    elif response.get("message") == "server.fs.mkdir() failed: File exists":
        _, internal_filename = __preprocess_file(orig_file_path=orig_file_path, local_sipi_server=local_sipi_server)
    else:
        raise BaseError(f"File {orig_file_path} couldn't be handled by the /upload_for_processing route of the local SIPI. Error message: {response['message']}")
    return orig_file_path, internal_filename


def enhanced_xml_upload(
    local_sipi_server: str,
    sipi_processed_path: str,
    remote_dsp_server: str,
    remote_sipi_server: str,
    processing_threads: int,
    uploading_threads: int,
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
        local_sipi_server: URL of the local SIPI IIIF server
        sipi_processed_path: Path to folder containing the processed  files
        remote_dsp_server: the DSP server where the data should be imported
        remote_sipi_server: URL of the remote SIPI IIIF server
        processing_threads: number of threads used for sending requests to the local SIPI
        uploading_threads: number of threads used for uploading the preprocessed files to the remote SIPI
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

    con = login(remote_dsp_server, user, password)

    start_multithreading_time = datetime.now()
    print(f"{start_multithreading_time}: Start preprocessing and uploading the multimedia files...")
    orig_filepath_2_uuid: dict[Path, str] = dict()

    # create processing thread pool
    with ThreadPoolExecutor(max_workers=processing_threads, thread_name_prefix="processing") as e1:
        # add processing jobs to pool
        processing_jobs = [e1.submit(
            __preprocess_file,
            orig_file_path,
            local_sipi_server
        ) for orig_file_path in all_paths]

        with ThreadPoolExecutor(max_workers=uploading_threads, thread_name_prefix="upload") as e2:
            # wait for a processing job to complete and add upload job to pool
            uploading_jobs = []
            for processed in as_completed(processing_jobs):
                try:
                    orig_file_path, internal_filename = processed.result()
                    orig_filepath_2_uuid[orig_file_path] = internal_filename
                    uploading_jobs.append(
                        e2.submit(
                            __upload_derivative,
                            sipi_processed_path,
                            orig_file_path,
                            internal_filename,
                            remote_sipi_server,
                            con
                        )
                    )
                except Exception as ex:
                    print(f"processing generated an exception: {ex}")
                else:
                    print(f" - Successfully preprocessed '{orig_file_path}' with internal filename '{internal_filename}'")

    # retrieve results of upload jobs, see if there was an exception
    for uploaded in as_completed(uploading_jobs):
        try:
            uploaded.result()
        except Exception as ex:
            print(f"upload generated an exception: {ex}")

    end_multithreading_time = datetime.now()
    multithreading_duration = end_multithreading_time - start_multithreading_time
    print(f"Time of multithreading (with {processing_threads} threads for preprocessing and {uploading_threads} threads for uploading): {multithreading_duration.seconds} seconds")

    # in the XML, replace the original file paths with the internal filenames
    for tag in xml_file_tree.iter():
        if tag.text in orig_filepath_2_uuid:
            tag.text = orig_filepath_2_uuid[tag.text]

    print("Preprocessing successfully finished! Start with regular xmlupload...")

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

    # tidy up the folder with the preprocessed files
    for filename in os.listdir(sipi_processed_path):
        file_path = os.path.join(sipi_processed_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))

    return True
