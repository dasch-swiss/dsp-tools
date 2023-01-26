import time
import requests
import threading
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


def upload_image(port: int, image_num: int, size: int, folder_num: int = 1) -> None:
    """
    This function uploads an image to the upload route.

    Args:
        port : port number which is added to the url
        image_num : number which is part of the file name
        size : size in MB of the file
        folder_num : number of the folder which is part of the directory path, if no number is provided the default value 1 is used

    Returns:
        None
    """

    print(f'{folder_num}-{image_num} - upload: start\nActive Threads: {threading.active_count()}')

    url = f'http://localhost:{port}/upload'
    files = {'file': open(f'testdata/bitstreams/images-{size}-{folder_num}/{image_num}_{size}mb.tif', 'rb')}
    response = requests.post(url, files=files)
    print(response)

    print(f'{folder_num}-{image_num} - upload: end')


def process_seq(port: int, queue_size: int, size: int, folder: int) -> None:
    """
    This is a helper function which does the image upload sequentially.

    Args:
        port : port number
        queue_size : amount of images that should be uploaded
        size : size in MB of the file
        folder : folder number

    Returns:
        None
    """

    for i in range(1, queue_size + 1):
        print(f"thread: {folder}", f'images-{size}-{folder}/{i}_{size}mb.tif')
        upload_image(port, i, size, folder)


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

    queue_size = 50
    amount_thread = 1
    size = 300

    start = time.perf_counter()
    # at the moment, only 1 thread per folder. the user gives us 1 folder, we have to make 32 portions out of all images
    # in it. and then distribute these 32 portions to the 32 threads.
    # instead of a folder number, we will have 32 lists, each list containing image paths
    folder = [*range(1, amount_thread + 1, 1)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_seq, repeat(sipi_port), repeat(queue_size), repeat(size), folder)
    end = time.perf_counter()

    print(f'\n{queue_size} Files ({size} MB) waiting in a thread. In total {amount_thread} threads')
    print(f'Total time: {round(end - start, 3)} second(s)\n')
