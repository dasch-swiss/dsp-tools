import shlex
import subprocess
from dataclasses import dataclass
from enum import Enum
from enum import auto

from loguru import logger


class FusekiBloatingLevel(Enum):
    NON_CRITICAL = auto()
    WARNING = auto()
    CRITICAL = auto()


@dataclass
class FusekiMetrics:
    container_id: str | None = None
    size_before: int | None = None
    size_after: int | None = None

    def get_start_size(self) -> None:
        self.size_before = self._get_size()

    def get_end_size(self) -> None:
        self.size_after = self._get_size()

    def _get_size(self) -> int | None:
        if not self.container_id:
            self._get_container_id()
        if not self.container_id:
            return None
        if result := self._run_command(["docker", "exec", self.container_id, "du", "-sb", "/fuseki"]):
            try:
                size_str = result.split()[0]
                return int(size_str)
            except (ValueError, IndexError):
                logger.error("Could not parse size from du command output.")
                self.communication_failure = True
                return None
        return None

    def _get_container_id(self) -> None:
        if result := self._run_command(["docker", "ps", "--format", "{{.ID}} {{.Image}}"]):
            for line in result.splitlines():
                parts = shlex.split(line)
                if len(parts) == 2 and "daschswiss/apache-jena-fuseki" in parts[1]:
                    self.container_id = parts[0]
                    return
        logger.error("Could not find Fuseki container ID.")

    def _run_command(self, cmd: list[str]) -> str | None:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        result_str = f"Result code: {result.returncode}, Message: {result.stdout}"
        if result.returncode != 0:
            logger.error(f"Could not run command: {cmd}. {result_str}")
            self.communication_failure = True
            return None
        logger.debug(f"Command output, {result_str}")
        return result.stdout.strip()
