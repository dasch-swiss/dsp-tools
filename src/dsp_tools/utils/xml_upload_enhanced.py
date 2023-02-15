import concurrent.futures
import json
import os
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

    # download and adapt JSON project file from 0123-import-scripts
    json_text = requests.get(
        "https://github.com/dasch-swiss/0123-import-scripts/blob/main/import_project.json?raw=true").text
    json_text = json_text.replace('"cardinality": "1"', '"cardinality": "0-n"')
    json_text = json_text.replace('"cardinality": "1-n"', '"cardinality": "0-n"')
    with open(testproject / "data_model.json", "x") as f:
        f.write(json_text)


def check_multimedia_folder(
    xmlfile: str,
    multimedia_folder: str
) -> etree.ElementTree:
    """
    Verify that all multimedia files referenced in the XML file are contained in multimedia_folder
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


# def make_equally_sized_batches(multimedia_folder: str, optimal_batch_size_mb: int) -> list[Batch]:
#     """
#     Read all multimedia files contained in multimedia_folder and its subfolders,
#     take the images and divide them into batches.
#     A batch is filled with images until the optimal_batch_size_mb is reached.
#     """
#     # collect all paths
#     path_to_size: dict[Path, float] = dict()
#     for img_type in image_extensions:
#         for pth in Path().glob(f"{multimedia_folder}/**/*.{img_type}"):
#             path_to_size[pth] = round(pth.stat().st_size / 1_000_000, 1)
#     all_paths = sorted(path_to_size.keys(), key=lambda x: path_to_size[x])
# TODO: This is experimental


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
) -> tuple[dict[str, str], list[Path]]:
    """
    Sends the images contained in batch to the /upload route of SIPI,
    creates a mapping of the original filepath to the SIPI-internal filename and the checksum,
    and returns the mapping for the successfully processed files,
    together with a list of the failed original filepaths.

    Args:
        batch: list of paths to image files
        sipi_port: port number of SIPI

    Returns:
        mapping, failed_batch_items
    """
    mapping: dict[str, str] = dict()
    failed_batch_items = list()
    for imgpath in batch:
        with open(imgpath, 'rb') as bitstream:
            response_raw = requests.post(url=f'http://localhost:{sipi_port}/upload', files={'file': bitstream})
        response = json.loads(response_raw.text)
        if response.get("message") == "server.fs.mkdir() failed: File exists":
            failed_batch_items.append(imgpath)
        else:
            internal_filename = response["uploadedFiles"][0]["internalFilename"]
            mapping[str(imgpath)] = internal_filename

    return mapping, failed_batch_items


def preprocess_batch(batch: list[Path], sipi_port: int) -> dict[str, str]:
    """
    Create JP2 and sidecar files of the images contained in one batch.

    Args:
        batch: list of paths to image files
        sipi_port: port number of SIPI

    Returns:
        mapping of original filepaths to internal filenames
    """
    mapping, failed_batch_items = make_preprocessing(
        batch=batch,
        sipi_port=sipi_port
    )
    while len(failed_batch_items) != 0:
        print(f"\tRetry the following failed files: {[str(x) for x in failed_batch_items]}")
        mapping_addition, failed_batch_items = make_preprocessing(
            batch=failed_batch_items,
            sipi_port=sipi_port
        )
        mapping.update(mapping_addition)
    return mapping


def write_preprocessed_xml_file(xml_file_tree: etree.ElementTree, mapping: dict[str, str], xmlfile: str) -> None:
    """
    Make a copy of the XML file with the filepaths replaced by the UUID.

    Args:
        xml_file_tree: etree representation of the original XML document
        mapping: mapping from the original filepaths to the internal filenames

    Returns:
        None
    """
    for elem in xml_file_tree.iter():
        if elem.text in mapping:
            elem.text = mapping[elem.text]
    xml_string = etree.tostring(xml_file_tree, encoding="unicode", pretty_print=True)
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
    with open(f"{Path(xmlfile).stem}-preprocessed.xml", "w", encoding="utf-8") as f:
        f.write(xml_string)


def preprocess_xml_upload(
    xmlfile: str,
    multimedia_folder: str,
    sipi_port: int
) -> None:
    """
    Given a project folder (current working directory)
    with a big quantity of multimedia files referenced in an XML file,
    and given a local SIPI instance,
    this method preprocesses the image files batch-wise in multithreading.

    Args:
        xmlfile: path to xml file containing the data
        multimedia_folder: name of the folder containing the multimedia files
        sipi_port: 5-digit port number that SIPI uses, can be found in the 'Container' view of Docker Desktop

    Returns:
        None
    """
    xml_file_tree = check_multimedia_folder(xmlfile=xmlfile, multimedia_folder=multimedia_folder)

    # concurrent.futures.ThreadPoolExecutor() works with min(32, os.cpu_count() + 4) threads
    # (see https://docs.python.org/3.10/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor),
    # so the ideal number of batches per group is equal to the number of available threads
    num_of_available_threads = min(32, os.cpu_count() + 4)

    # make_equally_sized_batches(multimedia_folder=multimedia_folder, optimal_batch_size_mb=15)

    batchgroups = make_batchgroups(
        multimedia_folder=multimedia_folder,
        images_per_batch=10,
        batches_per_group=num_of_available_threads
    )

    mapping = dict()

    for i, batchgroup in enumerate(batchgroups):
        print(f"Handing over Batchgroup no. {i} with {len(batchgroup)} batches to ThreadPoolExecutor.")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            batchgroup_mappings = executor.map(
                preprocess_batch,
                batchgroup,
                repeat(sipi_port)
            )
        for mp in batchgroup_mappings:
            mapping.update(mp)

        # TODO: send_batch_to_server(batchgroup_mappings)

    write_preprocessed_xml_file(xml_file_tree=xml_file_tree, mapping=mapping, xmlfile=xmlfile)

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
