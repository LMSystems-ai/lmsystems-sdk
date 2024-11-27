import jwt
from typing import Any, Optional, Union
from langgraph.pregel.remote import RemoteGraph
from langchain_core.runnables import RunnableConfig
from langgraph.pregel.protocol import PregelProtocol
from langgraph_sdk.client import LangGraphClient, SyncLangGraphClient
import requests
import cryptography
from .exceptions import (
    InvalidAPIKeyError,
    GraphNotPurchasedError,
    GraphNotFoundError,
    BackendAPIError,
    LmsystemsError,
)
class PurchasedGraph(PregelProtocol):
    def __init__(
        self,
        graph_name: str,
        api_key: str,
        config: Optional[RunnableConfig] = None,
        default_state_values: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize a PurchasedGraph instance.

        Args:
            graph_name: The name of the purchased graph.
            api_key: The buyer's lmsystems API key.
            config: Optional RunnableConfig for additional configuration.
            default_state_values: Optional default values for required state parameters.
        """
        self.graph_name = graph_name
        self.api_key = api_key
        self.config = config
        self.default_state_values = default_state_values or {}

        # Authenticate and retrieve graph details from the marketplace backend
        self.graph_info = self._get_graph_info()

        # Decrypt the LangGraph API key
        decrypted_lgraph_api_key = self._decrypt_api_key(self.graph_info['access_token'])

        # Create internal RemoteGraph instance
        self.remote_graph = RemoteGraph(
            self.graph_info['graph_name'],
            url=self.graph_info['graph_url'],
            api_key=decrypted_lgraph_api_key,
            config=config,
        )

    def _get_graph_info(self) -> dict:
        """
        Authenticate with the marketplace backend and retrieve graph details.

        Returns:
            A dictionary containing graph details.

        Raises:
            InvalidAPIKeyError: If the API key is invalid.
            GraphNotPurchasedError: If the graph hasn't been purchased by the user.
            GraphNotFoundError: If the graph does not exist.
            BackendAPIError: For other backend errors.
        """
        endpoint = "http://127.0.0.1:8000/api/get_graph_info"  # Local testing
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"graph_name": self.graph_name}

        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 401:
            raise InvalidAPIKeyError("Invalid lmsystems API key.")
        elif response.status_code == 403:
            raise GraphNotPurchasedError(f"You have not purchased the graph '{self.graph_name}'.")
        elif response.status_code == 404:
            raise GraphNotFoundError(f"Graph '{self.graph_name}' not found.")
        elif response.status_code != 200:
            raise BackendAPIError(f"Backend API error: {response.text}")

        return response.json()

    def _decrypt_api_key(self, access_token: str) -> str:
        """
        Extract the LangGraph API key from the JWT token.

        Args:
            access_token: JWT token containing the API key

        Returns:
            The LangGraph API key

        Raises:
            LmsystemsError: If there are any issues with the token
        """
        try:
            # Decode JWT token
            SECRET_KEY = "your_secret_key"  # This should match the backend
            decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])

            # Extract the API key
            lgraph_api_key = decoded_token.get("lgraph_api_key")
            if not lgraph_api_key:
                raise LmsystemsError("API key not found in token.")

            return lgraph_api_key

        except jwt.ExpiredSignatureError:
            raise LmsystemsError("Access token has expired.")
        except jwt.DecodeError:
            raise LmsystemsError("Error decoding access token.")
        except Exception as e:
            raise LmsystemsError(f"Error processing API key: {e}")

    def _prepare_input(self, input: Union[dict[str, Any], Any]) -> dict[str, Any]:
        """Merge input with default state values."""
        if isinstance(input, dict):
            return {**self.default_state_values, **input}
        return input

    # Delegate methods to the internal RemoteGraph instance
    def invoke(self, input: Union[dict[str, Any], Any], config: Optional[RunnableConfig] = None, **kwargs: Any) -> Union[dict[str, Any], Any]:
        prepared_input = self._prepare_input(input)
        return self.remote_graph.invoke(prepared_input, config=config, **kwargs)

    async def ainvoke(self, input: Union[dict[str, Any], Any], config: Optional[RunnableConfig] = None, **kwargs: Any) -> Union[dict[str, Any], Any]:
        prepared_input = self._prepare_input(input)
        return await self.remote_graph.ainvoke(prepared_input, config=config, **kwargs)

    def stream(self, input: Union[dict[str, Any], Any], config: Optional[RunnableConfig] = None, **kwargs: Any):
        prepared_input = self._prepare_input(input)
        return self.remote_graph.stream(prepared_input, config=config, **kwargs)

    async def astream(self, input: Union[dict[str, Any], Any], config: Optional[RunnableConfig] = None, **kwargs: Any):
        async for chunk in self.remote_graph.astream(input, config=config, **kwargs):
            yield chunk


    def with_config(self, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:
        return self.remote_graph.with_config(config, **kwargs)

    def get_graph(self, config: Optional[RunnableConfig] = None, *, xray: Union[int, bool] = False) -> Any:
        return self.remote_graph.get_graph(config=config, xray=xray)

    async def aget_graph(self, config: Optional[RunnableConfig] = None, *, xray: Union[int, bool] = False) -> Any:
        return await self.remote_graph.aget_graph(config=config, xray=xray)

    def get_state(self, config: RunnableConfig, *, subgraphs: bool = False) -> Any:
        return self.remote_graph.get_state(config=config, subgraphs=subgraphs)

    async def aget_state(self, config: RunnableConfig, *, subgraphs: bool = False) -> Any:
        return await self.remote_graph.aget_state(config=config, subgraphs=subgraphs)

    def get_state_history(self, config: RunnableConfig, *, filter: Optional[dict[str, Any]] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None) -> Any:
        return self.remote_graph.get_state_history(config=config, filter=filter, before=before, limit=limit)

    async def aget_state_history(self, config: RunnableConfig, *, filter: Optional[dict[str, Any]] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None) -> Any:
        return await self.remote_graph.aget_state_history(config=config, filter=filter, before=before, limit=limit)

    def update_state(self, config: RunnableConfig, values: Optional[Union[dict[str, Any], Any]], as_node: Optional[str] = None) -> RunnableConfig:
        return self.remote_graph.update_state(config=config, values=values, as_node=as_node)

    async def aupdate_state(self, config: RunnableConfig, values: Optional[Union[dict[str, Any], Any]], as_node: Optional[str] = None) -> RunnableConfig:
        return await self.remote_graph.aupdate_state(config=config, values=values, as_node=as_node)

    def with_config(self, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:
        return self.remote_graph.with_config(config, **kwargs)

    def get_graph(self, config: Optional[RunnableConfig] = None, *, xray: Union[int, bool] = False) -> Any:
        return self.remote_graph.get_graph(config=config, xray=xray)

    async def aget_graph(self, config: Optional[RunnableConfig] = None, *, xray: Union[int, bool] = False) -> Any:
        return await self.remote_graph.aget_graph(config=config, xray=xray)

    def get_state(self, config: RunnableConfig, *, subgraphs: bool = False) -> Any:
        return self.remote_graph.get_state(config=config, subgraphs=subgraphs)

    async def aget_state(self, config: RunnableConfig, *, subgraphs: bool = False) -> Any:
        return await self.remote_graph.aget_state(config=config, subgraphs=subgraphs)

    def get_state_history(self, config: RunnableConfig, *, filter: Optional[dict[str, Any]] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None) -> Any:
        return self.remote_graph.get_state_history(config=config, filter=filter, before=before, limit=limit)

    async def aget_state_history(self, config: RunnableConfig, *, filter: Optional[dict[str, Any]] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None) -> Any:
        return await self.remote_graph.aget_state_history(config=config, filter=filter, before=before, limit=limit)

    def update_state(self, config: RunnableConfig, values: Optional[Union[dict[str, Any], Any]], as_node: Optional[str] = None) -> RunnableConfig:
        return self.remote_graph.update_state(config=config, values=values, as_node=as_node)

    async def aupdate_state(self, config: RunnableConfig, values: Optional[Union[dict[str, Any], Any]], as_node: Optional[str] = None) -> RunnableConfig:
        return await self.remote_graph.aupdate_state(config=config, values=values, as_node=as_node)
