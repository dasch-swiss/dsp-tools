import getpass
import os
import subprocess
import warnings
from typing import Literal

import pyperf

# ruff: noqa:S607 (Starting a process with a partial executable path)


def setup_sudo() -> str:
    """Get sudo password once at script start"""
    return getpass.getpass(prompt="Enter sudo password for cache clearing: ")


def clear_mac_system_caches(sudo_password: str) -> None:
    """Sync filesystem with 'sync' and clear system caches using 'sudo -S purge'"""
    subprocess.run(["sync"], check=False)
    process = subprocess.Popen(
        ["sudo", "-S", "purge"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate(input=sudo_password + "\n")
    if not process.returncode == 0:
        warnings.warn("Failed to clear system caches")


def setup(sudo_password: str) -> None:
    clear_mac_system_caches(sudo_password)


def teardown() -> None:
    subprocess.run(["dsp-tools", "stop-stack"], check=True)


def task_to_measure():
    subprocess.run(["dsp-tools", "start-stack", "--no-prune"], check=True)


def run_performance_tests():
    container_engine: Literal["podman", "docker"] = "podman"
    os.environ["CONTAINER_ENGINE"] = container_engine
    sudo_password = setup_sudo()

    runner = pyperf.Runner()
    runner.timeit(
        name="run start-stack", stmt="task_to_measure()", setup="setup(sudo_password)", teardown="teardown()"
    )
