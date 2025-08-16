#!/usr/bin/env python3

import asyncio
import json
import os
import re
from typing import Annotated, Dict, List

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from pydantic import BaseModel, Field
from serpapi import GoogleSearch

# --- Load environment variables ---
load_dotenv()

TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"
assert SERPAPI_KEY is not None, "Please set SERPAPI_KEY in your .env file"

# --- Auth Provider ---
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="puch-client",
                scopes=["*"],
                expires_at=None,
            )
        return None

# --- MCP Server Setup ---
mcp = FastMCP(
    "Event Planner AI",
    auth=SimpleBearerAuthProvider(TOKEN),
)

# --- Tool: about (required) ---
@mcp.tool
async def about() -> dict:
    return {"name": mcp.name, "description": "An AI assistant for planning social events in India."}

# --- Tool: validate (required by Puch) ---
@mcp.tool
async def validate() -> str:
    return MY_NUMBER

# --- Event Planner Data Models ---
class EventDetails(BaseModel):
    event_type: str | None = None
    location: str | None = None
    guest_count: int | None = None
    budget_range: str | None = None
    theme: str | None = None
    vendor_details: Dict[str, list] = Field(default_factory=dict)

# Load the event and location data from JSON files
try:
    with open("data/indian_events.json", "r", encoding="utf-8") as f:
        event_data = json.load(f)["events"]
except (FileNotFoundError, json.JSONDecodeError):
    event_data = [
        {"name": "Wedding", "keywords": ["wedding", "marriage"]},
        {"name": "Birthday Party", "keywords": ["birthday"]},
        {"name": "Festival Celebration", "keywords": ["festival", "diwali", "holi"]},
    ]

try:
    with open("data/indian_locations.json", "r", encoding="utf-8") as f:
        location_data = json.load(f)["locations"]
except (FileNotFoundError, json.JSONDecodeError):
    location_data = [
        {"name": "Tiruchirappalli, Tamil Nadu", "keywords": ["tiruchirappalli", "trichy"]},
        {"name": "Delhi, NCR", "keywords": ["delhi", "ncr"]},
        {"name": "Mumbai, Maharashtra", "keywords": ["mumbai"]},
    ]

# --- Tool: start_event_planning ---
@mcp.tool
async def start_event_planning() -> str:
    """
    Initializes the event planning process and greets the user.
    """
    return "👋 Namaste! I am your personal Event Planner AI. Let's plan your perfect event! First, what kind of event are you planning? (e.g., Wedding, Birthday, Festival Party)"

# --- Tool: ask_for_details ---
@mcp.tool
async def ask_for_details(
    event_details: Annotated[EventDetails, Field(description="The current state of the event details. Pass the last known state to this tool.")],
    user_input: Annotated[str, Field(description="The user's latest message to process.")]
) -> str:
    """
    Analyzes user input to update event details and prompts for missing information.
    """
    user_input = user_input.lower()

    # Find the event type using the JSON data
    if not event_details.event_type:
        for event in event_data:
            for keyword in event["keywords"]:
                if keyword in user_input:
                    event_details.event_type = event["name"]
                    break
            if event_details.event_type:
                break

    # Find the location using the JSON data
    if not event_details.location:
        for location in location_data:
            for keyword in location["keywords"]:
                if keyword in user_input:
                    event_details.location = location["name"]
                    break
            if event_details.location:
                break

    # --- Guest Count Parsing ---
    if not event_details.guest_count:
        match = re.search(r'(\d+)\s*guests?', user_input)
        if match:
            event_details.guest_count = int(match.group(1))

    # --- Budget Parsing ---
    if not event_details.budget_range:
        budget_amount = None
        match = re.search(r'(\d+)\s*k', user_input)
        if match:
            budget_amount = int(match.group(1)) * 1000
        
        if not budget_amount:
            match = re.search(r'(\d+)\s*lakh', user_input)
            if match:
                budget_amount = int(match.group(1)) * 100000

        if not budget_amount:
            match = re.search(r'(\d+)\s*crore', user_input)
            if match:
                budget_amount = int(match.group(1)) * 10000000
                
        if budget_amount:
            if budget_amount < 50000:
                event_details.budget_range = "low"
            elif budget_amount < 500000:
                event_details.budget_range = "moderate"
            else:
                event_details.budget_range = "high"
        
        if not event_details.budget_range:
            if "low budget" in user_input or "affordable" in user_input:
                event_details.budget_range = "low"
            elif "moderate" in user_input:
                event_details.budget_range = "moderate"
            elif "high budget" in user_input or "lavish" in user_input:
                event_details.budget_range = "high"

    # --- Q&A Logic: Prompt for missing details ---
    if not event_details.event_type:
        return "What kind of event are you planning? (e.g., Wedding, Birthday, or a Festival like Diwali)"
    
    if not event_details.location:
        return f"Got it, a {event_details.event_type}. Where will this event be held?"
        
    if not event_details.guest_count:
        return "And about how many guests will be attending? Please provide a number."

    if not event_details.budget_range:
        return "To help me plan, what's your budget like? (e.g., low, moderate, high, or a specific amount like 50k or 1 lakh)"
    
    # If all details are complete, return a confirmation message
    return "Thank you! I have all the details. I will now create a personalized plan for you."

