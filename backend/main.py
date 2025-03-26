from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

logger.info("Configuring Gemini API...")
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContentRequest(BaseModel):
    content: dict

@app.post("/summarize")
async def summarize_content(request: ContentRequest):
    try:
        logger.info("Received content for summarization")
        logger.info(f"Content title: {request.content.get('title', 'No title')}")
        logger.info(f"Content length: {len(request.content.get('text', ''))} characters")
        
        # Initialize Gemini model
        logger.info("Initializing Gemini model...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare the prompt
        prompt = f"""
        Please provide a concise summary of the following webpage content:
        
        Title: {request.content['title']}
        URL: {request.content['url']}
        Content: {request.content['text'][:30000]}  # Limit content length
        
        Please provide a well-structured summary that captures the main points.
        """
        
        # Generate summary
        logger.info("Generating summary...")
        response = model.generate_content(prompt)
        
        logger.info("Summary generated successfully")
        return {"summary": response.text}
    
    except Exception as e:
        logger.error(f"Error in summarize_content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 