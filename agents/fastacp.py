from typing import Dict, List, Any, Optional
from acp_sdk.client import Client
import asyncio
import time
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastacp")

class Agent:
    """Represents an ACP agent with metadata"""
    def __init__(self, name: str, description: str = "", port: int = None):
        self.name = name
        self.description = description
        self.port = port

class AgentCollection:
    """Collection of discovered ACP agents"""
    
    def __init__(self):
        self.agents = []
    
    @classmethod
    async def from_acp(cls, *clients: Client):
        """Discover agents from ACP clients"""
        collection = cls()
        
        
        agent_configs = [
            
            {"name": "investment_agent", "port": 8000, "description": "Investment advice and portfolio recommendations"},
            {"name": "advisor_finder", "port": 8000, "description": "Financial advisor recommendations by location"},
            
            
            {"name": "market_researcher", "port": 8001, "description": "Market trends and research analysis"},
        ]
        
        logger.info("Discovering ACP agents...")
        
     
        client_port_map = {}
        for i, client in enumerate(clients):
            port = 8000 + i
            client_port_map[port] = client
            logger.info(f"Client {i+1} mapped to port {port}")
        
        
        for config in agent_configs:
            port = config["port"]
            if port in client_port_map:
                client = client_port_map[port]
                agent = Agent(
                    name=config["name"], 
                    description=config["description"],
                    port=port
                )
                collection.agents.append((client, agent))
                logger.info(f" Found agent: {config['name']} on port {port}")
        
        logger.info(f"Agent discovery complete. Found {len(collection.agents)} agents.")
        return collection

