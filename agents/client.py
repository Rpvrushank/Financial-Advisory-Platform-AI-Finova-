import nest_asyncio
nest_asyncio.apply()
import asyncio
from acp_sdk.client import Client

async def test_agents():
    async with Client(base_url="http://127.0.0.1:8000") as crewagent_client:
        print("Testing investment agent")
        run1 = await crewagent_client.run_sync(
            agent="investment_agent",
            input="I want to invest $50,000 in a balanced portfolio"
        )
        print("Investment Agent Response:")
        print(run1.output[0].parts[0].content)

        print("\n"  +  "-"*50 + "\n")

        print("Testing Advisor Finder agent")
        run2 = await crewagent_client.run_sync(
            agent = "advisor_finder",
            input= "Find me a financial advisor in Charlotte, NC who specializes in retirement planning"
            )
        print("Advisor agent Response:")
        print(run2.output[0].parts[0].content)

        print("\n"  +  "-"*50 + "\n")

    async with Client(base_url="http://127.0.0.1:8001") as smolagent_client:

        print("Market Researcher agent")
        run3 = await smolagent_client.run_sync(
            agent = "market_researcher",
            input = "Summarize the latest trends in renewable energy investments"
        )

        print("Market Researcher agent Response:")
        print(run3.output[0].parts[0].content)

if __name__ == "__main__":
    asyncio.run(test_agents())