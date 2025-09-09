import shlex
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
            if size := self._get_size():
                self.size_before = size

    def get_end_size(self) -> None:
        if not self.communication_failure:
            if size := self._get_size():
                self.size_after = size

    def _get_size(self) -> int | None:
        if not self.container_id:
            self._get_container_id()
        if not self.container_id:
            logger.error("Could not retrieve container ID")
            return None
        if result := self._run_command(["docker", "exec", self.container_id, "du", "-sb", "/fuseki"]):
            try:
                size_str = result.split()[0]
                return int(size_str)
            except (ValueError, IndexError):
                logger.error("Could not parse size from du command output.")
        return None

    def _get_container_id(self) -> None:
        if result := self._run_command(["docker", "ps", "--format", "{{.ID}} {{.Image}}"]):
            for line in result.splitlines():
                parts = shlex.split(line)
                if len(parts) == 2 and "daschswiss/apache-jena-fuseki" in parts[1]:
                    self.container_id = parts[0]
                    return
        logger.error("Could not find Fuseki container ID.")
        self.communication_failure = True

    def _run_command(self, cmd: list[str]) -> str | None:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, shell=isinstance(cmd, str))
        result_str = f"Result code: {result.returncode}, Message: {result.stdout}"
        if result.returncode != 0:
            logger.error(f"Could not run command: {cmd}. {result_str}")
            self.communication_failure = True
            return None
        logger.debug(f"Command output, {result_str}")
        return result.stdout.strip()
