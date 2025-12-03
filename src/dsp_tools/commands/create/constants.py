from rdflib import Namespace

KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
KNORA_ADMIN_STR = "http://www.knora.org/ontology/knora-admin#"
SALSAH_GUI_STR = "http://api.knora.org/ontology/salsah-gui/v2#"
SALSAH_GUI = Namespace(SALSAH_GUI_STR)

UNIVERSAL_PREFIXES = {"knora-api": KNORA_API_STR, "salsah-gui": SALSAH_GUI_STR}
