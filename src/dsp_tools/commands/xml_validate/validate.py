import timeit
from pathlib import Path

from dsp_tools.commands.xml_validate.xml_validate import xml_validate


def timed_xml_validate():
    xml_validate(Path("testdata/xml-validate/poc/data/err-2000-corr-2800.xml"))


execution_time = timeit.timeit(timed_xml_validate, number=1)
print(f"Execution time: {execution_time} seconds")
