from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import logging
import re

from neo4j_knowledge_tool import FinancialKnowledgeGraph

logger = logging.getLogger("knowledge_investment_tool")

class InvestmentQueryInput(BaseModel):
    """Input for knowledge-enhanced investment advice"""
    query: str = Field(..., description="Investment query with details like amount, risk tolerance, goals")

class FinancialKnowledgeTool(BaseTool):
    """Investment tool enhanced with Neo4j knowledge graph and document analysis"""
    name: str = "financial_knowledge_advisor"
    description: str = "Provide investment advice using Neo4j knowledge graph and uploaded documents"
    args_schema: Type[BaseModel] = InvestmentQueryInput
    
    def _run(self, query: str) -> str:
        """Execute knowledge-enhanced investment analysis"""
        try:
            print(f"=== FinancialKnowledgeTool Debug ===")
            print(f"Received query: '{query}' (type: {type(query)})")
            
            if not query or not isinstance(query, str):
                return "Invalid query received by financial knowledge tool"
            
            # Create knowledge graph instance in _run method
            try:
                knowledge_graph = FinancialKnowledgeGraph(
                    neo4j_password="Vrushank@56789",  
                    uploads_directory="./uploads"
                )
                print("Knowledge graph created successfully")
                
                has_uploaded = knowledge_graph.has_uploaded_data
                print(f"Has uploaded data: {has_uploaded}")
                
                if has_uploaded:
                    return self._knowledge_enhanced_analysis(query, knowledge_graph)
                else:
                    return self._graph_based_analysis(query, knowledge_graph)
                    
            except Exception as kg_error:
                print(f"Knowledge graph creation failed: {kg_error}")
                return self._fallback_analysis(query)
            
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return f"Tool execution failed: {str(e)}"
    
    def _knowledge_enhanced_analysis(self, query: str, knowledge_graph) -> str:
        """Use both uploaded documents and knowledge graph"""
        try:
            knowledge_results = knowledge_graph.search_knowledge(query)
            
            response_parts = ["**KNOWLEDGE-ENHANCED FINANCIAL ANALYSIS**\n"]
            
            if knowledge_results.get("uploaded_content"):
                response_parts.append("**ANALYSIS FROM YOUR UPLOADED DOCUMENTS:**")
                for i, content in enumerate(knowledge_results["uploaded_content"][:3], 1):
                    source = content.get("source", "Unknown document")
                    text = content.get("text", "")
                    display_text = text[:300] + "..." if len(text) > 300 else text
                    
                    response_parts.append(f"{i}. **From {source}:**")
                    response_parts.append(f"   {display_text}\n")
            
            risk_level = self._extract_risk_level(query)
            investment_amount = self._extract_amount(query)
            time_horizon = self._extract_time_horizon(query)
            
            response_parts.append("**PERSONALIZED RECOMMENDATIONS:**")
            response_parts.append(f"- Investment Amount: ${investment_amount:,.0f}")
            response_parts.append(f"- Risk Profile: {risk_level}")
            response_parts.append(f"- Time Horizon: {time_horizon}")
            response_parts.append("- Analysis incorporates your uploaded documents")
            
            response_parts.append("\n**POWERED BY:** Neo4j Knowledge Graph + Your Uploaded Documents")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            print(f"Error in knowledge-enhanced analysis: {e}")
            return self._fallback_analysis(query)
    
    def _graph_based_analysis(self, query: str, knowledge_graph) -> str:
        """Use knowledge graph without uploaded documents"""
        try:
            risk_level = self._extract_risk_level(query)
            investment_amount = self._extract_amount(query)
            time_horizon = self._extract_time_horizon(query)
            
            response_parts = ["**KNOWLEDGE GRAPH INVESTMENT ANALYSIS**\n"]
            response_parts.append("**RECOMMENDED STRATEGY:**")
            response_parts.append(f"- {risk_level} Risk Investment Strategy")
            response_parts.append(f"- Suitable for {time_horizon} investing")
            response_parts.append(f"- Amount: ${investment_amount:,.0f}")
            response_parts.append("\n**TIP:** Upload financial documents for personalized analysis!")
            response_parts.append("\n**POWERED BY:** Neo4j Knowledge Graph")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            print(f"Error in graph-based analysis: {e}")
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> str:
        """Fallback analysis when knowledge graph is unavailable"""
        risk_level = self._extract_risk_level(query)
        investment_amount = self._extract_amount(query)
        time_horizon = self._extract_time_horizon(query)
        
        response_parts = ["**STANDARD INVESTMENT ANALYSIS**\n"]
        response_parts.append("(Knowledge graph unavailable)")
        response_parts.append(f"\n**YOUR PROFILE:**")
        response_parts.append(f"- Investment Amount: ${investment_amount:,.0f}")
        response_parts.append(f"- Risk Tolerance: {risk_level}")
        response_parts.append(f"- Time Horizon: {time_horizon}")
        
        if risk_level == "Low":
            response_parts.append("\n**CONSERVATIVE STRATEGY:** 30% Stocks, 70% Bonds")
        elif risk_level == "High":
            response_parts.append("\n**AGGRESSIVE STRATEGY:** 90% Stocks, 10% Bonds")
        else:
            response_parts.append("\n**BALANCED STRATEGY:** 60% Stocks, 40% Bonds")
        
        return "\n".join(response_parts)
    
    def _extract_risk_level(self, query: str) -> str:
        """Extract risk level from query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['conservative', 'low risk', 'safe', 'stable']):
            return "Low"
        elif any(word in query_lower for word in ['aggressive', 'high risk', 'growth', 'risky']):
            return "High"
        elif any(word in query_lower for word in ['moderate', 'balanced', 'medium']):
            return "Moderate"
        return "Moderate"
    
    def _extract_amount(self, query: str) -> float:
        """Extract investment amount from query"""
        patterns = [
            r'\$\s*([\d,]+)(?:k|K|thousand)?',
            r'([\d,]+)\s*(?:dollars|usd|\$)',
            r'([\d,]+)(?:k|K|thousand)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    if 'k' in query.lower() or 'thousand' in query.lower():
                        amount *= 1000
                    if amount > 0:
                        return amount
                except:
                    continue
        return 50000
    
    def _extract_time_horizon(self, query: str) -> str:
        """Extract time horizon from query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['short', 'near term', '1 year', '2 year']):
            return "short-term"
        elif any(word in query_lower for word in ['medium', '3 year', '5 year', 'mid term']):
            return "medium-term"
        elif any(word in query_lower for word in ['long', 'retirement', '10 year', '20 year']):
            return "long-term"
        return "long-term"
    
def get_financial_knowledge_tool():
    """Factory function to create financial knowledge tool"""
    return FinancialKnowledgeTool()