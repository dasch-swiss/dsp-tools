import concurrent.futures
import glob
import json
import shutil
import warnings
from itertools import repeat
from pathlib import Path
from typing import Tuple

import requests
from lxml import etree

from dsp_tools import excel2xml

Batch = list[Path]
Batchgroup = list[Batch]


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

    all_paths = list()

    # generate multimedia folder
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
            dst_file = dst / f"test.{ext}"
            all_paths.append(str(dst_file.relative_to(testproject)))
            with open(dst_file, "bw") as f:
                f.write(img)
    print(f"Successfully created folder {testproject}")

    # generate an XML file that uses these files
    root = excel2xml.make_root(shortcode="0123", default_ontology="import")
    root = excel2xml.append_permissions(root)
    for filepath in all_paths:
        resource = excel2xml.make_resource(
            label=filepath,
            restype=":Image2D",
            id=excel2xml.make_xsd_id_compatible(filepath)
        )
        warnings.filterwarnings("ignore")
        resource.append(excel2xml.make_bitstream_prop(filepath))
        root.append(resource)
    excel2xml.write_xml(root, str(testproject / "data.xml"))


def check_multimedia_folder(
    xmlfile: str,
    multimedia_folder: str
) -> bool:
    """
    Verify that all multimedia files referenced in the XML file are contained in multimedia_folder
    (or one of its subfolders), and that all files contained in multimedia_folder are referenced in the XML file.
    """
    tree = etree.parse(xmlfile)
    bitstream_paths = [elem.text for elem in tree.iter() if etree.QName(elem).localname.endswith("bitstream")]
    filesystem_paths = glob.glob(multimedia_folder + "/**/*.*", recursive=True)
    result = bitstream_paths.sort() == filesystem_paths.sort()
    return result


def make_batchgroups_mockup(multimedia_folder: str) -> list[Batchgroup]:
    batchgroup1 = [
        [x for x in Path(multimedia_folder).iterdir() if x.is_file()],
        [x for x in Path(multimedia_folder + "/nested").iterdir() if x.is_file()],
        [x for x in Path(multimedia_folder + "/nested/subfolder").iterdir() if x.is_file()]
    ]
    batchgroups = [batchgroup1, ]
    return batchgroups


def make_batchgroups(multimedia_folder: str) -> list[Batchgroup]:
    """
    Read all multimedia files contained in multimedia_folder and subfolders,
    take the images and divide them into groups of batches.
    A batchgroup consists of 32 batches (because there are 32 threads available),
    and a batch consists of 100 images.

    The batchgroups will be handled sequentially by SIPI, one batchgroup after the other,
    so that the ZIPs become available little by little,
    and can be sent to the server as they become available.


    Returns:
        a list of Batchgroups, each group being a list of batches, each batch being a list of Paths
    """
    batchgroup1 = [
        [x for x in Path(multimedia_folder).iterdir() if x.is_file()],
        [x for x in Path(multimedia_folder + "/nested").iterdir() if x.is_file()],
        [x for x in Path(multimedia_folder + "/nested/subfolder").iterdir() if x.is_file()]
    ]
    batchgroups = [batchgroup1, ]
    return batchgroups


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
            failed_batch_items.append(imgpath)
        else:
            checksum = response["uploadedFiles"][0]["checksumDerivative"]
            internal_filename = response["uploadedFiles"][0]["internalFilename"]
            mapping[str(imgpath)] = [internal_filename, checksum]
            internal_filename_stems.append(Path(internal_filename).stem)

    return mapping, internal_filename_stems, failed_batch_items


def preprocess_batch(batch: list[Path], batch_id: int, sipi_port: int) -> None:
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
    print(f"Pre-process batch with ID {batch_id} ({len(batch)} elements)...")
    mapping, internal_filename_stems, failed_batch_items = make_preprocessing(
        batch=batch,
        sipi_port=sipi_port
    )
    while len(failed_batch_items) != 0:
        print(f"Handling the following failed_batch_items: {failed_batch_items}")
        mapping_addition, internal_filename_stems_addition, failed_batch_items = make_preprocessing(
            batch=failed_batch_items,
            sipi_port=sipi_port
        )
        mapping.update(mapping_addition)
        internal_filename_stems.extend(internal_filename_stems_addition)

    zip_waiting_room = Path(f"ZIP/{batch_id}")
    zip_waiting_room.mkdir(parents=True)
    for file in list(Path("tmp").iterdir()):  # don't use generator directly (thread unsafe)
        if Path(file.stem).stem in internal_filename_stems:  # doubling necessary due to double extensions
            shutil.move(file, zip_waiting_room)

    with open(zip_waiting_room / "mapping.json", "x") as f:
        json.dump(mapping, f)
    assert len(list(zip_waiting_room.iterdir())) == len(batch) * 3 + 1, \
        f"Number of files in ZIP for batch {batch_id} is inconsistent with the original batch size"
    shutil.make_archive(base_name=f"ZIP/{batch_id}", format="zip", root_dir=zip_waiting_room)
    shutil.rmtree(zip_waiting_room)

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
    print("Check passed: Your XML file contains the same multimedia files than your multimedia folder.")

    batchgroups = make_batchgroups_mockup(multimedia_folder=multimedia_folder)

    for batchgroup in batchgroups:
        print(f"Handing over {len(batchgroup)} batches to ThreadPoolExecutor")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(preprocess_batch, batchgroup, range(len(batchgroup)), repeat(sipi_port))

# General question: Did you evaluate alternatives to concurrent.futures.ThreadPoolExecutor.map()?

# Specific questions:
#   - should we use the max_workers argument? See here:
#     https://docs.python.org/3.10/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor:
#     Default value of max_workers is changed to min(32, os.cpu_count() + 4).
#     This default value preserves at least 5 workers for I/O bound tasks.
#     It utilizes at most 32 CPU cores for CPU bound tasks which release the GIL.
#     And it avoids using very large resources implicitly on many-core machines.
#     ThreadPoolExecutor now reuses idle worker threads before starting max_workers worker threads too.

#   - Should we use the chunksize argument? See here:
#     https://docs.python.org/3.10/library/concurrent.futures.html#concurrent.futures.Executor.map:
#     When using ProcessPoolExecutor,
#     this method chops iterables into a number of chunks
#     which it submits to the pool as separate tasks.
#     The (approximate) size of these chunks can be specified by setting chunksize to a positive integer.
#     For very long iterables,
#     using a large value for chunksize can significantly improve performance compared to the default size of 1.
#     With ThreadPoolExecutor, chunksize has no effect.
