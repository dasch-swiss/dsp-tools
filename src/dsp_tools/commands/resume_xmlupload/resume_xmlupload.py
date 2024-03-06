import pickle

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


def resume_xmlupload(
    server: str,
    user: str,
    password: str,
    sipi: str,
) -> bool:
    """
    Resume an interrupted xmlupload.

    Args:
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        sipi: the sipi instance to be used

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """
    upload_state = _read_upload_state_from_disk(server)

    con = ConnectionLive(server)
    con.login(user, password)
    sipi_con = ConnectionLive(sipi, token=con.get_token())
    sipi_server = Sipi(sipi_con)

    project_client: ProjectClient = ProjectClientLive(con, upload_state.config.shortcode)
    list_client: ListClient = ListClientLive(con, project_client.get_project_iri())

    iri_resolver, failed_uploads = upload_resources(
        resources=upload_state.pending_resources,
        imgdir=".",
        sipi_server=sipi_server,
        permissions_lookup=upload_state.permissions_lookup,
        con=con,
        stash=upload_state.stash,
        config=upload_state.config,
        project_client=project_client,
        list_client=list_client,
    )

    return cleanup_upload(iri_resolver, upload_state.config, failed_uploads)


def _read_upload_state_from_disk(server: str) -> UploadState:
    save_location = UploadConfig().with_server_info(server, "foo").diagnostics.save_location
    with open(save_location, "rb") as f:
        saved_state: UploadState = pickle.load(f)  # noqa: S301 (deserialization of untrusted data)
    return saved_state
