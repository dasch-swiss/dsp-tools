import time
import requests
import threading
from itertools import repeat
import concurrent.futures
import shutil
import os


def copy_files(org_file, size, directories, files) -> None:
    """
    This function takes an image and duplicates it.

    Args:
        org_file : the original file name ex. 50mb.tif
        size : size in MB of the file
        directories : amount of directories it should create
        files : amount of files that should be created within a directory

    Returns:
        None
    """

    for directory in range(1, directories + 1):

        dir_name = f"images-{size}-{directory}"
        dir_path = os.path.join("testdata/bitstreams/", dir_name)

        for file in range(1, files + 1):

            file_name = f"{file}_{size}mb.tif"

            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            shutil.copy2(os.path.join("testdata/bitstreams/", org_file), os.path.join(dir_path, file_name))


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


def image_queue_to_thread(port: int, queue_size: int, amount_thread: int, size: int) -> None:
    """
    This function manages an upload of certain queue size.

    Args:
        port : port number
        queue_size : size of the image queue that will be uploded
        amount_thread : amount of threads
        size : size in MB of the file

    Returns:
        None
    """

    print(f'-------- image_queue_to_thread() ---------')

    start = time.perf_counter()
    folder = [*range(1, amount_thread + 1, 1)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_seq, repeat(port), repeat(queue_size), repeat(size), folder)
    end = time.perf_counter()

    print(f'\n{queue_size} Files ({size} MB) waiting in a thread. In total {amount_thread} threads')
    print(f'Total time: {round(end - start, 3)} second(s)\n')


if __name__ == '__main__':
    copy_files("test.tif", 300, 1, 50)
    # after starting up a SIPI container, copy the port number displayed in the container in Docker Desktop
    container_port = 52804

    image_queue_to_thread(port=container_port, queue_size=50, amount_thread=1, size=300)
