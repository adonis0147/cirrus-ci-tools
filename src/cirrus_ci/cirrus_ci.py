import json
import os.path
import textwrap
import time
from typing import Optional

import requests

from . import logger

log = logger.Logger().get()


class CirrusCI:
    def __init__(self, token: str, repository: str, branch: str):
        self.token = token
        self.repository = repository
        self.branch = branch
        self.url = "https://api.cirrus-ci.com/graphql"

    def request(self, query: str, variables: dict, token: Optional[str] = None):
        payload = {
            "query": textwrap.dedent(query).strip(),
            "variables": variables,
        }
        headers = {} if token is None else {"Authorization": "Bearer {}".format(token)}
        response = requests.post(self.url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()

    def get_repository_id(self) -> str:
        owner, name = self.repository.split("/")
        query = """
            query GetRepositoryID($owner: String!, $name: String!) {
                ownerRepository(platform: "github", owner: $owner, name: $name) {
                    id
                }
            }
        """
        variables = {"owner": owner, "name": name}
        response = self.request(query, variables)
        owner_repository = response["data"]["ownerRepository"]
        if owner_repository is None:
            raise RuntimeError(response)
        return owner_repository["id"]

    def create_build(self, repository_id: str, config: str = "") -> str:
        query = """
            mutation CreateBuild($repository_id: ID!, $branch: String!, $mutation_id: String!,
                    $configOverride: String) {
                createBuild(input: {
                    repositoryId: $repository_id,
                    branch: $branch,
                    clientMutationId: $mutation_id
                    configOverride: $configOverride
                }) {
                    build {
                        id,
                        status
                    }
                }
            }
        """
        variables = {
            "repository_id": repository_id,
            "branch": self.branch,
            "mutation_id": "Cirrus-CI build ({})".format(time.asctime()),
            "configOverride": self.read_config(config),
        }
        response = self.request(query, variables, self.token)
        create_build = response["data"]["createBuild"]
        if create_build is None:
            raise RuntimeError(response)

        build_info = create_build["build"]
        build_id, status = build_info["id"], build_info["status"]
        if status != "CREATED":
            raise RuntimeError("Failed to create build, status={}".format(status))
        return build_id

    def read_config(self, config: str) -> str:
        if os.path.isfile(config):
            with open(config, "r") as f:
                return f.read()
        return ""

    def wait_build(
        self,
        build_id: str,
        timeout: Optional[int] = None,
        interval: Optional[int] = None,
    ):
        query = """
            subscription QueryBuild($build_id: ID!) {
                build(id: $build_id) {
                    status
                }
            }
        """
        variables = {"build_id": build_id}

        timeout = 2 * 60 if timeout is None else timeout
        interval = 10 if interval is None else interval

        start_time = time.time()
        while (time.time() - start_time) / 60 < timeout:
            try:
                response = self.request(query, variables)
            except Exception as e:
                log.warning(str(e))
                time.sleep(interval * 2)
                continue

            build = response["data"]["build"]
            if build is None:
                raise RuntimeError(response)
            status = build["status"]
            log.info(
                "Check the status of the build, build_id={}, status={}, elapsed={}s".format(
                    build_id, status, round(time.time() - start_time, 2)
                )
            )
            if status not in ["CREATED", "TRIGGERED", "EXECUTING"]:
                return status
            time.sleep(interval)

    def get_task_ids(self, build_id: str) -> list[str]:
        query = """
            query QueryBuild($build_id: ID!) {
                build(id: $build_id) {
                    tasks {
                        id
                    }
                }
            }
        """
        variables = {"build_id": build_id}
        response = self.request(query, variables)
        build = response["data"]["build"]
        if build is None:
            raise RuntimeError(response)
        return [task["id"] for task in build["tasks"]]
