import os
import json
import base64
import logging
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ConcertInfo(BaseModel):
    Artist_Name: str | None = Field(default=None, description="Name of the artist or band")
    Tour_Name: str | None = Field(default=None, description="Name of the tour")
    Dates: list[str] | None = Field(default=None, description="List of tour dates")
    Cities: list[str] | None = Field(default=None, description="List of cities in the tour")
    Venues: list[str] | None = Field(default=None, description="List of venues for the tour")
    VIP_Packages: list[str] | None = Field(default=None, description="Details of any VIP packages offered")

def extract_tour_info_from_image(image_bytes: bytes, mime_type: str) -> dict:
    """
    Extracts concert tour information from an image using a direct REST call to Gemini 1.5 Pro.
    Expects GEMINI_API_KEY to be set in the environment.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable is not set."}

    try:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        system_instruction = (
            "You are an expert data extractor. Your task is to analyze the provided concert tour poster "
            "and extract the required information into a strict JSON format. "
            "Ensure the extraction is accurate and comprehensive."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "parts": [
                        {"text": "Extract the concert information from this poster."},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "response_schema": ConcertInfo.model_json_schema()
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return {"error": f"API Error: {response.status_code} - {response.text}"}
            
        data = response.json()
        
        # Extract the text response from the API result
        try:
            result_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(result_text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse response format: {data}")
            return {"error": f"Failed to parse response format. Exception: {e}"}
            
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        return {"error": str(e)}

