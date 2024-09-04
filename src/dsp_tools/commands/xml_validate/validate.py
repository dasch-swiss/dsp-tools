from pathlib import Path

from dsp_tools.commands.xml_validate.xml_validate import xml_validate

xml_validate(Path("testdata/xml-validate/valid-data.xml"))

xml_validate(Path("testdata/xml-validate/invalid-data.xml"))
