import httpx
from pathlib import Path
from phi.agent import Agent
from phi.tools.csv_tools import CsvTools
from phi.model.groq import Groq
url = "https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv"
response = httpx.get(url)

imdb_csv = Path(__file__).parent.joinpath("wip").joinpath("sample_imdb.csv")
imdb_csv.parent.mkdir(parents=True, exist_ok=True)
imdb_csv.write_bytes(response.content)

agent = Agent(
    tools=[CsvTools(csvs=[imdb_csv])],
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True,
    show_tool_calls=True,
    instructions=[
        "First always get the list of files",
    ],
)
agent.cli_app(stream=True)