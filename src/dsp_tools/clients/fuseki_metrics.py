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
    communication_failure: bool = False

    def get_start_size(self) -> None:
        if not self.communication_failure:
            self.size_before = self._get_size()
        else:
            logger.error("Could not communicate with Fuseki. No size was requested.")

    def get_end_size(self) -> None:
        if not self.communication_failure:
            self.size_after = self._get_size()
        else:
            logger.error("Could not communicate with Fuseki. No size was requested.")

    def _get_size(self) -> int:
        if not self.container_id:
            self._get_container_id()
        cmd = f"docker exec '{self.container_id}' du -sb /fuseki 2>/dev/null | awk '{{print $1}}'"
        result = self._run_command(cmd)
        return int(result)

    def _get_container_id(self) -> None:
        cmd = "docker ps --format '{{.ID}} {{.Image}}' | grep 'daschswiss/apache-jena-fuseki' | awk '{print $1}'"
        if result := self._run_command(cmd):
            self.container_id = result

    def _run_command(self, cmd: str) -> str | None:
        result = subprocess.run(cmd, check=False, shell=True, capture_output=True, text=True)
        if not result.returncode != 0:
            logger.error(f"Could not run command: {cmd}. Result code: {result.returncode}")
            self.communication_failure = True
            return None
        return result.stdout.strip()


f = FusekiMetrics()
f._get_container_id()
