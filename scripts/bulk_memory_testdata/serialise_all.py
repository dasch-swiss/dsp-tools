"""
Serialises each generated XML file into the JSON-LD payload of the bulk import, next to the XML file.
The local stack has no ingested assets, thus bitstreams and placeholder files are left out. IIIF URIs stay.

If the XML file has resources that the dsp-api transformer rejects,
a second payload without them is written as <name>_no_transformer_errors.jsonld.
Only the second payload reaches the SHACL validation of the server.

Run from the repository root, with a local stack that has the projects 9999 and 0011:
    python -m scripts.bulk_memory_testdata.serialise_all [XML files]
"""

import sys
from pathlib import Path

from lxml import etree

from dsp_tools.commands.xmlupload.serialise_bulk_payload import serialise_bulk_payload
from scripts.bulk_memory_testdata.generate_all import LOCAL_CREDS
from scripts.bulk_memory_testdata.generate_all import OUTPUT_DIR
from scripts.bulk_memory_testdata.transformer_errors import get_transformer_rejected_ids
from scripts.bulk_memory_testdata.xml_ids import get_resources

_LENIENT_PREFIXES = ("failing_", "mixed20_")


def serialise_file(xml_file: Path) -> list[Path]:
    lenient = xml_file.name.startswith(_LENIENT_PREFIXES)
    outputs = [_serialise(xml_file, xml_file.with_suffix(".jsonld"), lenient, frozenset())]
    res_ids = [x.attrib["id"] for x in get_resources(etree.parse(xml_file).getroot())]
    if rejected := get_transformer_rejected_ids(res_ids):
        output_file = xml_file.with_name(f"{xml_file.stem}_no_transformer_errors.jsonld")
        outputs.append(_serialise(xml_file, output_file, lenient, frozenset(rejected)))
    return outputs


def _serialise(xml_file: Path, output_file: Path, lenient: bool, skip_resource_ids: frozenset[str]) -> Path:
    serialise_bulk_payload(
        xml_file,
        LOCAL_CREDS,
        output_file,
        lenient=lenient,
        skip_ingested_files=True,
        skip_resource_ids=skip_resource_ids,
    )
    print(f"Wrote {output_file}")
    return output_file


if __name__ == "__main__":
    files = [Path(x) for x in sys.argv[1:]] or sorted(OUTPUT_DIR.glob("*/*.xml"))
    for file in files:
        serialise_file(file)
