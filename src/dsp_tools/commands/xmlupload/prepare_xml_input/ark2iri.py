from __future__ import annotations

import base64
import uuid

import regex

from dsp_tools.error.exceptions import BaseError


def convert_ark_v0_to_resource_iri(ark: str) -> str:
    """
    Converts an ARK URL from salsah.org (ARK version 0) of the form ark:/72163/080c-779b9990a0c3f-6e
    to a DSP resource IRI of the form http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q

    This method is needed for the migration of projects from salsah.org to DSP.
    Resources need to be created with an existing ARK,
    so the IRI needs to be extracted from that ARK
    in order for the ARK URL to be still valid after the migration.

    Args:
        ark: an ARK version 0 of the form ark:/72163/080c-779b9990a0c3f-6e,
            '72163' being the Name Assigning Authority number,
            '080c' being the project shortcode,
            '779b9990a0c3f' being an ID derived from the object's Salsah ID and
            '6e' being check digits

    Raises:
        BaseError: if the ARK is invalid

    Returns:
        Resource IRI (str) of the form http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q
    """
    # create the DaSCH namespace to create version 5 UUIDs
    generic_namespace_url = uuid.NAMESPACE_URL
    dasch_uuid_ns = uuid.uuid5(generic_namespace_url, "https://dasch.swiss")  # cace8b00-717e-50d5-bcb9-486f39d733a2

    # get the salsah resource ID from the ARK and convert it to a UUID version 5 (base64 encoded)
    if ark.count("-") != 2:
        raise BaseError(f"Error while converting ARK '{ark}'. The ARK seems to be invalid")
    project_id, resource_id, _ = ark.split("-")
    _, project_id = project_id.rsplit("/", 1)
    project_id = project_id.upper()
    if not regex.match("^[0-9a-fA-F]{4}$", project_id):
        raise BaseError(f"Error while converting ARK '{ark}'. Invalid project shortcode '{project_id}'")
    if not regex.match("^[0-9A-Za-z]+$", resource_id):
        raise BaseError(f"Error while converting ARK '{ark}'. Invalid Salsah ID '{resource_id}'")

    # make a UUID v5 from the namespace created above (which is a UUID itself) and the resource ID
    # and encode it to base64
    dsp_uuid = base64.urlsafe_b64encode(uuid.uuid5(dasch_uuid_ns, resource_id).bytes).decode("utf-8")
    dsp_uuid = dsp_uuid[:-2]

    # use the new UUID to create the resource IRI
    return f"http://rdfh.ch/{project_id}/{dsp_uuid}"
