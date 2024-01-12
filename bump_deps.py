import subprocess
from pathlib import Path

import toml

toml_data = toml.loads(Path("pyproject.toml").read_text())

# Bump prod dependencies
dependencies = toml_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
for package, version in dependencies.items():
    cmd = f"poetry add {package}@latest".split()
    if package == "python":
        continue
    if "extras" in version:
        cmd.extend(["--extras", ",".join(version["extras"])])
    print("****** " + " ".join(cmd) + " ******")
    subprocess.run(cmd, check=False)

# Bump dev dependencies
dev_dependencies = toml_data.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {}).get("dependencies", {})
for package, version in dev_dependencies.items():
    cmd = f"poetry add {package}@latest --group dev".split()
    if "extras" in version:
        cmd.extend(["--extras=", ",".join(version["extras"])])
    print("****** " + " ".join(cmd) + " ******")
    subprocess.run(cmd, check=False)

# Upgrade sub-dependencies in poetry.lock
subprocess.run("poetry update".split(), check=False)
