from lmsystems.client import LmsystemsClient
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# Async usage
async def main():
    # Simple initialization with just graph name and API key
    client = await LmsystemsClient.create(
        graph_name="stripe-expert-31",
        api_key=os.environ.get("LMSYSTEMS_API_KEY")
    )

    # Create thread and run with error handling
    try:
        thread = await client.create_thread()

        run = await client.create_run(
            thread,
            input={"messages": [{"role": "user", "content": "What's this repo about?"}],
            "repo_url": "https://github.com/RVCA212/airport-gaming",
            "github_token": "",
            "repo_path": "/users/152343"},
            config={
                "configurable": {
                    "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY"),
                }
            }
        )

        # Stream response
        async for chunk in client.stream_run(thread, run):
            print(chunk)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())