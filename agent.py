from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful summarization assistant.",
    instruction=(
        "You are a helpful AI assistant. "
        "Summarize the user's input clearly and concisely in 3 to 5 lines. "
        "Keep the meaning accurate."
    ),
)