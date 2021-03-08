import pprint
import json

from .onto_get import get_onto_data
from .onto_create_ontology import create_ontology_from_model

from ..models.connection import Connection
from ..models.project import Project

def transfer_project(shortcode: str, user: str, password: str, origin: str, target: str, verbose: bool) -> bool:
    if verbose:
        print(f'Transfering project {shortcode} from {origin} to {target}.')
    
    # Datamodel/ontology
    onto_res = _transfer_datamodel(shortcode=shortcode,
                                   user=user,
                                   password=password,
                                   origin=origin,
                                   target=target,
                                   verbose=verbose)
    if not onto_res:
        print("Transfering the datamodel failed.")
        return False
    if verbose:
        print('Successfully transferred the datamodel.')

    # Metadata

    # Admin

    # Permissions

    # Data & Images

    return True


def _transfer_datamodel(shortcode: str, user: str, password: str, origin: str, target: str, verbose: bool):
    if verbose:
        print(f'Collecting Datamodel: {shortcode} @ {origin}\n\n')

    # download from origin
    con = Connection(server=origin)
    project = Project(con=con, shortcode=shortcode)
    datamodel = get_onto_data(project, con)

    if verbose:
        # print(datamodel)
        # pprint.pprint(datamodel)
        # print(json.dumps(datamodel))
        pprint.pprint(json.dumps(datamodel))

    # upload to target
    return create_ontology_from_model(datamodel=datamodel,
                                      lists_file="",
                                      server=target,
                                      user=user,
                                      password=password,
                                      verbose=verbose,
                                      dump=False)
    
