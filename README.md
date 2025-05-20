# FestivalRadar

FestivalRadar is a Python microservice that aggregates and filters live event data from multiple sources (currently Ticketmaster and Eventbrite). It provides an API and MCP server interface for discovering summer festivals, concerts, and cultural events in your city.

## Features

- Unified event search by city, date range, and (optional) genre
- Fetches from both Ticketmaster and Eventbrite
- MCP protocol support for AI integrations
- Prompt completions for chatbots and users

## Usage

Clone this repo and enter the folder:

    cd festivalradar

Create and activate a virtual environment (Python 3.11+):

    python3.11 -m venv .venv && source .venv/bin/activate

Install dependencies (requires uv):

    uv pip install -r requirements.txt

Add your API keys to a `.env` file:

    TICKETMASTER_API_KEY=your_ticketmaster_key
    EVENTBRITE_API_KEY=your_eventbrite_token

Start the server:

    uvicorn festivalradar_server:app --reload

Visit in your browser to see results:

    http://127.0.0.1:8000/test-events?city=Ottawa&start_date=2025-06-01&end_date=2025-06-30

## API Endpoints

- `/` – Server status
- `/test-events` – Query events with parameters: `city`, `genre` (optional), `start_date`, `end_date`

Example:

    /test-events?city=Ottawa&genre=music&start_date=2025-07-01&end_date=2025-07-31

## MCP & Prompt Integration

- Exposes MCP tools and prompts for AI chat clients
- Works with Claude Desktop or any MCP-compatible chatbot

## API Keys & Security

- **Do not commit your `.env` file to public repos**
- Add your API keys using your cloud provider’s environment variable settings if deploying

Example `.env` file:

    TICKETMASTER_API_KEY=your_ticketmaster_key
    EVENTBRITE_API_KEY=your_eventbrite_token

## Requirements

- Python 3.11+
- fastapi
- fastmcp
- httpx
- python-dotenv
- uvicorn

Sample `requirements.txt`:

    fastapi
    fastmcp
    httpx
    python-dotenv
    uvicorn

## License

MIT License

## Credits

- Ticketmaster Discovery API: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- Eventbrite API: https://www.eventbrite.com/platform/api
- FastAPI: https://fastapi.tiangolo.com/
- FastMCP: https://pypi.org/project/fastmcp/
