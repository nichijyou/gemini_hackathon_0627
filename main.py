from fastapi import FastAPI, UploadFile, File, HTTPException
import os

from pipeline.vision_extractor import extract_tour_info_from_image

app = FastAPI(title="Encore Agent API")

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
