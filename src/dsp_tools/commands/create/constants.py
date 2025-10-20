from rdflib import Namespace

KNORA_API = "http://api.knora.org/ontology/knora-api/v2#"
SALSAH_GUI = "http://api.knora.org/ontology/salsah-gui/v2#"
SALSAH_GUI_NAMESPACE = Namespace(SALSAH_GUI)

UNIVERSAL_PREFIXES = {"knora-api": KNORA_API, "salsah-gui": SALSAH_GUI}
