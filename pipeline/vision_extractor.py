import json
import logging
from google import genai
from google.genai import types
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
    Extracts concert tour information from an image using Gemini 1.5 Pro.
    Expects GEMINI_API_KEY to be set in the environment.
    """
    try:
        # Initialize the GenAI client.
        client = genai.Client()
        
        # Prepare the image part
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        
        system_instruction = (
            "You are an expert data extractor. Your task is to analyze the provided concert tour poster "
            "and extract the required information into a strict JSON format. "
            "Ensure the extraction is accurate and comprehensive."
        )

        # Call the Gemini model
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=[image_part, "Extract the concert information from this poster."],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ConcertInfo,
                temperature=0.1
            )
        )
        
        if response.text:
            return json.loads(response.text)
        else:
            logger.error("No text returned from the model.")
            return {"error": "No text returned from the model."}
            
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        return {"error": str(e)}
