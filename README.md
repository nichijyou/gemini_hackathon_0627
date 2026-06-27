# Encore Agent

A Python-based backend project optimized for Google Cloud Run deployment.

## Project Structure

- `/pipeline`: Multimodal data pipeline for processing images via the Gemini API.
- `/agent`: Agent logic layer using the Vertex AI SDK.
- `main.py`: FastAPI entry point.

## Hackathon Deliverables Checklist
- [x] Initial project scaffolding
- [ ] Implement multimodal data pipeline (`/pipeline`) for processing images via the Gemini API
- [ ] Implement agent logic layer (`/agent`) using the Vertex AI SDK
- [ ] Expose FastAPI endpoints for the agent and pipeline
- [ ] Deploy to Google Cloud Run
- [ ] Test End-to-End Multimodal flow
- [ ] Prepare presentation/demo

## Local Development
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