class ACPCallingAgent:
    """
    Production-ready agent that orchestrates multiple ACP agents
    Optimized for performance and cost-efficiency
    """
    
    def __init__(self, acp_agents: Dict[str, Dict[str, Any]], model):
        self.acp_agents = acp_agents
        self.model = model
        self._call_stats = {"total_calls": 0, "successful_calls": 0, "failed_calls": 0}
        
        logger.info(f"ACPCallingAgent initialized with {len(acp_agents)} agents")
        logger.info(f"Available agents: {list(acp_agents.keys())}")
    
    async def run(self, query: str) -> str:
        """
        Execute query with intelligent agent orchestration
        """
        start_time = time.time()
        
        try:
          
            agent_calls = self._determine_agents(query)
            
            if not agent_calls:
                return "No suitable agents found for this query. Please rephrase your financial question."
            
            logger.info(f"Routing to agents: {[call['agent'] for call in agent_calls]}")
            
            
            results = await self._execute_agent_calls(agent_calls)
            
         
            final_result = self._synthesize_results(results, query)
            
        
            execution_time = time.time() - start_time
            logger.info(f"⚡ Query completed in {execution_time:.2f}s")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in ACPCallingAgent: {str(e)}")
            return f"System error occurred. Please try again. (Error: {str(e)})"
    
    def _determine_agents(self, query: str) -> List[Dict[str, str]]:
        """
        Exclusive keyword-based agent routing
        Returns only ONE agent per query
        """
        query_lower = query.lower().strip()
        
        investment_keywords = [
            'invest', 'portfolio', 'allocation', 'diversif', 'risk', 'return', 
            'retirement', 'savings', 'wealth', '401k', 'ira', 'mutual fund',
            'etf', 'stock', 'bond', 'asset', 'financial planning', 'money'
        ]
        
        advisor_keywords = [
            'find advisor', 'find adviser', 'recommend advisor', 'recommend adviser',
            'financial planner', 'need advisor', 'looking for advisor',
            'advisor in charlotte', 'advisor in new york', 'advisor in miami',
            'cfp advisor', 'cfa advisor', 'find financial advisor'
        ]
        
        market_keywords = [
            'market', 'trend', 'research', 'analysis', 'outlook', 'economic',
            'sector', 'industry', 'current', 'news', 'performance', 'renewable',
            'energy', 'tech', 'technology'
        ]
        
        # Check market keywords first
        if any(keyword in query_lower for keyword in market_keywords):
            if 'market_researcher' in self.acp_agents:
                return [{
                    'agent': 'market_researcher',
                    'query': query,
                    'priority': 1
                }]
        
        # Check advisor keywords
        if any(keyword in query_lower for keyword in advisor_keywords):
            if 'advisor_finder' in self.acp_agents:
                return [{
                    'agent': 'advisor_finder', 
                    'query': query,
                    'priority': 1
                }]
        
        # Check investment keywords
        if any(keyword in query_lower for keyword in investment_keywords):
            if 'investment_agent' in self.acp_agents:
                return [{
                    'agent': 'investment_agent',
                    'query': query,
                    'priority': 1
                }]
        
        # Fallback for general financial terms
        if any(word in query_lower for word in ['financial', 'finance', 'dollar', '$']):
            return [{
                'agent': 'investment_agent',
                'query': query,
                'priority': 3
            }]
        
        # Final fallback
        return [{
            'agent': 'investment_agent',
            'query': query,
            'priority': 4
        }]
    
    async def _execute_agent_calls(self, agent_calls: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Execute agent calls with error handling"""
        results = []
        
        
        for call_info in agent_calls:
            agent_name = call_info['agent']
            query = call_info['query']
            
            try:
                logger.info(f" Calling {agent_name}...")
                result = await self._call_agent(agent_name, query)
                
                results.append({
                    'agent': agent_name,
                    'result': result,
                    'success': True
                })
                
                self._call_stats["successful_calls"] += 1
                logger.info(f"{agent_name} completed successfully")
                
            except Exception as e:
                logger.error(f"{agent_name} failed: {str(e)}")
                self._call_stats["failed_calls"] += 1
                
                results.append({
                    'agent': agent_name,
                    'result': f"{agent_name} is currently unavailable.",
                    'success': False
                })
        
        self._call_stats["total_calls"] += len(agent_calls)
        return results
    
    async def _call_agent(self, agent_name: str, query: str) -> str:
        """Call a specific ACP agent"""
        try:
            agent_info = self.acp_agents[agent_name]
            client = agent_info['client']
            
            print(f"Calling {agent_name} with 90s timeout...")
            start_time = time.time()
            
            result = await asyncio.wait_for(
                client.run_sync(agent=agent_name, input=query),
                timeout=90.0
            )
            
            elapsed = time.time() - start_time
            print(f"{agent_name} completed in {elapsed:.2f}s")
            
            response_content = result.output[0].parts[0].content
            print(f"{agent_name} response length: {len(response_content)} characters")
            
            return response_content
            
        except asyncio.TimeoutError:
            print(f"Agent {agent_name} timed out after 90 seconds")
            raise Exception(f"Agent {agent_name} timed out")
        except Exception as e:
            print(f"Agent {agent_name} error: {str(e)}")
            raise Exception(f"Agent {agent_name} error: {str(e)}")
    
    def _synthesize_results(self, results: List[Dict[str, str]], original_query: str) -> str:
        """Synthesize results efficiently without additional LLM calls"""
        successful_results = [r for r in results if r['success']]
        
        if not successful_results:
            return "All agents are currently unavailable. Please try again later."
        
        if len(successful_results) == 1:
         
            agent_name = successful_results[0]['agent']
            result = successful_results[0]['result']
            
            agent_labels = {
                'investment_agent': 'INVESTMENT ANALYSIS',
                'advisor_finder': 'ADVISOR RECOMMENDATIONS', 
                'market_researcher': 'MARKET RESEARCH'
            }
            
            label = agent_labels.get(agent_name, f'{agent_name.upper()}')
            return f"**{label}**\n\n{result}"
        
        
        response_parts = ["**COMPREHENSIVE FINANCIAL ANALYSIS**\n"]
        
        agent_labels = {
            'investment_agent': 'INVESTMENT STRATEGY',
            'advisor_finder': 'ADVISOR RECOMMENDATIONS',
            'market_researcher': 'MARKET INSIGHTS'
        }
        
        for result_info in successful_results:
            agent_name = result_info['agent']
            result = result_info['result']
            label = agent_labels.get(agent_name, f'{agent_name.upper()}')
            
            response_parts.append(f"\n**{label}:**\n{result}")
        
       
        agent_count = len(successful_results)
        response_parts.append(f"\n\n**✨ INTEGRATED GUIDANCE:** This analysis combines insights from {agent_count} specialized financial experts to provide comprehensive guidance tailored to your needs.")
        
        return "\n".join(response_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total = max(self._call_stats["total_calls"], 1)
        return {
            **self._call_stats,
            "success_rate": (self._call_stats["successful_calls"] / total) * 100,
            "available_agents": list(self.acp_agents.keys())
        }