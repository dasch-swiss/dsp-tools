import shutil
from typing import Tuple
import requests
from itertools import repeat
import concurrent.futures
from pathlib import Path
import os
import json


def generate_testdata() -> None:
    """
    Creates a test data folder in the user's current working directory.

    Returns:
        None
    """
    testproject = Path(os.getcwd()) / "enhanced-xmlupload-testproject"
    if testproject.exists():
        print("The test project folder is already existing.")
        return
    destinations = [
        testproject / "multimedia",
        testproject / "multimedia" / "nested",
        testproject / "multimedia" / "nested" / "subfolder"
    ]
    for sub in destinations:
        sub.mkdir(parents=True)
    github_bitstreams_path = "https://github.com/dasch-swiss/dsp-tools/blob/main/testdata/bitstreams"
    ext_img = ["jpg", "jpeg", "tif", "tiff", "jp2", "png"]
    for ext in ext_img:
        img = requests.get(f"{github_bitstreams_path}/test.{ext}?raw=true").content
        for dst in destinations:
            with open(dst / f"test.{ext}", "bw") as f:
                f.write(img)
    print(f"Successfully created folder {testproject}")

    # TODO: generate an XML file that uses these files


def check_multimedia_folder(
    xmlfile: str,
    multimedia_folder: str
) -> bool:
    """
    Verify that all multimedia files referenced in the XML file are contained in multimedia_folder
    (or one of its subfolders), and that all files contained in multimedia_folder are referenced in the XML file.
    """

    # TODO
    return True


def make_batches(multimedia_folder: str) -> Tuple[list[list[Path]], int]:
    """
    Make 32 portions (batches) out of all images in the multimedia folder, one batch per thread.
    A batch is a list of file paths.

    Returns:
        batches, batch size
    """
    # TODO: Vij is working on this. This is only a mock-up
    batches = [
        [x for x in Path(multimedia_folder).iterdir() if x.is_file()],
        [x for x in Path(multimedia_folder + "/nested").iterdir() if x.is_file()],
        [x for x in Path(multimedia_folder + "/nested/subfolder").iterdir() if x.is_file()]
    ]
    batch_size = 6
    return batches, batch_size


def make_preprocessing(
    batch: list[Path],
    sipi_port: int
) -> Tuple[dict[str, list[str]], list[str], list[Path]]:
    """
    Sends the images contained in batch to the /upload route of SIPI,
    creates a mapping of the original filepath to the SIPI-internal filename and the checksum,
    and returns the mapping for the successfully processed files,
    together with a list of the failed original filepaths.

    Args:
        batch: list of paths to image files
        sipi_port: port number of SIPI

    Returns:
        mapping, internal_filename_stems, failed_batch_items
    """
    mapping: dict[str, list[str]] = dict()
    internal_filename_stems = list()
    failed_batch_items = list()
    for imgpath in batch:
        response_raw = requests.post(
            url=f'http://localhost:{sipi_port}/upload',
            files={'file': open(imgpath, 'rb')}
        )
        response = json.loads(response_raw.text)
        if response.get("message") == "server.fs.mkdir() failed: File exists":
            # TODO: This happens sometimes. Probably a multithreading issue. I hope my handling of it is appropriate!
            failed_batch_items.append(imgpath)
        else:
            checksum = response["uploadedFiles"][0]["checksumDerivative"]
            internal_filename = response["uploadedFiles"][0]["internalFilename"]
            mapping[str(imgpath)] = [internal_filename, checksum]
            internal_filename_stems.append(Path(internal_filename).stem)

    return mapping, internal_filename_stems, failed_batch_items


def process_seq(batch: list[Path], batch_id: int, sipi_port: int) -> None:
    """
    Process the images contained in one batch:
    create JP2 and sidecar files,
    pack them into a ZIP together with the original files
    (one ZIP per batch)

    Args:
        batch: list of paths to image files
        batch_id: ID of the batch
        sipi_port: port number of SIPI

    Returns:
        None
    """
    print(f"Pre-process batch with ID {batch_id}...")
    mapping, internal_filename_stems, failed_batch_items = make_preprocessing(
        batch=batch,
        sipi_port=sipi_port
    )
    while len(failed_batch_items) != 0:
        print(f"Handling the following failed_batch_items: {failed_batch_items}")
        mapping_addition, internal_filename_stems_addition, failed_batch_items = make_preprocessing(
            batch=batch,
            sipi_port=sipi_port
        )
        mapping.update(mapping_addition)
        internal_filename_stems.extend(internal_filename_stems_addition)

    print(f"Packaging batch with ID {batch_id} into a ZIP...")
    zip_waiting_room = Path(f"ZIP/{batch_id}")
    zip_waiting_room.mkdir(parents=True)
    for file in Path("tmp").iterdir():
        if Path(file.stem).stem in internal_filename_stems:   # doubling necessary due to double extensions
            shutil.move(file, zip_waiting_room)

    with open(zip_waiting_room / "mapping.json", "x") as f:
        json.dump(mapping, f)
    shutil.make_archive(base_name=f"ZIP/{batch_id}", format="zip", root_dir=zip_waiting_room)

    # shutil.rmtree(zip_waiting_room)

    # TODO: send the ZIP to the DSP server


def enhanced_xml_upload(
    xmlfile: str,
    multimedia_folder: str,
    sipi_port: int
) -> None:
    """
    Given a project folder (current working directory)
    with a big quantity of multimedia files referenced in an XML file,
    and given a local SIPI instance, this method preprocesses the image files batch-wise in multithreading,
    packs each batch into a ZIP, and sends it to a DSP server.

    Args:
        xmlfile: path to xml file containing the data
        multimedia_folder: name of the folder containing the multimedia files
        sipi_port: 5-digit port number that SIPI uses, can be found in the 'Container' view of Docker Desktop

    Returns:
        None
    """

    shutil.rmtree("ZIP", ignore_errors=True)
    shutil.rmtree("tmp", ignore_errors=True)

    if not check_multimedia_folder(xmlfile=xmlfile, multimedia_folder=multimedia_folder):
        print("The multimedia folder and the XML file don't contain the same files!")
        exit(1)

    batches, batch_size = make_batches(multimedia_folder=multimedia_folder)

    print(f"Handing over {len(batches)} batches to ThreadPoolExecutor")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_seq, batches, range(len(batches)), repeat(sipi_port))

    # shutil.rmtree("tmp")
