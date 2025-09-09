import subprocess
from dataclasses import dataclass
from loguru import logger
_10_GB_IN_BYTES = 10_000_000_000
_20_GB_IN_BYTES = _10_GB_IN_BYTES * 2


@dataclass
class FusekiMetrics:
    container_id: str | None = None
    size_before: int | None = None
    size_after: int | None = None

    def get_start_size(self) -> None:
        self.size_before = self._get_size()

    def get_end_size(self) -> None:
        self.size_after = self._get_size()

    def _get_size(self) -> int:
        if not self.container_id:
            self._get_container_id()
        cmd = f"docker exec '{self.container_id}' du -sb /fuseki 2>/dev/null | awk '{{print $1}}'"
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return int(result.stdout.strip())

    def _get_container_id(self) -> None:
        cmd = "docker ps --format '{{.ID}} {{.Image}}' | grep 'daschswiss/apache-jena-fuseki' | awk '{print $1}'"
        result = self._run_command(cmd)
        self.container_id = result

    def _run_command(self, cmd: str) -> str:
        result = subprocess.run(cmd.split(), check=False, capture_output=True, text=True)
        if not result.returncode != 0:
            logger.error(f"Could not run command: {cmd}. Result code: {result.returncode}")
        return ""

f = FusekiMetrics()
f._get_container_id()