"""
Rasa Model
---------------

This module provides an annotator model
that queries an external RASA NLU Server for utterance classification.
"""
import asyncio
import time
import json
from urllib.parse import urljoin
from typing import Optional

import requests

try:
    import httpx

    rasa_available = True
except ImportError:
    htppx = object()
    rasa_available = False

from ...utils import RasaResponse
from ..base_model import BaseModel
from ...utils import STATUS_SUCCESS, STATUS_UNAVAILABLE
from .async_mixin import AsyncMixin


class AbstractRasaModel(BaseModel):
    """
    Abstract class for a RASA annotator.
    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        namespace_key: Optional[str] = None,
        *,
        retries: int = 10,
        headers: Optional[dict] = None,
    ):
        super().__init__(namespace_key=namespace_key)
        self.headers = headers or {"Content-Type": "application/json"}
        health_check = requests.get(model)
        health_check.raise_for_status()
        self.parse_url = urljoin(model, ("model/parse" + (f"?token={api_key}" if api_key else "")))
        self.train_url = urljoin(model, ("model/train" + (f"?token={api_key}" if api_key else "")))
        if jwt_token is not None:
            self.headers["Authorization"] = "Bearer " + jwt_token
        self.retries = retries


class RasaModel(AbstractRasaModel):
    """
    This class implements a synchronous connection to RASA NLU server for dialog annotation.
    In order to work with this class, you need to have a running instance of Rasa NLU Server
    with the model trained to recognize your intents.
    Please, refer to the `RASA docs <https://rasa.com/docs/rasa/nlu-only-server>`_ on how to
    develop a RASA project and launch an NLU-only server.

    :param model: Rasa model url.
    :param api_key: Rasa api key for request authorization. The exact authentification method can be retrieved
        from your Rasa Server config.
    :param jwt_token: Rasa jwt token for request authorization. The exact authentification method can be retrieved
        from your Rasa Server config.
    :param namespace_key: Name of the namespace in framework states that the model will be using.
    :param retries: The number of times requests will be repeated in case of failure.
    :param headers: Fill in this parameter, if you want to override the standard set of headers with custom headers.

    """

    def predict(self, request: str) -> dict:
        message = {"text": request}
        retries = 0
        while retries < self.retries:
            retries += 1
            response: requests.Response = requests.post(self.parse_url, headers=self.headers, data=json.dumps(message))
            if response.status_code == STATUS_UNAVAILABLE:
                time.sleep(1)
            elif response.status_code == STATUS_SUCCESS:
                break
            else:
                raise requests.HTTPError(str(response.status_code) + " " + response.text)

        json_response = response.json()
        parsed = RasaResponse.model_validate(json_response)
        result = {item.name: item.confidence for item in parsed.intent_ranking} if parsed.intent_ranking else dict()
        return result


class AsyncRasaModel(AsyncMixin, AbstractRasaModel):
    """
    This class implements an asynchronous connection to RASA NLU server for dialog annotation.
    In order to work with this class, you need to have a running instance of Rasa NLU Server
    with the model trained to recognize your intents.
    Please, refer to the `RASA docs <https://rasa.com/docs/rasa/nlu-only-server>`_ on how to
    develop a RASA project and launch an NLU-only server.

    :param model: Rasa model url.
    :param api_key: Rasa api key for request authorization. The exact authentification method can be retrieved
        from your Rasa Server config.
    :param jwt_token: Rasa jwt token for request authorization. The exact authentification method can be retrieved
        from your Rasa Server config.
    :param namespace_key: Name of the namespace in framework states that the model will be using.
    :param retries: The number of times requests will be repeated in case of failure.
    :param headers: Fill in this parameter, if you want to override the standard set of headers with custom headers.

    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        namespace_key: Optional[str] = None,
        *,
        retries: int = 10,
        headers: Optional[dict] = None,
    ):
        if not rasa_available:
            raise ImportError("`httpx` package missing. Try `pip install dff[httpx]`")
        super().__init__(model, api_key, jwt_token, namespace_key, retries=retries, headers=headers)

    async def predict(self, request: str) -> dict:
        client = httpx.AsyncClient()
        message = {"text": request}
        retries = 0
        while retries < self.retries:
            retries += 1
            response: httpx.Response = await client.post(self.parse_url, headers=self.headers, data=json.dumps(message))
            if response.status_code == STATUS_UNAVAILABLE:  # Wait for model to warm up
                await asyncio.sleep(1)
            elif response.status_code == STATUS_SUCCESS:
                break
            else:
                raise httpx.HTTPStatusError(str(response.status_code) + " " + response.text)

        json_response = response.json()
        parsed = RasaResponse.model_validate(json_response)
        result = {item.name: item.confidence for item in parsed.intent_ranking} if parsed.intent_ranking else dict()

        await client.aclose()
        return result