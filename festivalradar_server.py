from fastapi import FastAPI
from fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os

# Load API keys from .env
load_dotenv()
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")

# Create FastAPI app and MCP wrapper
app = FastAPI()
mcp = FastMCP("festivalradar", app=app, port=8000)

@app.get("/")
def root():
    return {"status": "FestivalRadar online!"}

@mcp.tool()
def find_local_events(
    city: str,
    genre: str = None,
    start_date: str = None,
    end_date: str = None
):
    """
    Find local events in a given city, filtered by genre and date range, from Ticketmaster and Eventbrite.
    """
    results = []

    # --- Ticketmaster ---
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city,
        "countryCode": "CA",
        "size": 10,
    }
    if genre:
        params["classificationName"] = genre
    if start_date:
        params["startDateTime"] = f"{start_date}T00:00:00Z"
    if end_date:
        params["endDateTime"] = f"{end_date}T23:59:59Z"

    url_tm = "https://app.ticketmaster.com/discovery/v2/events.json"
    try:
        response_tm = httpx.get(url_tm, params=params, timeout=10)
        data_tm = response_tm.json()
        events_tm = data_tm.get("_embedded", {}).get("events", [])
        for event in events_tm:
            results.append({
                "source": "Ticketmaster",
                "name": event.get("name"),
                "date": event.get("dates", {}).get("start", {}).get("localDate"),
                "venue": event.get("_embedded", {}).get("venues", [{}])[0].get("name"),
                "url": event.get("url"),
                "genre": ", ".join([c["name"] for c in event.get("classifications", []) if "name" in c]),
            })
    except Exception as e:
        results.append({"source": "Ticketmaster", "error": str(e)})

    # --- Eventbrite ---
    headers_eb = {"Authorization": f"Bearer {EVENTBRITE_API_KEY}"}
    params_eb = {
        "location.address": city,
        "expand": "venue",
        "sort_by": "date",
        "page_size": 10,
    }
    if genre:
        params_eb["q"] = genre
    if start_date:
        params_eb["start_date.range_start"] = f"{start_date}T00:00:00Z"
    if end_date:
        params_eb["start_date.range_end"] = f"{end_date}T23:59:59Z"

    url_eb = "https://www.eventbriteapi.com/v3/events/search/"
    try:
        response_eb = httpx.get(url_eb, params=params_eb, headers=headers_eb, timeout=10)
        data_eb = response_eb.json()
        events_eb = data_eb.get("events", [])
        for event in events_eb:
            results.append({
                "source": "Eventbrite",
                "name": event.get("name", {}).get("text"),
                "date": event.get("start", {}).get("local"),
                "venue": event.get("venue", {}).get("name"),
                "url": event.get("url"),
                "genre": event.get("category_id"),  # Eventbrite genre/category is different
            })
    except Exception as e:
        results.append({"source": "Eventbrite", "error": str(e)})

    return results

@mcp.prompt()
def generate_event_search_prompt(
    city: str = None,
    genre: str = None,
    start_date: str = None,
    end_date: str = None
) -> str:
    """
    Generate a natural language prompt for the user or Claude to discover local events.
    """
    city_part = f"in {city}" if city else ""
    genre_part = f"{genre} " if genre else ""
    date_part = ""
    if start_date and end_date:
        date_part = f"between {start_date} and {end_date}"
    elif start_date:
        date_part = f"after {start_date}"
    elif end_date:
        date_part = f"before {end_date}"

    prompt = f"Find {genre_part}events {city_part} {date_part}. List top results with date, venue, and ticket link."
    return prompt.strip()

@app.get("/test-events")
def test_events(
    city: str,
    genre: str = None,
    start_date: str = None,
    end_date: str = None
):
    return find_local_events(
        city=city,
        genre=genre,
        start_date=start_date,
        end_date=end_date
    )

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
