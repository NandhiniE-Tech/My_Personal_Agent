import csv
import json
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from phi.agent import Agent
from phi.model.groq import Groq
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.playground import Playground, serve_playground_app
from phi.tools.csv_tools import CsvTools
CSV_agent_Listener = Agent(
    name="csv Agent Listener",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[CsvTools()],
    instructions=["Always include user input and save changes in csv files"],
    storage=SqlAgentStorage(table_name="web_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

CSV_agent_Reviewer = Agent(
    name="csv Agent reviewer",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[CsvTools()],
    instructions=["changes required save in csv files"],
    storage=SqlAgentStorage(table_name="web_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

app = Playground(agents=[CSV_agent_Listener, CSV_agent_Reviewer]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)