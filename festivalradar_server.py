from fastapi import FastAPI
from fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os

# Load API keys from .env
load_dotenv()
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")

app = FastAPI()
mcp = FastMCP("festivalradar", app=app, port=8000)

@app.get("/")
def root():
    return {"status": "FestivalRadar online!"}

@app.get("/mcp/healthz")
def healthz():
    return {"status": "ok"}

@mcp.tool()
def find_local_events(
    city: str,
    genre: str = None,
    start_date: str = None,
    end_date: str = None
):
    """
    Find local events in a given city, filtered by genre and date range.
    Aggregates from Ticketmaster and Eventbrite.
    """
    results = []

    # --- Ticketmaster ---
    tm_params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city,
        "countryCode": "CA",
        "size": 10,
    }
    if genre:
        tm_params["classificationName"] = genre
    if start_date:
        tm_params["startDateTime"] = f"{start_date}T00:00:00Z"
    if end_date:
        tm_params["endDateTime"] = f"{end_date}T23:59:59Z"

    try:
        tm_url = "https://app.ticketmaster.com/discovery/v2/events.json"
        response = httpx.get(tm_url, params=tm_params, timeout=10)
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        for event in events:
            # Defensive serialization: every field is always a string
            results.append({
                "source": "Ticketmaster",
                "name": str(event.get("name", "")),
                "date": str(event.get("dates", {}).get("start", {}).get("localDate", "")),
                "venue": str(event.get("_embedded", {}).get("venues", [{}])[0].get("name", "")),
                "url": str(event.get("url", "")),
                "genre": ", ".join([str(c.get("name", "")) for c in event.get("classifications", []) if "name" in c]),
                "description": str(event.get("info") or event.get("description") or ""),
            })
    except Exception as e:
        results.append({"source": "Ticketmaster", "error": str(e)})

    # --- Eventbrite ---
    if EVENTBRITE_API_KEY:
        eb_params = {
            "location.address": city,
            "expand": "venue",
            "page_size": 10,
        }
        if start_date:
            eb_params["start_date.range_start"] = f"{start_date}T00:00:00Z"
        if end_date:
            eb_params["start_date.range_end"] = f"{end_date}T23:59:59Z"
        if genre:
            eb_params["q"] = genre  # Simple query filter

        eb_url = "https://www.eventbriteapi.com/v3/events/search/"
        try:
            headers = {"Authorization": f"Bearer {EVENTBRITE_API_KEY}"}
            eb_response = httpx.get(eb_url, params=eb_params, headers=headers, timeout=10)
            eb_data = eb_response.json()
            eb_events = eb_data.get("events", [])
            for event in eb_events:
                # Defensive serialization: every field is always a string
                results.append({
                    "source": "Eventbrite",
                    "name": str(event.get("name", {}).get("text", "")),
                    "date": str(event.get("start", {}).get("local", "")),
                    "venue": str((event.get("venue", {}) or {}).get("name", "Unknown")),
                    "url": str(event.get("url", "")),
                    "genre": str(genre or ""),
                    "description": str((event.get("description", {}) or {}).get("text", "")),
                })
        except Exception as e:
            results.append({"source": "Eventbrite", "error": str(e)})

    return results

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

import os
PORT = int(os.environ.get("PORT", 8000))
mcp.run(transport="sse", host="0.0.0.0", port=PORT)
