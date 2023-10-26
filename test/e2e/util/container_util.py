# from dataclasses import dataclass
# import subprocess
from time import sleep

from testcontainers.compose import DockerCompose

# import requests


# # from testcontainers.core.container import DockerContainer
# # from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for, wait_for_logs

# # from dsp_tools.utils.create_logger import get_logger


# # @dataclass
# # class Stack:
# #     db: DockerContainer
# #     api: DockerContainer
# #     sipi: DockerContainer


# # def _start_stack() -> Stack:
# #     with (
# #         DockerContainer("daschswiss/apache-jena-fuseki:latest")
# #         .with_bind_ports(3030)
# #         .with_env("ADMIN_PASSWORD", "test") as db_container
# #     ):
# #         r = wait_container_is_ready(db_container)
# #         print("DB container is ready")
# #         print(r)
# #         return Stack(db_container, None, None)


# # def test_run_stack(stack: Stack) -> None:
# #     sleep(3)
# #     assert stack == [1]


def run() -> None:
    # compose = DockerCompose("testdata/docker", "docker-compose.yml")
    with DockerCompose("testdata/docker", "docker-compose.yml") as compose:
        print(compose.get_service_host("db", 3030))
        do_something()
        print("done")
    # compose._call_command("docker-compose pull")
    # compose._call_command("docker-compose up -d db")

    # # Do something with the container
    # sleep(1)
    # print(compose.get_service_host("db", 3030))
    # sleep(2)


def do_something() -> None:
    print("doing something here...")
    sleep(1)
    print("doing something here...")
    sleep(1)
    print("doing something here...")
    sleep(1)
    print("doing something here...")
    sleep(1)
    print("doing something here...")
    sleep(1)


# # def run() -> None:
# #     db = _start_db()
# #     sleep(3)
# #     _stop_all(db)


# # def _start_db() -> DockerContainer:
# #     db = (
# #         DockerContainer("daschswiss/apache-jena-fuseki:latest")
# #         .with_bind_ports(3030)
# #         .with_name("db-1")
# #         .with_env("ADMIN_PASSWORD", "test")
# #     )
# #     db.start()
# #     port = db.get_exposed_port(3030)
# #     host = db.get_container_host_ip()
# #     url = f"http://{host}:{port}/$/ping"
# #     _await_container(url)
# #     print("DB container is ready")
# #     db.get_wrapped_container
# #     return db


# # def _await_container(url: str) -> None:
# #     while True:
# #         sleep(0.1)
# #         try:
# #             res = requests.get(url, timeout=1)
# #             if res.status_code == 200:
# #                 break
# #         except requests.exceptions.ConnectionError:
# #             pass


# # def _stop_all(*containers: DockerContainer) -> None:
# #     for container in containers:
# #         container.stop()


# def run() -> None:
#     start_stack()
#     print("Stack started")
#     print("doing something here...")
#     sleep(3)
#     stop_stack()
#     print("Stack stopped")


# def start_stack() -> None:
#     _start_db()
#     _await_db()
#     _init_db()  # XXX: add args here
#     _start_rest()
#     _await_api()


# def _start_db() -> None:
#     print("starting db container...")
#     # XXX: implement
#     print("db container started")


# def _await_db() -> None:
#     # XXX: implement
#     print("db container is ready")


# def _init_db() -> None:
#     print("initializing db...")
#     # XXX: implement
#     print("db initialized")


# def _start_rest() -> None:
#     print("starting api, sipi and ingest containers...")
#     # XXX: implement
#     print("containers started")


# def _await_api() -> None:
#     print("waiting for api...")
#     # XXX: implement
#     print("api container is ready")


# def stop_stack() -> None:
#     subprocess.run("docker compose down --volumes", shell=True, cwd=self.__docker_path_of_user, check=True)


if __name__ == "__main__":
    run()
