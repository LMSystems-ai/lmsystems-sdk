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
        graph_name="github-agent-6",
        api_key=os.environ["LMSYSTEMS_API_KEY"]
    )

    # Create thread and run with error handling
    try:
        thread = await client.create_thread()

        run = await client.create_run(
            thread,
            input={"messages": [{"role": "user", "content": "What's this repo about?"}],
                  "repo_url": "hello.com",
                  "repo_path": "/12344322",
                  "github_token": ""}
        )

        # Stream response
        async for chunk in client.stream_run(thread, run):
            print(chunk)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())