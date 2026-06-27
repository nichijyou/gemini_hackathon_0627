# Encore Agent: Minimum Runnable App Guide

This guide will help you run the Encore Agent end-to-end. 

## Requirements
The agent is currently deployed live on Google Cloud Run. It requires a `GEMINI_API_KEY` to function, which has already been set in the Cloud Run service environment variables.

## How to Test the Agent

You can test the agent directly from your terminal using `curl`. 

1. Ensure you have an image file of a concert poster. For this example, we will assume you have a file named `bruno_poster.jpg` in your current directory.
2. Run the following command:

```bash
curl -X POST "https://geminihackathonjun-848057658446.asia-northeast1.run.app/api/concierge" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@bruno_poster.jpg"
```

## What Happens Next?
When you send the POST request:
1. **Vision Extractor Pipeline**: The agent reads the poster image and uses the `gemini-1.5-flash` model to strictly extract JSON data about the concert (Artist, Tour Name, Dates, Cities, Venues, VIP Packages).
2. **Concierge Agent**: The extracted JSON is then passed to the orchestration agent. The agent uses tools to synthesize a travel itinerary, create an estimated budget, and suggest a community meetup for fans.

## Local Development
If you wish to run the app locally:
1. Install dependencies: `pip install -r requirements.txt`
2. Export your API Key: `export GEMINI_API_KEY="your-api-key"`
3. Start the server: `uvicorn main:app --reload`
4. Send the same curl request but to `http://127.0.0.1:8000/api/concierge`
