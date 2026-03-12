from __future__ import annotations

import sys
import warnings
from datetime import datetime
from typing import Never

from loguru import logger

from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.xmlupload import _save_upload_state
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.error.exceptions import PermanentTimeOutError
from dsp_tools.setup.logger_config import WARNINGS_SAVEPATH


def handle_permanent_connection_error(err: PermanentConnectionError) -> Never:
    msg = "Lost connection to DSP server, probably because the server is down. "
    msg += f"Please continue later with 'resume-xmlupload'. Reason for this failure: {err.message}"
    logger.error(msg)
    msg += f"\nSee {WARNINGS_SAVEPATH} for more information."
    raise XmlUploadInterruptedError(msg) from None


def handle_keyboard_interrupt() -> Never:
    warnings.warn(DspToolsUserWarning("xmlupload manually interrupted. Tidying up, then exit..."))
    msg = "xmlupload manually interrupted. Please continue later with 'resume-xmlupload'"
    raise XmlUploadInterruptedError(msg) from None


def handle_permanent_timeout_or_keyboard_interrupt(
    err: PermanentTimeOutError | KeyboardInterrupt, res_id: str
) -> Never:
    warnings.warn(DspToolsUserWarning(f"{type(err).__name__}: Tidying up, then exit..."))
    msg = (
        f"There was a {type(err).__name__} while trying to create resource '{res_id}'.\n"
        f"It is unclear if the resource '{res_id}' was created successfully or not.\n"
        f"Please check manually in the DSP-APP or DB.\n"
        f"In case of successful creation, call 'resume-xmlupload' with the flag "
        f"'--skip-first-resource' to prevent duplication.\n"
        f"If not, a normal 'resume-xmlupload' can be started."
    )
    logger.error(msg)
    raise XmlUploadInterruptedError(msg) from None


def interrupt_if_indicated(upload_state: UploadState, creation_attempts_of_this_round: int) -> None:
    # if the interrupt_after value is not set, the upload will not be interrupted
    interrupt_after = upload_state.config.interrupt_after or 999_999_999
    if creation_attempts_of_this_round + 1 >= interrupt_after:
        msg = f"Interrupted: Maximum number of resources was reached ({upload_state.config.interrupt_after})"
        raise XmlUploadInterruptedError(msg)


def tidy_up_resource_creation_idempotent(
    upload_state: UploadState,
    iri: str | None,
    resource: ProcessedResource,
) -> None:
    previous_successful = len(upload_state.iri_resolver.lookup)
    previous_failed = len(upload_state.failed_uploads)
    upcoming = len(upload_state.pending_resources)
    current_res = previous_successful + previous_failed + 1
    total_res = previous_successful + previous_failed + upcoming
    if iri:
        # resource creation succeeded: update the iri_resolver
        upload_state.iri_resolver.lookup[resource.res_id] = iri
        msg = f"Created resource {current_res}/{total_res}: '{resource.label}' (ID: '{resource.res_id}', IRI: '{iri}')"
        logger.info(msg)
    else:  # noqa: PLR5501
        # resource creation failed gracefully: register it as failed
        if resource.res_id not in upload_state.failed_uploads:
            upload_state.failed_uploads.append(resource.res_id)

    if resource in upload_state.pending_resources:
        upload_state.pending_resources.remove(resource)


def inform_about_resource_creation_failure(resource: ProcessedResource, err_msg: str | None) -> None:
    log_msg = f"Unable to create resource '{resource.label}' ({resource.res_id})\n"
    if err_msg:
        log_msg += err_msg
    logger.exception(log_msg)


def handle_upload_error(err: BaseException, upload_state: UploadState) -> None:
    """
    In case the xmlupload must be interrupted,
    e.g. because of an error that could not be handled,
    or due to keyboard interrupt,
    this method ensures
    that all information about what is already in DSP
    is written into diagnostic files.

    It then quits the Python interpreter with exit code 1.

    Args:
        err: the error that was the cause of the abort
        upload_state: the current state of the upload
    """
    if isinstance(err, XmlUploadInterruptedError):
        msg = "\n==========================================\n" + err.message + "\n"
        exit_code = 0
    else:
        msg = (
            f"\n==========================================\n"
            f"{datetime.now()}: xmlupload must be aborted because of an error.\n"
            f"Error message: '{err}'\n"
            f"See {WARNINGS_SAVEPATH} for more information\n"
        )
        exit_code = 1

    msg += _save_upload_state(upload_state)

    if failed := upload_state.failed_uploads:
        msg += f"Independently from this, there were some resources that could not be uploaded: {failed}\n"

    if exit_code == 1:
        logger.error(msg)
    else:
        logger.info(msg)
    print(msg)

    sys.exit(exit_code)
