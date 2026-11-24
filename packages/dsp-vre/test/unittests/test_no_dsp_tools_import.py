import subprocess
import sys

# A fresh interpreter: the test process itself can have dsp_tools loaded through other tests.
_IMPORT_ALL_AND_LIST_DSP_TOOLS_MODULES = """
import importlib
import pkgutil
import sys

import dsp_vre

for module_info in pkgutil.walk_packages(dsp_vre.__path__, prefix="dsp_vre."):
    importlib.import_module(module_info.name)
print(sorted(m for m in sys.modules if m == "dsp_tools" or m.startswith("dsp_tools.")))
"""


def test_import_of_all_modules_loads_no_dsp_tools_module() -> None:
    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_ALL_AND_LIST_DSP_TOOLS_MODULES],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"
