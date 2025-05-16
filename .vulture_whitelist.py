from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.utils.ansi_colors import BOLD_GREEN
from dsp_tools.utils.data_formats.date_util import is_full_date
from dsp_tools.utils.data_formats.shared import check_notna

PermissionValue.RV
PermissionValue.V
PermissionValue.M
PermissionValue.D
PermissionValue.CR

BOLD_GREEN

IriResolver.non_empty()

is_full_date("")

check_notna("")

LegalInfoClient().get_enabled_licenses()
LegalInfoClientLive("", "", AuthenticationClient()).get_enabled_licenses()
