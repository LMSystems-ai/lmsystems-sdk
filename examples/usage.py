from lmsystems.purchased_graph import PurchasedGraph
from langgraph.graph import StateGraph, START, MessagesState

# Define required state values
state_values = {
    "repo_url": "https://github.com/RVCA212/portfolio-starter-kit",
    "github_token": "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",
    "repo_path": "/repo"
}

# Instantiate the purchased graph with default state values
purchased_graph = PurchasedGraph(
    graph_name="engineer",
    api_key="abc123securetestkey",
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

# You can also override default values when needed
result_with_different_repo = graph.invoke({
    "messages": [{"role": "user", "content": "what's this repo about?"}],
    "repo_url": "https://github.com/different/repo"  # This will override the default
})
