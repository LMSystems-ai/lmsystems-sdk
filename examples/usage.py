from lmsystems.purchased_graph import PurchasedGraph
from langgraph.graph import StateGraph, START, MessagesState
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define your configuration
config = {
    "configurable": {
        "model": "anthropic",
        "anthropic_api_key": ""
    }
}

# Define required state values
state_values = {
    "repo_url": "https://github.com/RVCA212/airport-gaming",
    "github_token": "",
    "repo_path": "/repo/152343"
}

# Instantiate the purchased graph with the config
purchased_graph = PurchasedGraph(
    graph_name="github-agent-6",
    api_key=os.environ.get("LMSYSTEMS_API_KEY"),
    config=config,
    default_state_values=state_values
)

# Define your parent graph with MessagesState schema
builder = StateGraph(MessagesState)
builder.add_node("purchased_node", purchased_graph)
builder.add_edge(START, "purchased_node")
graph = builder.compile()

# Now you can invoke with just the messages, other state values are automatically included
result = graph.invoke({
    "messages": [{"role": "user", "content": "what's this repo about?"}]
})
print(result)

# Optional: Stream outputs
for chunk in graph.stream({
    "messages": [{"role": "user", "content": "what's this repo about?"}]
}, subgraphs=True):
    print(chunk)

