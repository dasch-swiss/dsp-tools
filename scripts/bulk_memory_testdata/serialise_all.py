"""
Serialises each generated XML file into the JSON-LD payload of the bulk import, next to the XML file.
The local stack has no ingested assets, thus bitstreams and placeholder files are left out. IIIF URIs stay.

Run from the repository root, with a local stack that has the projects 9999 and 0011:
    python -m scripts.bulk_memory_testdata.serialise_all [XML files]
"""

import sys
from pathlib import Path

from dsp_tools.commands.xmlupload.serialise_bulk_payload import serialise_bulk_payload
from scripts.bulk_memory_testdata.generate_all import LOCAL_CREDS
from scripts.bulk_memory_testdata.generate_all import OUTPUT_DIR

_LENIENT_PREFIXES = ("failing_", "mixed20_")


def serialise_file(xml_file: Path) -> Path:
    output_file = xml_file.with_suffix(".jsonld")
    lenient = xml_file.name.startswith(_LENIENT_PREFIXES)
    serialise_bulk_payload(xml_file, LOCAL_CREDS, output_file, lenient=lenient, skip_ingested_files=True)
    print(f"Wrote {output_file}")
    return output_file


if __name__ == "__main__":
    files = [Path(x) for x in sys.argv[1:]] or sorted(OUTPUT_DIR.glob("*/*.xml"))
    for file in files:
        serialise_file(file)
