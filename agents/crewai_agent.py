import warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, LLM
from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server

from vector_database import get_financial_knowledge_tool

from mcp_advisor_tool import get_mcp_advisor_tool


server = Server()

llm = LLM( model ="anthropic/claude-sonnet-4-20250514" ,
          max_tokens=1024,
          temperature=0.2,
          api_key=os.getenv("ANTHROPIC_API_KEY"))

@server.agent()
async def investment_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    "Investment Agent that provides personalized investment strategies and advisor matching based on user profiles and market conditions."

    try:
        print("Investment agent starting...")
        
        # Import and create the tool
        from vector_database import get_financial_knowledge_tool
        smart_tool = get_financial_knowledge_tool()
        print("Tool created successfully")
        tools_list = [smart_tool]
    except Exception as e:
        print(f"An error occurred: {e}")
        tools_list = [] 
            

    Investment_Guide = Agent(
        role="Senior Investment Advisor and Portfolio Strategist",
        goal="Provide comprehensive investment strategies and portfolio management advice to clients, focusing on long-term growth and risk mitigation.",
        backstory="You are a seasoned investment professional with over 15 years of experience in wealth management and portfolio strategy. You hold a CFA (Chartered Financial Analyst) designation and an MBA in Finance from a top-tier business school."
                "Throughout your career, you've successfully managed portfolios worth over $500 million across diverse market conditions, including the 2008 financial crisis and the COVID-19 market volatility. Your expertise spans across asset classes including equities, fixed income, alternatives, and international markets."
                "You have a proven track record of creating personalized investment strategies that align with clients' financial goals, risk tolerance, and time horizons. Your approach combines fundamental analysis, technical indicators, and macroeconomic trends to build resilient portfolios."
                "You are known for your ability to explain complex financial concepts in simple terms, helping clients make informed decisions about their financial future. Your conservative yet growth-oriented philosophy has helped hundreds of clients achieve their retirement, education, and wealth-building goals while protecting their downside risk during market downturns.",
        tools=tools_list,
        llm=llm,
        allow_delegation=False,
        verbose=True
    )

    task1 = Task(
    description= input[0].parts[0].content,

        expected_output="""
        A comprehensive investment analysis report containing:
        
        **INVESTMENT RECOMMENDATION SUMMARY**
        - Overall recommendation: [BUY/HOLD/SELL/WAIT]
        - Confidence level: [High/Medium/Low]
        - Investment timeline: [Short-term/Medium-term/Long-term]
        
        **PORTFOLIO ALLOCATION**
        - Recommended asset allocation percentages
        - Specific investment vehicles (ETFs, stocks, bonds)
        - Dollar amounts for each allocation
        
        **RISK ANALYSIS**
        - Risk level assessment: [Conservative/Moderate/Aggressive]
        - Key risks identified
        - Risk mitigation strategies
        
        **ACTION ITEMS**
        - Immediate next steps
        - Monitoring recommendations
        - Rebalancing schedule
        
        **RATIONALE**
        - Detailed explanation of recommendations
        - Market factors considered
        - Alignment with user goals
        
        Format: Structured JSON + human-readable summary for UI display
        """,
        agent=Investment_Guide
    )

    crew = Crew(agents = [Investment_Guide], tasks = [task1], llm=llm)
    task_output = await crew.kickoff_async()
    yield Message(parts=[MessagePart(content=str(task_output))])

@server.agent()
async def advisor_finder(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    "Investment Advisor Finder that identifies and recommends the most suitable investment advisors based on clients' specific needs and preferences."

    mcp_tool = get_mcp_advisor_tool()

    Advisor_Finder = Agent(
        role="Investment Advisor Finder",
        goal="Identify and recommend the most suitable investment advisors based on clients' specific needs and preferences.",
        backstory="You are an expert in matching clients with the right financial advisors. You have access to a curated database of pre-verified advisors in select cities (Charlotte NC, New York NY, Miami FL). "
        "When your database has advisors for the requested location, prioritize those verified advisors and present them first. "
        "When your database doesn't have advisors for a location, or when you want to provide additional options, use your extensive knowledge to suggest additional qualified advisors based on the user's specific needs and location. "
        "You can combine both approaches: show verified advisors from your database AND supplement with additional advisor recommendations using your expertise about the financial advisory industry. "
        "This gives users both specific, actionable contacts from your verified database and broader options based on your knowledge of advisor types, credentials, and best practices in financial planning.",
        tools=[mcp_tool],
        llm=llm,
        allow_delegation=False,
        verbose=True
    )

    

    task2 = Task(
        description= input[0].parts[0].content,

        expected_output="""
        A comprehensive advisor matching report containing:
        
        **TOP ADVISOR MATCHES** (Ranked 1-5)
        
        For each advisor:
        **ADVISOR PROFILE**
        - Name and firm
        - Credentials (CFP, CFA, ChFC, etc.)
        - Years of experience
        - Specializations
        - Location (address/remote options)
        
        **MATCH ANALYSIS**
        - Match score: [0-100%]
        - Why this advisor fits your needs
        - Potential concerns or limitations
        
        **FINANCIAL DETAILS**
        - Fee structure and rates
        - Minimum investment requirements
        - Services included
        - Additional costs
        
        **CREDENTIALS & VERIFICATION**
        - License status
        - Regulatory record (clean/issues)
        - Professional associations
        - Client testimonials/ratings
        
        **NEXT STEPS**
        - Contact information
        - Recommended questions to ask
        - Suggested meeting agenda
        - Red flags to watch for
        
        **COMPARISON MATRIX**
        Side-by-side comparison of top 3 advisors
        
        Format: Structured data for UI cards + detailed profiles for drill-down
        """,
        agent=Advisor_Finder
    )

    crew = Crew(agents = [Advisor_Finder], tasks = [task2], llm=llm)
    task_output = await crew.kickoff_async()
    yield Message(parts=[MessagePart(content=str(task_output))])
    
if __name__ == "__main__":
    print("Starting ACP server...")
    server.run()

