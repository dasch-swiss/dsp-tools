from __future__ import annotations

import pickle
import warnings
from typing import Never

from loguru import logger
from requests import ReadTimeout

from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.setup.logger_config import WARNINGS_SAVEPATH

# The handlers below convert a low-level failure into the exception that determines the exit code:
# XmlUploadInterruptedError (an InternalError) exits with 1, a KeyboardInterrupt exits with 130.
# BadCredentialsError (a UserError) also exits with 1, but it is raised natively by the client
# and only re-raised in execute_upload.py, not converted by a handler here.
# Their messages reach the user in different ways:
# entry_point.py prints the DSP-TOOLS exceptions, but not a KeyboardInterrupt.
# Therefore the keyboard interrupt handlers emit their message as a user warning, which is printed.


def handle_permanent_connection_error(err: PermanentConnectionError) -> Never:
    msg = (
        f"Lost connection to DSP server, probably because the server is down. "
        f"Reason for this failure: {err.message}\n"
        f"See {WARNINGS_SAVEPATH} for more information."
    )
    logger.exception(msg)
    raise XmlUploadInterruptedError(msg) from None


def handle_keyboard_interrupt() -> Never:
    msg = "xmlupload manually interrupted. Tidying up, then exit..."
    warnings.warn(DspToolsUserWarning(msg))
    logger.exception(msg)
    raise KeyboardInterrupt(msg) from None


def handle_permanent_timeout(err: TimeoutError | ReadTimeout, res_id: str) -> Never:
    warnings.warn(DspToolsUserWarning(f"{type(err).__name__}: Tidying up, then exit..."))
    msg = _unclear_creation_outcome_msg(type(err).__name__, res_id)
    logger.exception(msg)
    raise XmlUploadInterruptedError(msg) from None


def handle_keyboard_interrupt_during_creation(res_id: str) -> Never:
    msg = _unclear_creation_outcome_msg("KeyboardInterrupt", res_id)
    warnings.warn(DspToolsUserWarning(f"KeyboardInterrupt: Tidying up, then exit...\n{msg}"))
    logger.exception(msg)
    raise KeyboardInterrupt(msg) from None


def _unclear_creation_outcome_msg(reason: str, res_id: str) -> str:
    return (
        f"There was a {reason} while trying to create resource '{res_id}'.\n"
        f"It is unclear if the resource '{res_id}' was created successfully or not.\n"
        f"Please check manually in the DSP-APP or DB.\n"
        f"In case of successful creation, call 'resume-xmlupload' with the flag "
        f"'--skip-first-resource' to prevent duplication.\n"
        f"If not, a normal 'resume-xmlupload' can be started."
    )


def interruption_is_indicated(upload_state: UploadState, creation_attempts_of_this_round: int) -> bool:
    """Whether the number of resources requested with '--interrupt-after' has been created."""
    if not (interrupt_after := upload_state.config.interrupt_after):
        return False
    return creation_attempts_of_this_round + 1 >= interrupt_after


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


def persist_state_for_resume(upload_state: UploadState) -> None:
    """
    Write all information about what is already in DSP into diagnostic files,
    and tell the user how to continue the interrupted upload.

    Args:
        upload_state: the current state of the upload
    """
    msg = save_upload_state(upload_state)
    msg += "Continue later with 'resume-xmlupload'.\n"
    if failed := upload_state.failed_uploads:
        msg += f"Independently from this, there were some resources that could not be uploaded: {failed}\n"
    logger.info(msg)
    print(f"\n==========================================\n{msg}")


def save_upload_state(upload_state: UploadState) -> str:
    save_location = upload_state.config.diagnostics.save_location
    save_location.unlink(missing_ok=True)
    save_location.touch(exist_ok=True)
    with open(save_location, "wb") as file:
        pickle.dump(upload_state, file)
    logger.info(f"Saved the current upload state to {save_location}")
    return f"Saved the current upload state to {save_location}.\n"
