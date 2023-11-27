import regex

from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.utils.connection_live import ConnectionLive

# ruff: noqa: D103 (undocumented-public-function)


def test_list_client_live() -> None:
    con = ConnectionLive("http://localhost:3333")
    con.login("root@example.com", "test")
    project_client = ProjectClientLive(con, "0001")
    project_iri = project_client.get_project_iri()
    assert project_iri == "http://rdfh.ch/projects/0001"
    list_client = ListClientLive(con, project_iri)
    list_node_id_to_iri_lookup = list_client.get_list_node_id_to_iri_lookup()
    assert len(list_node_id_to_iri_lookup) >= 28
    assert all(regex.search(r"^http://rdfh\.ch/lists/0001/.+$", x) for x in list_node_id_to_iri_lookup.values())
