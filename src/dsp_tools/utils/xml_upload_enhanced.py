import glob
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import uuid
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path, PurePath
from typing import Union, Any, Tuple

import docker
import regex
import requests
from docker.models.resource import Model
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
        print("The test project folder already exists.")
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
        "https://github.com/dasch-swiss/dsp-tools/blob/main/testdata/json-project/test-project-enhanced-xmlupload.json?raw=true").text
    json_text = json_text.replace('"cardinality": "1"', '"cardinality": "0-n"')
    json_text = json_text.replace('"cardinality": "1-n"', '"cardinality": "0-n"')
    with open(testproject / "data_model.json", "x") as f:
        f.write(json_text)
    print("Successfully created data_model.json")

    return True


def _parse_xml_file(xmlfile: str) -> tuple[etree._ElementTree, list[str]]:
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


def __upload_derivative(
    sipi_processed_path: str,
    orig_file: str,
    internal_filename: str,
    remote_sipi_server: str,
    con: Connection
) -> tuple[int, str]:
    upload_candidates: list[str] = []
    upload_candidates.extend(glob.glob(f"{Path(sipi_processed_path)}/{Path(internal_filename).stem}/**/*.*"))
    upload_candidates.extend(glob.glob(f"{Path(sipi_processed_path)}/{Path(internal_filename).stem}*.*"))

    orig_file_path = Path(orig_file)
    min_num_of_candidates = 5 if orig_file_path.suffix == ".mp4" else 3
    if len(upload_candidates) < min_num_of_candidates:
        raise BaseError(
            f"Local SIPI created the following files for {orig_file_path}, but more were expected: {upload_candidates}")

    for candidate in upload_candidates:
        with open(candidate, "rb") as bitstream:
            response_upload = requests.post(
                url=f"{regex.sub(r'/$', '', remote_sipi_server)}/upload_without_processing?token={con.get_token()}",
                files={"file": bitstream}
            )
        if not response_upload.json().get("uploadedFiles"):
            raise BaseError(
                f"File {candidate} ({orig_file_path!s}) could not be uploaded. The API response was: {response_upload.text}")

    print(f" - Uploaded {len(upload_candidates)} derivatives of {orig_file}")
    return len(upload_candidates), str(orig_file_path)


def __preprocess_file_2(
    in_file: Path,
    out_dir: Path
):
    out_dir.mkdir(parents=True, exist_ok=True)
    orig, converted = process_file(in_file, out_dir)
    return orig, converted


def __preprocess_file(
    orig_file: str,
    local_sipi_server: str,
) -> tuple[Path, str]:
    """
    Sends a multimedia file to the SIPI /upload_for_processing route of the
    local DSP stack.

    Args:
        orig_file: file to process
        local_sipi_server: URL of the local SIPI IIIF server

    Returns:
        tuple consisting of the original path and the SIPI-internal filename
    """

    with open(orig_file, "rb") as bitstream:
        response_raw = requests.post(
            url=f"{local_sipi_server}/upload_for_processing",
            files={"file": bitstream}
        )
    response = json.loads(response_raw.text)
    if response.get("uploadedFiles", [{}])[0].get("internalFilename"):
        internal_filename: str = response["uploadedFiles"][0]["internalFilename"]
    elif response.get("message") == "server.fs.mkdir() failed: File exists":
        _, internal_filename = __preprocess_file(orig_file=orig_file, local_sipi_server=local_sipi_server)
    else:
        raise BaseError(
            f"File {orig_file} couldn't be handled by the /upload_for_processing route of the local SIPI. Error message: {response['message']}")
    return orig_file, internal_filename


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

    con = Connection(remote_dsp_server)
    try_network_action(lambda: con.login(user, password))

    print(f"{datetime.now()}: Start preprocessing and uploading the multimedia files...")
    start_multithreading_time = datetime.now()
    orig_filepath_2_uuid: dict[str, str] = dict()

    # create processing thread pool
    with ThreadPoolExecutor(processing_threads, "processing") as e1:
        # add processing jobs to pool
        # processing_jobs = [e1.submit(
        #     __preprocess_file,
        #     orig_file,
        #     local_sipi_server
        # ) for orig_file in all_paths]
        processing_jobs = [e1.submit(
            __preprocess_file_2,
            Path(orig_file),
            Path(sipi_processed_path)
        ) for orig_file in all_paths]

        with ThreadPoolExecutor(uploading_threads, "upload") as e2:
            # wait for a processing job to complete and add upload job to pool
            uploading_jobs = []
            for processed in as_completed(processing_jobs):
                try:
                    orig_file, internal_filename = processed.result()
                    orig_filepath_2_uuid[orig_file] = str(internal_filename)
                    uploading_jobs.append(
                        e2.submit(
                            __upload_derivative,
                            sipi_processed_path,
                            orig_file,
                            str(internal_filename),
                            remote_sipi_server,
                            con
                        )
                    )
                except Exception as ex:
                    print(f"processing generated an exception: {ex}")
                else:
                    print(f" - Successfully preprocessed {orig_file} with internal filename: {internal_filename}")

    for uploaded in as_completed(uploading_jobs):
        try:
            uploaded.result()
        except Exception as ex:
            print(f"upload generated an exception: {ex}")

    end_multithreading_time = datetime.now()
    multithreading_duration = end_multithreading_time - start_multithreading_time
    print(
        f"Time of multithreading (with {processing_threads} threads for preprocessing and {uploading_threads} threads for uploading): {multithreading_duration.seconds} seconds")

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



