from fastapi import FastAPI, UploadFile, File, HTTPException
import os

from pipeline.vision_extractor import extract_tour_info_from_image
from agent.concierge_agent import generate_concert_itinerary

app = FastAPI(title="Encore Agent API")

# Ensure GEMINI_API_KEY is available (read from os.environ implicitly via our codebase)
# It is used by the pipeline/vision_extractor.py
api_key_check = os.environ.get("GEMINI_API_KEY")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Encore Agent API is running."}

@app.post("/extract")
async def extract_poster_info(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await file.read()
        result = extract_tour_info_from_image(contents, file.content_type)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/concierge")
async def generate_concierge_package(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await file.read()
        
        # 1. Vision Extraction
        concert_info = extract_tour_info_from_image(contents, file.content_type)
        if "error" in concert_info:
            raise HTTPException(status_code=500, detail=concert_info["error"])
            
        # 2. Agent Orchestration
        agent_result = generate_concert_itinerary(concert_info)
        if "error" in agent_result:
            raise HTTPException(status_code=500, detail=agent_result["error"])
            
        return {
            "concert_info": concert_info,
            "concierge_plan": agent_result["plan"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
