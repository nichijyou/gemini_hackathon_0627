import json
import logging
import vertexai
from vertexai.generative_models import GenerativeModel, Part
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
    Extracts concert tour information from an image using Vertex AI.
    """
    try:
        # Let vertexai auto-detect project and location from Cloud Run metadata
        vertexai.init(location="asia-northeast1")
        
        system_instruction = (
            "You are an expert data extractor. Your task is to analyze the provided concert tour poster "
            "and extract the required information into a strict JSON format. "
            "Ensure the extraction is accurate and comprehensive."
        )

        model = GenerativeModel(
            "gemini-1.5-pro-001",
            system_instruction=[system_instruction]
        )

        image_part = Part.from_data(data=image_bytes, mime_type=mime_type)

        response = model.generate_content(
            [image_part, "Extract the concert information from this poster."],
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
            }
        )

        if response.text:
            return json.loads(response.text)
        else:
            logger.error("No text returned from the model.")
            return {"error": "No text returned from the model."}

    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        return {"error": str(e)}