def get_file_paths_from_xml(xml_file: Path) -> list[str]:
    """
    Parse XML file to get all file paths.

    Args:
        xml_file: path to the XML file

    Returns:
        list of all paths in the <bitstream> tags
    """
    tree: etree._ElementTree = etree.parse(xml_file)
    bitstream_paths = [x.text for x in tree.iter()
                       if etree.QName(x).localname.endswith("bitstream") and x.text is not None]
    return bitstream_paths


def get_sipi_container() -> Union[Model, Any]:
    """
    Checks the locally running containers and returns the Sipi container

    Returns:
        the sipi container
    """
    docker_client = docker.from_env()
    containers = docker_client.containers.list()
    for c in containers:
        if "sipi" in c.name:
            return c


def compute_sha256(file: Path):
    """
    Calculates SHA256 checksum of a file

    Args:
        file: path of the file

    Returns:
        the checksum
    """
    hash_sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def convert_file_with_sipi(in_file_local_path, out_file_local_path) -> bool:
    """
    Converts a file by calling a locally running Sipi container

    Args:
        in_file_local_path: input file
        out_file_local_path: output file
    """
    mounted_path_on_sipi = "images/tmp/"
    out_dir_sipi = "processed/"
    in_file_sipi_path = mounted_path_on_sipi + os.path.basename(in_file_local_path)  # images/tmp/test.tif
    out_file_sipi_path = mounted_path_on_sipi + out_dir_sipi + os.path.basename(
        out_file_local_path)  # images/tmp/processed/76c99684-354f-4e8c-9c20-2b25901a1862.jp2
    sipi_container = get_sipi_container()
    # result = sipi_container.exec_run(f"/sipi/sipi --topleft {in_file_sipi_path} {out_file_sipi_path}")
    result = sipi_container.exec_run(f"/sipi/sipi {in_file_sipi_path} {out_file_sipi_path}")
    if result.exit_code != 0:
        print("Sipi image conversion failed:", result)
        return False
    return True


def create_orig_file(in_file, random_file_name, out_dir):
    """
    Creates the .orig file expected by the API.

    Args:
        in_file ():
        random_file_name ():
        out_dir ():
    """
    orig_ext = PurePath(in_file).suffix  # .tif
    orig_file_basename = f"{random_file_name}{orig_ext}.orig"
    orig_file = PurePath(out_dir, orig_file_basename)
    shutil.copyfile(in_file, orig_file)


def get_video_metadata_with_ffprobe(file_path):
    command_array = ["ffprobe",
                     "-v",
                     "error",
                     "-select_streams", "v:0",
                     "-show_entries",
                     "stream=width,height,bit_rate,duration,nb_frames,r_frame_rate",
                     "-print_format", "json",
                     "-i",
                     file_path]
    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    video_metadata = json.loads(result.stdout)['streams'][0]  # get first stream
    return video_metadata


def create_sidecar_file(
    orig_file: Path,
    converted_file: Path,
    out_dir: Path,
    file_category: str):
    if file_category not in ("IMAGE", "VIDEO", "OTHER"):
        raise BaseError(f"Unexpected file category {file_category}")

    original_filename = PurePath(orig_file).name  # test.tif

    checksum_original = compute_sha256(orig_file)
    checksum_derivative = compute_sha256(converted_file)

    internal_filename = PurePath(converted_file).name
    random_part_of_filename = PurePath(converted_file).stem
    original_extension = PurePath(orig_file).suffix
    original_internal_filename = f"{random_part_of_filename}{original_extension}.orig"
    sidecar_dict = {"originalFilename": original_filename,
                    "checksumOriginal": checksum_original,
                    "checksumDerivative": checksum_derivative,
                    "internalFilename": internal_filename,
                    "originalInternalFilename": original_internal_filename}

    if file_category == "VIDEO":
        video_metadata = get_video_metadata_with_ffprobe(converted_file)
        sidecar_dict["width"] = video_metadata["width"]
        sidecar_dict["height"] = video_metadata["height"]
        sidecar_dict["duration"] = float(video_metadata["duration"])
        nb_frames = int(video_metadata["nb_frames"])
        duration = float(video_metadata["duration"])
        fps = nb_frames / duration
        sidecar_dict["fps"] = fps

    sidecar_json = json.dumps(sidecar_dict, indent=4)

    sidecar_file_basename = f"{random_part_of_filename}.info"
    sidecar_file = PurePath(out_dir, sidecar_file_basename)

    with open(sidecar_file, "w") as f:
        f.write(sidecar_json)


