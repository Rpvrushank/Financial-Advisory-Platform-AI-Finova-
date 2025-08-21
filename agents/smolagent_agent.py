
from collections.abc import AsyncGenerator
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
from acp_sdk.models import Message, MessagePart
from smolagents import CodeAgent, DuckDuckGoSearchTool, VisitWebpageTool, LiteLLMModel
import os
from dotenv import load_dotenv
load_dotenv()

import asyncio


server = Server()

model = LiteLLMModel(
    model_id = "anthropic/claude-sonnet-4-20250514",
    api_key = os.getenv("ANTHROPIC_API_KEY"),
    max_tokens = 2048,
    temperature = 0.2,
)

@server.agent()
async def market_researcher(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    "Market Researcher Agent that gathers and summarizes market data."
    try:
        # Add input validation first
        if not input or len(input) == 0:
            yield Message(parts=[MessagePart(content="No input received for market research.")])
            return
            
        if not input[0].parts or len(input[0].parts) == 0:
            yield Message(parts=[MessagePart(content="Invalid input format received.")])
            return
            
        prompt = input[0].parts[0].content
        print(f"Market researcher processing: {prompt}")
        
        # Create agent with web tools
        agent = CodeAgent(tools=[DuckDuckGoSearchTool(), VisitWebpageTool()], model=model)
        
        # Add timeout protection (30 seconds max)
        response = await asyncio.wait_for(
            asyncio.to_thread(agent.run, prompt),
            timeout=90.0
        )
        
        yield Message(parts=[MessagePart(content=str(response))])
        
    except asyncio.TimeoutError:
        # Fallback to local analysis if web search times out
        yield Message(parts=[MessagePart(content="Web search timed out. Providing analysis based on general market knowledge...")])
        
    except Exception as e:
        print(f"Market researcher error: {e}")
        import traceback
        traceback.print_exc()
        yield Message(parts=[MessagePart(content=f"Market research unavailable: {str(e)}")])

if __name__ == "__main__":
    print("Starting ACP server...")
    server.run(port=8001)
