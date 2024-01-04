import regex

from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.utils.connection_live import ConnectionLive


def test_list_client_live() -> None:
    con = ConnectionLive("http://localhost:3333")
    con.login("root@example.com", "test")
    list_client = ListClientLive(con, "http://rdfh.ch/projects/0001")
    list_node_id_to_iri_lookup = list_client.get_list_node_id_to_iri_lookup()
    assert len(list_node_id_to_iri_lookup) >= 28
    assert all(regex.search(r"^http://rdfh\.ch/lists/0001/.+$", x) for x in list_node_id_to_iri_lookup.values())
