from lmsystems.client import SyncLmsystemsClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Synchronous usage
def main():
    # Simple initialization with just graph name and API key
    client = SyncLmsystemsClient(
        graph_name="stripe-expert-31",
        api_key=os.environ.get("LMSYSTEMS_API_KEY"),
        stream_mode=True
    )

    # Create thread and run with error handling
    try:
        thread = client.threads.create()

        run = client.create_run(
            thread,
            input={
                "messages": [{"role": "user", "content": "What's this repo about?"}],
                "repo_url": "https://github.com/RVCA212/airport-gaming",
                "github_token": "",
                "repo_path": "/users/152343"
            },
            config={
                "configurable": {
                    "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY"),
                }
            }
        )

        # Join run and print results
        for chunk in client.join_run(thread, run):
            print(chunk)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()