# LMSystems SDK

The LMSystems SDK provides flexible interfaces for integrating and executing purchased graphs from the LMSystems marketplace in your Python applications. The SDK offers two main approaches:

1. **PurchasedGraph Class**: For seamless integration with LangGraph workflows
2. **LmsystemsClient**: For direct, low-level interaction with LMSystems graphs, offering more flexibility and control

### Try it in Colab

Get started quickly with our interactive Colab notebook:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/18IGOYcnN_CZSuH6RBwIjeXq9zMMs59OQ?usp=sharing)

This notebook provides a hands-on introduction to the LMSystems SDK with ready-to-run examples.

## Installation

Install the package using pip:

```bash
pip install lmsystems
```


## Quick Start

### Using the Client SDK

The client SDK provides direct interaction with LMSystems graphs:

```python
from lmsystems.client import LmsystemsClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Async usage
async def main():
    # Simple initialization with just graph name and API key
    client = await LmsystemsClient.create(
        graph_name="graph-name-id",
        api_key=os.environ["LMSYSTEMS_API_KEY"]
    )

    # Create thread and run with error handling
    try:
        thread = await client.create_thread()

        # No need to provide config - it's handled through your account settings
        run = await client.create_run(
            thread,
            input={"messages": [{"role": "user", "content": "What's this repo about?"}],
                  "repo_url": "",
                  "repo_path": "",
                  "github_token": ""}
        )

        # Stream response
        async for chunk in client.stream_run(thread, run):
            print(chunk)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Using PurchasedGraph with LangGraph

For integration with LangGraph workflows:

```python
from lmsystems.purchased_graph import PurchasedGraph
from langgraph.graph import StateGraph, START, MessagesState
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set required state values
state_values = {
    "repo_url": "https://github.com/yourusername/yourrepo",
    "github_token": "your-github-token",
    "repo_path": "/path/to/1234322"
}

# Initialize the purchased graph - no config needed!
purchased_graph = PurchasedGraph(
    graph_name="github-agent-6",
    api_key=os.environ.get("LMSYSTEMS_API_KEY"),
    default_state_values=state_values
)

# Create a parent graph with MessagesState schema
builder = StateGraph(MessagesState)
builder.add_node("purchased_node", purchased_graph)
builder.add_edge(START, "purchased_node")
graph = builder.compile()

# Invoke the graph
result = graph.invoke({
    "messages": [{"role": "user", "content": "what's this repo about?"}]
})

# Stream outputs (optional)
for chunk in graph.stream({
    "messages": [{"role": "user", "content": "what's this repo about?"}]
}, subgraphs=True):
    print(chunk)
```

## Configuration

### API Keys and Configuration
The SDK now automatically handles configuration through your LMSystems account. To set up:

1. Create an account at [LMSystems](https://www.lmsystems.ai)
2. Navigate to your [account settings](https://www.lmsystems.ai/account)
3. Configure your API keys (OpenAI, Anthropic, etc.)
4. Generate your LMSystems API key

Your configured API keys and settings will be automatically used when running graphs - no need to include them in your code!

> **Note**: While configuration is handled automatically, you can still override settings programmatically if needed:
```python
# Optional: Override stored config
config = {
    "configurable": {
        "model": "gpt-4",
        "openai_api_key": "your-custom-key"
    }
}
purchased_graph = PurchasedGraph(
    graph_name="github-agent-6",
    api_key=os.environ.get("LMSYSTEMS_API_KEY"),
    config=config  # Optional override
)
```

Store your LMSystems API key securely using environment variables:
```bash
export LMSYSTEMS_API_KEY="your-api-key"
```

## API Reference

### LmsystemsClient Class

```python
LmsystemsClient.create(
    graph_name: str,
    api_key: str
)
```

Parameters:
- `graph_name`: Name of the graph to interact with
- `api_key`: Your LMSystems API key

Methods:
- `create_thread()`: Create a new thread for graph execution
- `create_run(thread, input)`: Create a new run within a thread
- `stream_run(thread, run)`: Stream the output of a run
- `get_run(thread, run)`: Get the status and result of a run
- `list_runs(thread)`: List all runs in a thread

### PurchasedGraph Class

```python
PurchasedGraph(
    graph_name: str,
    api_key: str,
    config: Optional[RunnableConfig] = None,
    default_state_values: Optional[dict[str, Any]] = None
)
```

Parameters:
- `graph_name`: Name of the purchased graph
- `api_key`: Your LMSystems API key
- `config`: Optional configuration for the graph
- `default_state_values`: Default values for required state parameters

Methods:
- `invoke()`: Execute the graph synchronously
- `ainvoke()`: Execute the graph asynchronously
- `stream()`: Stream graph outputs synchronously
- `astream()`: Stream graph outputs asynchronously

## Error Handling

The SDK provides specific exceptions for different error cases:
- `AuthenticationError`: API key or authentication issues
- `GraphError`: Graph execution or configuration issues
- `InputError`: Invalid input parameters
- `APIError`: Backend communication issues

Example error handling:
```python
from lmsystems.exceptions import LmsystemsError

try:
    result = graph.invoke(input_data)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except GraphError as e:
    print(f"Graph execution failed: {e}")
except InputError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API communication error: {e}")
except LmsystemsError as e:
    print(f"General error: {e}")
```

## Support

For support, feature requests, or bug reports:
- Contact me at sean.sullivan3@yahoo.com