import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

def search_flights(destination_city: str) -> dict:
    """Mock function to search for flights."""
    return {
        "flights": [
            {
                "airline": "Japan Airlines",
                "departure": "Tokyo Haneda (HND)",
                "arrival": destination_city,
                "price": "$850",
                "duration": "12h 30m"
            }
        ]
    }

def search_hotels(destination_city: str, dates: str) -> dict:
    """Mock function to search for hotels."""
    return {
        "hotels": [
            {
                "name": f"{destination_city} Grand Hotel",
                "dates": dates,
                "price_per_night": "$220",
                "rating": "4.8 stars",
                "package": "Standard Package with Breakfast"
            }
        ]
    }

tools_json = [
    {
        "functionDeclarations": [
            {
                "name": "search_flights",
                "description": "Search for flights departing from Tokyo Haneda to a given destination city.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "destination_city": {"type": "STRING", "description": "The destination city to fly to."}
                    },
                    "required": ["destination_city"]
                }
            },
            {
                "name": "search_hotels",
                "description": "Search for hotels in the destination city for the given dates.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "destination_city": {"type": "STRING", "description": "The destination city to stay in."},
                        "dates": {"type": "STRING", "description": "The dates of the stay (e.g., 'Oct 15-18')."}
                    },
                    "required": ["destination_city", "dates"]
                }
            }
        ]
    }
]

def generate_concert_itinerary(concert_data: dict) -> dict:
    """
    Takes extracted concert data, uses tools to gather travel details,
    and synthesizes a complete travel concierge plan.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable is not set."}

    prompt = f"""
    You are an elite travel concierge.
    A user wants to attend this concert tour. Here is the extracted data:
    {json.dumps(concert_data, indent=2)}

    Please look at the first available city and date from the data. 
    Use your tools to:
    1. Search for flights to that destination city.
    2. Search for hotels in that destination city for those dates.

    After retrieving the travel options, synthesize a complete, cohesive travel concierge plan.
    Your final plan MUST include:
    1. A detailed Itinerary (Concert, Flight, Hotel).
    2. An estimated Budget breakdown.
    3. A Community Meetup suggestion for other fans.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    payload = {
        "contents": messages,
        "tools": tools_json,
        "generationConfig": {"temperature": 0.2}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
        
        data = response.json()
        candidate = data.get("candidates", [])[0]
        parts = candidate.get("content", {}).get("parts", [])
        
        function_calls = [p["functionCall"] for p in parts if "functionCall" in p]
        
        if function_calls:
            # Append model's response to messages
            messages.append(candidate["content"])
            
            tool_parts = []
            for fc in function_calls:
                name = fc["name"]
                args = fc.get("args", {})
                if name == "search_flights":
                    res = search_flights(args.get("destination_city", "Unknown"))
                elif name == "search_hotels":
                    res = search_hotels(args.get("destination_city", "Unknown"), args.get("dates", "Unknown"))
                else:
                    res = {"error": "Unknown function"}
                    
                tool_parts.append({"functionResponse": {"name": name, "response": res}})
                
            messages.append({"role": "function", "parts": tool_parts})
            payload["contents"] = messages
            
            response2 = requests.post(url, headers=headers, json=payload)
            if response2.status_code != 200:
                return {"error": f"API Error 2: {response2.status_code} - {response2.text}"}
                
            data2 = response2.json()
            return {"plan": data2["candidates"][0]["content"]["parts"][0]["text"]}
        else:
            return {"plan": parts[0]["text"]}
            
    except Exception as e:
        logger.error(f"Error during orchestration: {e}")
        return {"error": str(e)}
