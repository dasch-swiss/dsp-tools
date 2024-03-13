import pickle
import sys
from copy import deepcopy
from dataclasses import replace

from termcolor import colored

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.list_client import ListClient
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.project_client import ProjectClient
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import cleanup_upload
from dsp_tools.commands.xmlupload.xmlupload import upload_resources
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def resume_xmlupload(server: str, user: str, password: str, sipi: str, skip_first_resource: bool = False) -> bool:
    """
    Resume an interrupted xmlupload.

    Args:
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        sipi: the sipi instance to be used
        skip_first_resource: if this flag is set, the first resource of the pending resources is removed

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """
    upload_state = _read_upload_state_from_disk(server)
    if skip_first_resource:
        if len(upload_state.pending_resources) > 0:
            new_pending = deepcopy(upload_state.pending_resources)
            new_pending.pop(0)
            upload_state = replace(upload_state, pending_resources=new_pending)
        else:
            msg = (
                "The list of pending resources is empty.\n"
                "It is not yet possible to skip the first item of the stashed properties.\n"
                "Do you want to continue with the upload of the stashed properties anyway? [y/n]"
            )
            resp = None
            while resp not in ["y", "n"]:
                resp = input(colored(msg, color="red"))
            if resp == "n":
                sys.exit(1)

    previous_successful = len(upload_state.iri_resolver_lookup)
    previous_failed = len(upload_state.failed_uploads)
    previous_total = previous_successful + previous_failed
    msg = (
        f"Resuming upload for project {upload_state.config.shortcode} on server {server}. "
        f"Number of resources uploaded until now: {previous_total}"
    )
    if previous_failed:
        msg += f" ({previous_failed} of them failed)"
    logger.info(msg)
    print("\n==========================\n" + msg + "\n==========================\n")

    con = ConnectionLive(server)
    con.login(user, password)
    sipi_con = ConnectionLive(sipi, token=con.get_token())
    sipi_server = Sipi(sipi_con)

    project_client: ProjectClient = ProjectClientLive(con, upload_state.config.shortcode)
    list_client: ListClient = ListClientLive(con, project_client.get_project_iri())

    iri_resolver, failed_uploads, nonapplied_stash = upload_resources(
        resources=upload_state.pending_resources,
        failed_uploads=upload_state.failed_uploads,
        imgdir=".",
        sipi_server=sipi_server,
        permissions_lookup=upload_state.permissions_lookup,
        con=con,
        stash=upload_state.pending_stash,
        config=upload_state.config,
        project_client=project_client,
        list_client=list_client,
        iri_resolver=IriResolver(upload_state.iri_resolver_lookup),
    )

    return cleanup_upload(iri_resolver, upload_state.config, failed_uploads, nonapplied_stash)


def _read_upload_state_from_disk(server: str) -> UploadState:
    save_location = UploadConfig().with_server_info(server, "foo").diagnostics.save_location
    with open(save_location, "rb") as f:
        saved_state: UploadState = pickle.load(f)  # noqa: S301 (deserialization of untrusted data)
    return saved_state
