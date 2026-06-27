# Encore Agent

A Python-based backend project optimized for Google Cloud Run deployment.

## Project Structure

- `/pipeline`: Multimodal data pipeline for processing images via the Gemini API.
- `/agent`: Agent logic layer using the Vertex AI SDK.
- `main.py`: FastAPI entry point.

## Hackathon Deliverables Checklist
- [x] Initial project scaffolding
- [x] Implement multimodal data pipeline (`/pipeline`) for processing images via the Gemini API
- [x] Implement agent logic layer (`/agent`) using the Vertex AI SDK
- [x] Expose FastAPI endpoints for the agent and pipeline
- [x] Deploy to Google Cloud Run (URL: https://geminihackathonjun-848057658446.asia-northeast1.run.app/)
- [ ] Test End-to-End Multimodal flow
- [ ] Prepare presentation/demo

## Live Testing
```bash
# Test the Concierge endpoint (replace poster.jpg with an actual image)
curl -X POST "https://geminihackathonjun-848057658446.asia-northeast1.run.app/api/concierge" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@poster.jpg"
```

## Local Development
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
