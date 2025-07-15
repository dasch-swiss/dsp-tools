import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias


def get_temp_directory() -> TemporaryDirectory[str]:
    ttl_dir = (Path.home() / ".dsp-tools" / "validate-data").absolute()
    ttl_dir.mkdir(exist_ok=True, parents=True)
    t_dir = TemporaryDirectory(dir=ttl_dir)
    return t_dir


def clean_up_temp_directory(temp_dir: TemporaryDirectory[str], save_graphs_dir: Path | None) -> None:
    if save_graphs_dir:
        tmp_folder = Path(temp_dir.name)
        save_graphs_dir.mkdir(parents=True, exist_ok=True)
        for tmp_filepath in tmp_folder.glob("*"):
            if tmp_filepath.is_file():
                dest_filepath = save_graphs_dir / tmp_filepath.relative_to(tmp_folder)
                shutil.copy2(tmp_filepath, dest_filepath)
    temp_dir.cleanup()


def reformat_any_iri(iri: SubjectObjectTypeAlias | str) -> str:
    """
    Reformats any kind of IRI, if it starts with data then it treats is like a data IRI.
    Otherwise, like an ontology IRI.

    Args:
        iri: Input IRI

    Returns:
        reformatted string
    """
    iri_str = str(iri)
    if iri_str.startswith("http://data/"):
        return reformat_data_iri(iri_str)
    if iri_str.startswith("http://rdfh.ch/"):
        return iri_str
    return reformat_onto_iri(iri_str)


def reformat_onto_iri(iri: SubjectObjectTypeAlias | str) -> str:
    """Takes a rdflib Node and returns a prefixed IRI in string form."""
    iri_str = str(iri)
    if "http://www.w3.org/2000/01/rdf-schema#" in iri_str:
        return f"rdfs:{iri_str.split('#')[-1]}"
    onto = iri_str.split("/")[-2]
    ending = iri_str.split("#")[-1]
    if onto == "knora-api":
        return ending
    return f"{onto}:{ending}"


def reformat_data_iri(iri: SubjectObjectTypeAlias | str) -> str:
    """Takes a rdflib Node with in the data namespace and returns only the suffix."""
    return str(iri).replace("http://data/", "", 1)
