from .onto_get import get_onto_data

from ..models.connection import Connection
from ..models.project import Project

def transfer_project(shortcode: str, user: str, password: str, origin: str, target: str, verbose: bool):
    pass


def _transfer_datamodel(shortcode: str, server: str):
    con = Connection(server=server)
    project = Project(con=con, shortcode=shortcode)
    datamodel = get_onto_data(project, con)

    print(datamodel)
    pass
