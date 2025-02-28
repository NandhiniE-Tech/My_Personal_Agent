# No openai Key, NO worries get groq key and put in .env file

from phi.agent import Agent, RunResponse
from phi.model.groq import Groq

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)
agent.print_response("Share a 2 sentence horror story.")