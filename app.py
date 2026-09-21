from langchain_core.messages import HumanMessage
from src.agents.agents import agent_web_Data_Collector, agent_risk_finder, agent_decision_maker

# Initialize 3 agents
investigator = agent_web_Data_Collector()
skeptic = agent_risk_finder()
judge = agent_decision_maker()

def run_diligence(startup_name: str):
    """
    This is your pipeline - pure LangChain new, no LangGraph
    """
    
    # --- Agent 1 ---
    print(f"\n--- Agent 1 Investigating: {startup_name} ---")
    result1 = investigator.invoke({
        "messages": [HumanMessage(content=f"Collect data for startup: {startup_name}")]
    })
    agent1_output = result1["messages"][-1].content
    print(agent1_output)

    # --- Agent 2 --- Takes Agent 1 output
    print(f"\n--- Agent 2 Finding Risks ---")
    input_for_agent2 = f"""
    Startup: {startup_name}
    
    Data from Agent 1:
    {agent1_output}
    
    Now find competitors, negative reviews, lawsuits, market risks for this startup.
    """
    result2 = skeptic.invoke({
        "messages": [HumanMessage(content=input_for_agent2)]
    })
    agent2_output = result2["messages"][-1].content
    print(agent2_output)

    # --- Agent 3 --- Takes Agent 1 + Agent 2 output
    print(f"\n--- Agent 3 Making Decision ---")
    input_for_agent3 = f"""
    Startup: {startup_name}
    
    Agent 1 Data (Good):
    {agent1_output}
    
    Agent 2 Data (Risks):
    {agent2_output}
    
    Write final INVESTMENT MEMO with Verdict: INVEST or PASS with 3 reasons.
    """
    result3 = judge.invoke({
        "messages": [HumanMessage(content=input_for_agent3)]
    })
    final_report = result3["messages"][-1].content

    return {
        "startup_name": startup_name,
        "agent1_output": agent1_output,
        "agent2_output": agent2_output,
        "final_report": final_report
    }


result = run_diligence("Perplexity AI")

print("\n========== FINAL MEMO ==========\n")
print(result["final_report"])