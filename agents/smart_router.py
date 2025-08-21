import asyncio 
import nest_asyncio
from acp_sdk.client import Client
from smolagents import LiteLLMModel
from fastacp import AgentCollection, ACPCallingAgent
from colorama import Fore
import os
from dotenv import load_dotenv

load_dotenv()
nest_asyncio.apply()

model = LiteLLMModel(
    model_id="anthropic/claude-sonnet-4-20250514",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

async def run_financial_workflow() -> None:
    """SmartRouter for Financial Advisory Platform using ACPCallingAgent"""
    
    print(f"{Fore.CYAN} Starting Financial Advisory SmartRouter...{Fore.RESET}\n")
    
   
    async with Client(base_url="http://localhost:8000") as financial_agents, \
               Client(base_url="http://localhost:8001") as market_agent:
        
        print(f"{Fore.BLUE} Discovering available agents...{Fore.RESET}")
        
       
        agent_collection = await AgentCollection.from_acp(financial_agents, market_agent)  
        acp_agents = {agent.name: {'agent': agent, 'client': client} for client, agent in agent_collection.agents}
        
        print(f"{Fore.GREEN}Found agents: {list(acp_agents.keys())}{Fore.RESET}\n")
        
        
        acpagent = ACPCallingAgent(acp_agents=acp_agents, model=model)
        
   
        test_queries = [
            "I want to invest $50,000 in a balanced portfolio for retirement",
            "Find me a financial advisor in Charlotte, NC who specializes in retirement planning", 
            "Research current renewable energy investment trends and recommend portfolio allocation",
            "I'm 35 years old, want to invest $100k, find an advisor in New York, and check current market conditions"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"{Fore.MAGENTA}{'='*60}")
            print(f"Test {i}: {query}")
            print(f"{'='*60}{Fore.RESET}")
            
            try:
                
                result = await acpagent.run(query)
                print(f"{Fore.YELLOW}SmartRouter Result:{Fore.RESET}\n{result}\n")
                
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Fore.RESET}\n")

if __name__ == "__main__":
    asyncio.run(run_financial_workflow())