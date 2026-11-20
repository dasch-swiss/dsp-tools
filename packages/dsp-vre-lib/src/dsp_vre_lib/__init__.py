"""Python client library for the DSP-API of a DSP server."""

import logging

# A library adds no output of its own: without a handler of the caller, Python prints warnings on stderr.
logging.getLogger("dsp_vre_lib").addHandler(logging.NullHandler())
