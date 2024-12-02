"""Apify Actor reader"""
from typing import Callable, Dict, List, Optional

from llama_index import download_loader
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document


class ApifyActor(BaseReader):
    """Apify Actor reader.
    Calls an Actor on the Apify platform and reads its resulting dataset when it finishes.

    Args:
        apify_api_token (str): Apify API token.
    """

    def __init__(self, apify_api_token: str) -> None:
        """Initialize the Apify Actor reader."""
        from apify_client import ApifyClient

        self.apify_api_token = apify_api_token
        self.apify_client = ApifyClient(apify_api_token)

    # async def fetch_run_status(self, run_id):
    #     import asyncio
    #     import requests
    #     from flask import current_app
    #     while True:
    #         try:
    #             token = current_app.config['APIFY_TOKEN']
    #             response = requests.get(
    #                 f"https://api.apify.com/v2/actor-runs/{run_id}/log?token={token}")
    #             response.raise_for_status()
    #             status_data = response.json()
    #             print(status_data)
    #             await asyncio.sleep(10)
    #         except Exception as e:
    #             await asyncio.sleep(10)

    def start_run(
        self,
        actor_id: str,
        run_input: Dict,
        *,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        content_type: Optional[str] = None,
        max_items: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
        wait_secs: Optional[int] = None,
    ) -> List[Document]:
        """Call an Actor on the Apify platform, wait for it to finish, and return its resulting dataset.
        Args:
            actor_id (str): The ID or name of the Actor.
            run_input (Any, optional): The input to pass to the actor run.
            content_type (str, optional): The content type of the input.
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the default run configuration for the actor (typically latest).
            max_items (int, optional): Maximum number of results that will be returned by this run.
                                       If the Actor is charged per result, you will not be charged for more results than the given limit.
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the default run configuration for the actor.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.
                                          By default, the run uses timeout specified in the default run configuration for the actor.
            webhooks (list, optional): Optional webhooks (https://docs.apify.com/webhooks) associated with the actor run,
                                       which can be used to receive a notification, e.g. when the actor finished or failed.
                                       If you already have a webhook set up for the actor, you do not have to add it again here.
            wait_secs (int, optional): The maximum number of seconds the server waits for the run to finish. If not provided, waits indefinitely.
        Returns:
            List[Document]: List of documents.
        """
        actor_run = self.apify_client.actor(actor_id).start(run_input=run_input,
                                                            build=build,
                                                            memory_mbytes=memory_mbytes,
                                                            timeout_secs=timeout_secs,
                                                            content_type=content_type,
                                                            max_items=max_items,
                                                            webhooks=webhooks,
                                                            wait_for_finish=wait_secs)

        return actor_run.get('id')

    def finish_run(self, run_id, wait_secs, dataset_mapping_function):
        started_run = self.apify_client.run(
            run_id=run_id).wait_for_finish(wait_secs=wait_secs)

        try:
            from llama_hub.utils import import_loader

            ApifyDataset = import_loader("ApifyDataset")
        except ImportError:
            ApifyDataset = download_loader("ApifyDataset")

        reader = ApifyDataset(self.apify_api_token)
        documents = reader.load_data(
            dataset_id=started_run.get("defaultDatasetId"),
            dataset_mapping_function=dataset_mapping_function,
        )

        return documents
