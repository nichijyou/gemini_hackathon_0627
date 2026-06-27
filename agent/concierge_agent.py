import os
import json
import logging
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

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

# Vertex AI Function Declarations
search_flights_func = FunctionDeclaration(
    name="search_flights",
    description="Search for flights departing from Tokyo Haneda to a given destination city.",
    parameters={
        "type": "object",
        "properties": {
            "destination_city": {"type": "string", "description": "The destination city to fly to."}
        },
        "required": ["destination_city"]
    }
)

search_hotels_func = FunctionDeclaration(
    name="search_hotels",
    description="Search for hotels in the destination city for the given dates.",
    parameters={
        "type": "object",
        "properties": {
            "destination_city": {"type": "string", "description": "The destination city to stay in."},
            "dates": {"type": "string", "description": "The dates of the stay (e.g., 'Oct 15-18')."}
        },
        "required": ["destination_city", "dates"]
    }
)

tools = Tool(function_declarations=[search_flights_func, search_hotels_func])

def generate_concert_itinerary(concert_data: dict) -> dict:
    """
    Takes extracted concert data, uses tools to gather travel details,
    and synthesizes a complete travel concierge plan.
    """
    try:
        # Initialize Vertex AI. When deployed on Cloud Run, it will automatically
        # use the service account credentials attached to the Cloud Run instance.
        vertexai.init()
    except Exception as e:
        logger.warning(f"Vertex AI initialization warning (expected if local without ADC): {e}")

    model = GenerativeModel("gemini-1.5-pro", tools=[tools])
    
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
    
    try:
        chat = model.start_chat()
        response = chat.send_message(prompt)
        
        # Orchestrator Loop for Tool execution
        while response.function_calls:
            tool_responses = []
            for function_call in response.function_calls:
                result = {}
                if function_call.name == "search_flights":
                    dest = function_call.args.get("destination_city", "Unknown")
                    result = search_flights(dest)
                elif function_call.name == "search_hotels":
                    dest = function_call.args.get("destination_city", "Unknown")
                    dates = function_call.args.get("dates", "Unknown dates")
                    result = search_hotels(dest, dates)
                else:
                    result = {"error": "Unknown function"}
                
                tool_responses.append(Part.from_function_response(
                    name=function_call.name,
                    response={"content": result}
                ))
            
            # Send the tool results back to the model
            response = chat.send_message(tool_responses)
            
        return {"plan": response.text}
        
    except Exception as e:
        logger.error(f"Error during orchestration: {e}")
        return {"error": str(e)}
