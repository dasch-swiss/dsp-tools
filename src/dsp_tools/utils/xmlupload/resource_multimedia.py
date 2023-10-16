from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dsp_tools.models.permission import Permissions
from dsp_tools.models.sipi import Sipi
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action
from dsp_tools.utils.xmlupload.write_diagnostic_info import MetricRecord

logger = get_logger(__name__)


def calculate_multimedia_file_size(
    resources: list[XMLResource],
    imgdir: str,
    preprocessing_done: bool,
) -> tuple[list[float], float | int]:
    """
    This function calculates the size of the bitstream files in the specified directory.

    Args:
        resources: List of resources to identify the files used
        imgdir: directory where the files are
        preprocessing_done: True if sipi has preprocessed the files

    Returns:
        List with all the file sizes
        Total of all the file sizes
    """
    # If there are multimedia files: calculate their total size
    bitstream_all_sizes_mb = [
        Path(Path(imgdir) / Path(res.bitstream.value)).stat().st_size / 1000000
        if res.bitstream and not preprocessing_done
        else 0.0
        for res in resources
    ]
    if sum(bitstream_all_sizes_mb) > 0:
        bitstream_size_total_mb = round(sum(bitstream_all_sizes_mb), 1)
        print(f"This xmlupload contains multimedia files with a total size of {bitstream_size_total_mb} MB.")
        logger.info(f"This xmlupload contains multimedia files with a total size of {bitstream_size_total_mb} MB.")
    else:  # make Pylance happy
        bitstream_size_total_mb = 0.0
    return bitstream_all_sizes_mb, bitstream_size_total_mb


def get_sipi_multimedia_information(
    resource: XMLResource,
    sipi_server: Sipi,
    imgdir: str,
    filesize: float,
    permissions_lookup: dict[str, Permissions],
    metrics: list[MetricRecord],
) -> dict[str, str | Permissions] | None:
    """
    This function takes a resource with a corresponding bitstream filepath.
    If the pre-processing is not done, it retrieves the file from the directory and uploads it to sipi.
    If pre-processing is done it retrieves the bitstream information from sipi.

    Args:
        resource: resource with that has a bitstream
        sipi_server: server to upload
        imgdir: directory of the file
        filesize: size of the file
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
        metrics: to store metric information in
        preprocessing_done: If True, then no upload is necessary

    Returns:
        The information from sipi which is needed to establish a link from the resource
    """
    pth = resource.bitstream.value  # type: ignore[union-attr]
    bitstream_start = datetime.now()
    filetype = Path(pth).suffix[1:]
    img: Optional[dict[Any, Any]] = try_network_action(
        sipi_server.upload_bitstream,
        filepath=str(Path(imgdir) / Path(pth)),
    )
    bitstream_duration = datetime.now() - bitstream_start
    bitstream_duration_ms = bitstream_duration.seconds * 1000 + int(bitstream_duration.microseconds / 1000)
    mb_per_sec = round((filesize / bitstream_duration_ms) * 1000, 1)
    metrics.append(MetricRecord(resource.id, filetype, filesize, "bitstream upload", bitstream_duration_ms, mb_per_sec))
    internal_file_name_bitstream = img["uploadedFiles"][0]["internalFilename"]  # type: ignore[index]
    resource_bitstream = resource.get_bitstream_information_from_sipi(
        internal_file_name_bitstream=internal_file_name_bitstream,
        permissions_lookup=permissions_lookup,
    )
    return resource_bitstream
