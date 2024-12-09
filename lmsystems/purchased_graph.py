import jwt
from typing import Any, Optional, Union
from langgraph.pregel.remote import RemoteGraph
from langchain_core.runnables import RunnableConfig
from langgraph.pregel.protocol import PregelProtocol
from langgraph_sdk.client import LangGraphClient, SyncLangGraphClient
import requests
from .exceptions import (
    LmsystemsError,
    AuthenticationError,
    GraphError,
    InputError,
    APIError
)
import os
from lmsystems.config import Config

class PurchasedGraph(PregelProtocol):
    def __init__(
        self,
        graph_name: str,
        api_key: str,
        config: Optional[RunnableConfig] = None,
        default_state_values: Optional[dict[str, Any]] = None,
        base_url: str = Config.DEFAULT_BASE_URL,
        development_mode: bool = False,
    ):
        """
        Initialize a PurchasedGraph instance.

        Args:
            graph_name: The name of the purchased graph.
            api_key: The buyer's lmsystems API key.
            config: Optional RunnableConfig for additional configuration.
            default_state_values: Optional default values for required state parameters.
            base_url: The base URL of the marketplace backend.
            development_mode: Whether to run in development mode.

        Raises:
            AuthenticationError: If the API key is invalid
            GraphError: If the graph doesn't exist or hasn't been purchased
            InputError: If required configuration is invalid
            APIError: If there are backend communication issues
        """
        if not api_key:
            raise AuthenticationError("API key is required.")
        if not graph_name:
            raise InputError("Graph name is required")

        self.graph_name = graph_name
        self.api_key = api_key
        self.config = config
        self.default_state_values = default_state_values or {}
        self.base_url = base_url
        self.development_mode = development_mode

        try:
            # Authenticate and retrieve graph details
            self.graph_info = self._get_graph_info()

            # Extract the LangGraph API key from token
            lgraph_api_key = self._extract_api_key(self.graph_info['access_token'])

            # Create internal RemoteGraph instance
            self.remote_graph = RemoteGraph(
                self.graph_info['graph_name'],
                url=self.graph_info['graph_url'],
                api_key=lgraph_api_key,
                config=config,
            )
        except Exception as e:
            raise APIError(f"Failed to initialize graph: {str(e)}")

    def _get_graph_info(self) -> dict:
        """Authenticate with the marketplace backend and retrieve graph details."""
        try:
            endpoint = f"{self.base_url}/api/get_graph_info"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {"graph_name": self.graph_name}

            response = requests.post(endpoint, json=payload, headers=headers)

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key.")
            elif response.status_code == 403:
                raise GraphError(f"Graph '{self.graph_name}' has not been purchased")
            elif response.status_code == 404:
                raise GraphError(f"Graph '{self.graph_name}' not found")
            elif response.status_code != 200:
                raise APIError(f"Backend API error: {response.text}")

            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to communicate with backend: {str(e)}")

    def _extract_api_key(self, access_token: str) -> str:
        """Extract the LangGraph API key from the JWT token without verification."""
        try:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            lgraph_api_key = decoded_token.get("lgraph_api_key")
            if not lgraph_api_key:
                raise GraphAuthenticationError("LangGraph API key not found in token payload")
            return lgraph_api_key
        except jwt.InvalidTokenError as e:
            raise GraphAuthenticationError(f"Invalid access token: {str(e)}")
        except Exception as e:
            raise GraphAuthenticationError(f"Failed to decode token: {str(e)}")

    def _prepare_input(self, input: Union[dict[str, Any], Any]) -> dict[str, Any]:
        """Merge input with default state values."""
        try:
            if isinstance(input, dict):
                return {**self.default_state_values, **input}
            return input
        except Exception as e:
            raise ValidationError(f"Failed to prepare input: {str(e)}")

    # Delegate methods to the internal RemoteGraph instance
    def invoke(self, input: Union[dict[str, Any], Any], config: Optional[RunnableConfig] = None, **kwargs: Any) -> Union[dict[str, Any], Any]:
        """
        Invoke the graph with the given input.

        Args:
            input: The input for the graph
            config: Optional configuration override
            **kwargs: Additional arguments

        Raises:
            InputError: If the input is invalid
            GraphError: If graph execution fails
            APIError: If there are communication issues
        """
        try:
            prepared_input = self._prepare_input(input)
            return self.remote_graph.invoke(prepared_input, config=config, **kwargs)
        except Exception as e:
            if isinstance(e, LmsystemsError):
                raise
            raise GraphError(f"Failed to execute graph: {str(e)}")

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
