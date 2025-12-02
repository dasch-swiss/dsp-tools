from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.project_client_live import ProjectInfoClientLive
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.project.models.project_definition import ProjectMetadata


def create_project(project: ProjectMetadata, auth: AuthenticationClient) -> str | CollectedProblems:
    client = ProjectInfoClientLive(auth.server)