def get_file_category(file: Path):
    IMAGE_JP2 = "image/jp2"
    IMAGE_JPX = "image/jpx"
    IMAGE_TIFF = "image/tiff"
    IMAGE_PNG = "image/png"
    IMAGE_JPG = "image/jpeg"
    APPLICATION_XML = "application/xml"
    TEXT_XML = "text/xml"
    TEXT_PLAIN = "text/plain"
    TEXT_CSV = "text/csv"
    AUDIO_MP3 = "audio/mpeg"
    AUDIO_WAV = "audio/wav"
    AUDIO_X_WAV = "audio/x-wav"
    AUDIO_VND_WAVE = "audio/vnd.wave"
    APPLICATION_CSV = "application/csv"
    APPLICATION_PDF = "application/pdf"
    APPLICATION_DOC = "application/msword"
    APPLICATION_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    APPLICATION_XLS = "application/vnd.ms-excel"
    APPLICATION_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    APPLICATION_PPT = "application/vnd.ms-powerpoint"
    APPLICATION_PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    APPLICATION_ZIP = "application/zip"
    APPLICATION_TAR = "application/x-tar"
    APPLICATION_GZIP = "application/gzip"
    APPLICATION_7Z = "application/x-7z-compressed"
    APPLICATION_TGZ = "application/x-compress"
    APPLICATION_Z = "application/x-compress"
    VIDEO_MP4 = "video/mp4"

    image_mimetypes = [IMAGE_JP2,
                       IMAGE_JPG,
                       IMAGE_JPX,
                       IMAGE_PNG,
                       IMAGE_TIFF]
    video_mimetypes = [VIDEO_MP4]
    other_mimetypes = [AUDIO_MP3,
                       AUDIO_VND_WAVE,
                       AUDIO_WAV,
                       AUDIO_X_WAV,
                       APPLICATION_CSV,
                       APPLICATION_XML,
                       TEXT_CSV,
                       TEXT_PLAIN,
                       TEXT_XML,
                       APPLICATION_DOC,
                       APPLICATION_DOCX,
                       APPLICATION_PDF,
                       APPLICATION_PPT,
                       APPLICATION_PPTX,
                       APPLICATION_XLS,
                       APPLICATION_XLSX,
                       APPLICATION_7Z,
                       APPLICATION_GZIP,
                       APPLICATION_TAR,
                       APPLICATION_TGZ,
                       APPLICATION_Z,
                       APPLICATION_ZIP
                       ]

    # image_extensions = []
    # video_extensions = ["mp4"]
    # other_extensions = ["mp3", "wav", "csv",
    #                     "odd", "rng", "txt",
    #                     "xml", "xsd", "xsl", "doc",
    #                     "docx", "pdf", "ppt", "pptx",
    #                     "xls", "xlsx", "7z", "gz",
    #                     "gzip", "tar", "tgz", "z", "zip"]

    mimetype, _ = mimetypes.guess_type(file)

    if mimetype in video_mimetypes:
        category = "VIDEO"
    elif mimetype in image_mimetypes:
        category = "IMAGE"
    elif mimetype in other_mimetypes:
        category = "OTHER"
    else:
        category = None
    return category


def extract_key_frames(file: Path):
    result = subprocess.call(['sh', '/Users/irina/GitHub/dsp-tools/export-moving-image-frames.sh', '-i', file])
    if result != 0:
        raise BaseError(f"Something happened while extracting frames from: {file}")


def process_file(
    in_file: Path,
    out_dir: Path
) -> tuple[Path, Path]:
    """
    Sends a file to SIPI to convert it. Creates a derivative, an original file and a sidecar file.

    Args:
        in_file: path to file
        out_dir: target location of processed files (.../images/tmp/processed)

    Returns:
        tuple consisting of the original path and the SIPI-internal filename
    """

    random_uuid = uuid.uuid4()

    # create .orig file
    create_orig_file(in_file, random_uuid, out_dir)

    # convert file (create derivative) and create sidecar file based on category (image, video or other)
    file_category = get_file_category(in_file)
    if file_category == "OTHER":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(random_uuid) + ext
        converted_file = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file)
        create_sidecar_file(in_file, converted_file, out_dir, file_category)
    elif file_category == "IMAGE":
        ext = ".jp2"
        converted_file_basename = str(random_uuid) + ext
        converted_file = out_dir / converted_file_basename
        convert_file_with_sipi(in_file, converted_file)
        create_sidecar_file(in_file, converted_file, out_dir, file_category)
    elif file_category == "VIDEO":
        ext = PurePath(in_file).suffix
        converted_file_basename = str(random_uuid) + ext
        converted_file = out_dir / converted_file_basename
        shutil.copyfile(in_file, converted_file)
        extract_key_frames(converted_file)
        create_sidecar_file(in_file, converted_file, out_dir, file_category)
    else:
        raise BaseError(f"Unexpected file category: {file_category}")

    return in_file, converted_file