# --- Tool: plan_event ---
@mcp.tool
async def plan_event(
    event_details: Annotated[EventDetails, Field(description="The final, complete event details to create a plan.")]
) -> dict:
    """
    Generates a comprehensive event plan and a vendor checklist based on event details.
    """
    event_type = event_details.event_type
    
    plan = {
        "event_type": event_type,
        "location": event_details.location,
        "guest_count": event_details.guest_count,
        "budget_range": event_details.budget_range,
        "plan_items": []
    }

    if "wedding" in event_type.lower():
        plan["plan_items"] = [
            {"category": "Venue & Catering", "description": "Booking a suitable venue and caterer for the ceremony and reception."},
            {"category": "Photography & Videography", "description": "Hiring a photographer and videographer to capture candid and traditional moments."},
            {"category": "Decorations & Florist", "description": "Arranging for mandap decor, floral arrangements, and lighting."},
            {"category": "Bridal Services", "description": "Hiring a professional makeup and mehendi artist for the bride."},
            {"category": "Entertainment", "description": "Booking a DJ or live band for music and a choreographer for sangeet."},
            {"category": "Ceremony Officiant", "description": "Finding a priest or pandit to conduct the rituals."},
            {"category": "Logistics", "description": "Arranging transportation for the baraat and guests."}
        ]
    elif "birthday" in event_type.lower():
        plan["plan_items"] = [
            {"category": "Venue & Decor", "description": "Booking a party hall and setting up theme-based decorations."},
            {"category": "Catering", "description": "Arranging food, drinks, and a birthday cake."},
            {"category": "Entertainment", "description": "Hiring a DJ, magician, or other performers."},
            {"category": "Photography", "description": "Hiring a photographer to capture the celebration."}
        ]
    else:
        plan["plan_items"] = [
            {"category": "General", "description": "This is a basic plan as the event type is not recognized."},
            {"category": "Venue", "description": "Selecting a suitable location."},
            {"category": "Food", "description": "Planning for food and beverages."},
            {"category": "Services", "description": "Arranging for essential services like music and photography."}
        ]
    
    return plan

# --- Tool: find_vendors ---
@mcp.tool
async def find_vendors(
    category: Annotated[str, Field(description="The vendor category to search for (e.g., 'Wedding Photographer').")],
    location: Annotated[str, Field(description="The location for the search (e.g., 'Tiruchirappalli, Tamil Nadu').")],
    budget: Annotated[str, Field(description="The budget range for vendors ('low', 'moderate', 'high').")] = 'moderate'
) -> List[dict]:
    """
    Searches for and recommends vendors using a search API and budget constraints.
    """
    budget_terms = {
        "low": "affordable",
        "moderate": "best",
        "high": "luxury"
    }
    
    query = f"{budget_terms.get(budget, 'best')} {category} in {location} reviews"
    
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "hl": "en",
            "gl": "in"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        vendor_list = []
        for item in results.get("local_results", []) + results.get("organic_results", []):
            vendor_data = {
                "name": item.get("title", "N/A"),
                "link": item.get("link", "N/A"),
                "rating": item.get("rating", "N/A"),
                "reviews": item.get("reviews", "N/A"),
                "snippet": item.get("snippet", "N/A")
            }
            vendor_list.append(vendor_data)
            if len(vendor_list) >= 5:
                break

        return vendor_list

    except Exception as e:
        raise McpError(ErrorData(code="INVALID_PARAMS", message=f"Failed to find vendors: {e}"))

# --- Run MCP Server ---
async def main():
    print("🚀 Starting Event Planner MCP server on http://0.0.0.0:8086")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

# In Jupyter, use await instead of asyncio.run()
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())