from langchain.agents import create_agent
from langchain_ollama import ChatOllama # FIX: Use Ollama, not OpenAI
from src.tools.tools import web_Data_Collector, risk_finder
from dotenv import load_dotenv

load_dotenv()

llm = ChatOllama(model="qwen2.5:7b", temperature=0)

# 1st Agent: The Fan
def agent_web_Data_Collector():
    return create_agent(
        model=llm,
        tools=[web_Data_Collector],
        system_prompt="""You are Agent 1 - Data Collector.
        Your job: Given startup name, call web_Data_Collector and extract:
        - Website
        - Founders
        - Funding (how much & when)
        - Product
        - Recent News
        Return ONLY that structured data."""
    )

# 2nd Agent: The Hater
def agent_risk_finder():
    return create_agent(
        model=llm,
        tools=[risk_finder],
        system_prompt="""You are Agent 2 - Risk Finder.
        Your job: You get data from Agent 1. Now call risk_finder tool to find:
        - Competitors
        - Negative Reviews
        - Lawsuits
        - Market Risks
        Do NOT search for positive info. Only risks."""
    )

# 3rd Agent: The Judge
def agent_decision_maker():
    return create_agent(
        model=llm,
        tools=[], # No tools, only reasoning
        system_prompt="""You are Agent 3 - Decision Maker.
        Your job: You get output from Agent 1 and Agent 2.
        Write final investment memo with Verdict: INVEST or PASS with 3 reasons.
        """
    )