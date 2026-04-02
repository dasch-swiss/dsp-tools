from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.clients.resource_client_live import ResourceClientLive
from dsp_tools.commands.xmlupload.execute_upload import _execute_one_resource_upload
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.setup.ansi_colors import BOLD_GREEN
from dsp_tools.setup.ansi_colors import YELLOW
from dsp_tools.utils.data_formats.date_util import is_full_date
from dsp_tools.utils.data_formats.shared import check_notna
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

ResourceClient().post_resource()
ResourceClientLive().post_resource()
_execute_one_resource_upload()
