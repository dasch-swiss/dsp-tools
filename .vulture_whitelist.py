from dsp_tools.clients.ontology_create_client_live import OntologyCreateClientLive
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.error.exceptions import UnexpectedApiResponseError
from dsp_tools.error.xmllib_errors import XmllibFileNotFoundError
from dsp_tools.error.xmllib_errors import XmllibInputError
from dsp_tools.error.xmllib_errors import XmllibInternalError
from dsp_tools.utils.ansi_colors import BOLD_GREEN
from dsp_tools.utils.ansi_colors import YELLOW
from dsp_tools.utils.data_formats.date_util import is_full_date
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.data_formats.shared import check_notna
from dsp_tools.utils.rdflib_utils import serialise_json
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import validate_root_emit_user_message

PermissionValue.RV
PermissionValue.V
PermissionValue.M
PermissionValue.D
PermissionValue.CR

BOLD_GREEN
YELLOW

IriResolver.non_empty()

is_full_date("")

check_notna("")

validate_root_emit_user_message()

XmllibInputError()
XmllibInternalError()
XmllibFileNotFoundError()

# functions used in the new `create` code, can be removed once the `create` directory is not ignored by vulture any more

serialise_json()
UnexpectedApiResponseError()

from_dsp_iri_to_prefixed_iri()
make_dsp_ontology_prefix()

OntologyCreateClientLive().get_last_modification_date()
OntologyCreateClientLive().post_resource_cardinalities()
