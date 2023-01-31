import concurrent.futures
import json
import os
import shutil
import warnings
from collections.abc import Generator
from itertools import repeat
from pathlib import Path

import requests
from lxml import etree

from dsp_tools import excel2xml

Batch = list[Path]
Batchgroup = list[Batch]

BatchGroupIndex = int
BatchIndex = int
positionWithinBatchIndex = int
NextBatchPlace = tuple[BatchGroupIndex, BatchIndex, positionWithinBatchIndex]

image_extensions = ["jpg", "jpeg", "tif", "tiff", "jp2", "png"]


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
    for ext in image_extensions:
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
) -> None:
    """
    Verify that all multimedia files referenced in the XML file are contained in multimedia_folder
    (or one of its subfolders), and that all files contained in multimedia_folder are referenced in the XML file.
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


def make_batchgroups(multimedia_folder: str, images_per_batch: int, batches_per_group: int) -> list[Batchgroup]:
    """
    Read all multimedia files contained in multimedia_folder and its subfolders,
    take the images and divide them into groups of batches.

    Args:
        multimedia_folder: path to the folder containing the multimedia files
        images_per_batch: max. batch size (can be smaller if there are not enough images to fill it)
        batches_per_group: max. batchgroup size (can be smaller if there are not enough images to fill it)

    Returns:
        a list of Batchgroups, each group being a list of batches, each batch being a list of Paths
    """
    # collect all paths
    all_paths: list[Path] = list()
    for img_type in image_extensions:
        all_paths.extend(Path().glob(f"{multimedia_folder}/**/*.{img_type}"))

    # distribute the paths into batchgroups
    all_paths_generator = (x for x in all_paths)
    batchgroups: list[Batchgroup] = list()
    try:
        for batchgroup_index, batch_index, position_within_batch_index in yield_next_batch_place(
            images_per_batch=images_per_batch,
            batches_per_group=batches_per_group
        ):
            next_path = next(all_paths_generator)
            if len(batchgroups) < batchgroup_index + 1:
                batchgroups.append(list())
            if len(batchgroups[batchgroup_index]) < batch_index + 1:
                batchgroups[batchgroup_index].append(list())
            batchgroups[batchgroup_index][batch_index].append(next_path)
    except StopIteration:
        pass

    # verify that content of batches is equal to the originally found paths
    paths_in_batches = list()
    for batchgroup in batchgroups:
        for batch in batchgroup:
            paths_in_batches.extend(batch)
    assert sorted(paths_in_batches) == sorted(all_paths)

    print(f"Found {len(all_paths)} files in folder '{multimedia_folder}'. Prepare batches as follows: ")
    for i, batchgroup in enumerate(batchgroups):
        batchsizes = [f"{len(x):2d}" for x in batchgroup]
        print(f"\tBatchgroup no. {i} with {len(batchgroup)} batches, size of each batch: {batchsizes}")

    return batchgroups


def yield_next_batch_place(images_per_batch: int, batches_per_group: int) -> Generator[NextBatchPlace, None, None]:
    """
    This generator yields the place where to put the next image in.
    First, we want to distribute the images over 1 batchgroup, each batch containing 1 image.
    Then we give every batch a second image, and so on, until the batchgroup is full.
    Then, we fill the next batchgroup.
    For this purpose, this generator yields a tuple consisting of (batchgroup, batch, position_within_batch).
    batch is the fastest growing index (going up to batches_per_group - 1),
    position_within_batch the second fastest (going up to images_per_batch - 1),
    and batchgroup the slowest growing index (going up to infinity)
    """
    for batchgroup in range(999999):
        for position_within_batch in range(images_per_batch):
            for batch in range(batches_per_group):
                yield batchgroup, batch, position_within_batch


def make_preprocessing(
    batch: list[Path],
    sipi_port: int
) -> tuple[dict[str, list[str]], list[str], list[Path]]:
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
    # print(f"\tPre-process batch with ID {batch_id} ({len(batch)} elements)...")
    mapping, internal_filename_stems, failed_batch_items = make_preprocessing(
        batch=batch,
        sipi_port=sipi_port
    )
    while len(failed_batch_items) != 0:
        print(f"\tRetry the following failed files: {[str(x) for x in failed_batch_items]}")
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
    zipped_batch = shutil.make_archive(base_name=f"ZIP/{batch_id}", format="zip", root_dir=zip_waiting_room)
    print(f"\tBatch {batch_id} is ready to be sent to DSP server as {Path(zipped_batch).relative_to(os.getcwd())}")
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
    and given a local SIPI instance,
    this method preprocesses the image files batch-wise in multithreading,
    packs each batch into a ZIP,
    and sends it to a DSP server.

    Args:
        xmlfile: path to xml file containing the data
        multimedia_folder: name of the folder containing the multimedia files
        sipi_port: 5-digit port number that SIPI uses, can be found in the 'Container' view of Docker Desktop

    Returns:
        None
    """

    shutil.rmtree("ZIP", ignore_errors=True)

    check_multimedia_folder(xmlfile=xmlfile, multimedia_folder=multimedia_folder)

    batchgroups = make_batchgroups(
        multimedia_folder=multimedia_folder,
        images_per_batch=10,
        batches_per_group=32
    )

    # Preprocess images with SIPI, one batchgroup after the other,
    # so that the ZIPs become available little by little,
    # and can be sent to the server as they become available
    for i, batchgroup in enumerate(batchgroups):
        print(f"Handing over Batchgroup no. {i} with {len(batchgroup)} batches to ThreadPoolExecutor.")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(preprocess_batch, batchgroup, [f"{i}-{j}" for j in range(len(batchgroup))], repeat(sipi_port))

    assert len(list(Path("tmp").iterdir())) == 0
    shutil.rmtree("tmp", ignore_errors=True)
    print("Sucessfully finished!")

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
