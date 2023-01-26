from typing import Tuple
import requests
from itertools import repeat
import concurrent.futures
from pathlib import Path
import os


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


def process_seq(batch: list[Path], sipi_port: int, id: int) -> None:
    """
    Upload the images contained in one batch, sequentially.

    Args:
        batch: list of paths to image files
        sipi_port: port number of SIPI

    Returns:
        None
    """
    print(f"Process batch with ID {id}...")
    for imgpath in batch:
        response = requests.post(url=f'http://localhost:{sipi_port}/upload', files={'file': open(imgpath, 'rb')})
        print(response.text)


def enhanced_xml_upload(
    xmlfile: str,
    multimedia_folder: str,
    sipi_port: int
) -> None:
    """
    This function manages an upload of certain queue size.

    Args:
        xmlfile: path to xml file containing the data
        multimedia_folder: name of the folder containing the multimedia files
        sipi_port: 5-digit port number that SIPI uses, can be found in the 'Container' view of Docker Desktop

    Returns:
        None
    """

    if not check_multimedia_folder(xmlfile=xmlfile, multimedia_folder=multimedia_folder):
        print("The multimedia folder and the XML file don't contain the same files!")
        exit(1)

    batches, batch_size = make_batches(multimedia_folder=multimedia_folder)

    print(f"Handing over {len(batches)} batches to ThreadPoolExecutor")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_seq, batches, repeat(sipi_port), range(len(batches)))
