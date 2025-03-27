from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
from agent1 import get_medical_validation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure API key
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class ContentRequest(BaseModel):
    content: dict

@app.post("/summarize")
async def validate_content(request: ContentRequest):
    try:
        logger.info("Received content validation request")
        content = request.content
        metadata = content.get('metadata', {})
        
        # Prepare the text for validation
        title = content.get('title', 'No title')
        url = content.get('url', 'No URL')
        text = content.get('text', '')
        
        logger.info(f"Content info - Title: {title}, URL: {url}, Text length: {len(text)}")
        
        # Format the text to include metadata context
        formatted_text = f"""
        Title: {title}
        URL: {url}
        
        Metadata:
        - Description: {metadata.get('description', 'Not available')}
        - Keywords: {metadata.get('keywords', 'Not available')}
        - Author: {metadata.get('author', 'Not available')}
        - Open Graph Title: {metadata.get('ogTitle', 'Not available')}
        - Open Graph Description: {metadata.get('ogDescription', 'Not available')}
        
        Main Content:
        {text[:30000]}  # Limit content length
        """
        
        # Log the request
        logger.info(f"Processing Content for Validation - Source: {url}, Length: {len(formatted_text)}")
        
        # Get validation results using the medical validation function
        logger.info("Calling get_medical_validation function")
        validation_result = get_medical_validation(formatted_text)
        
        # Check the result structure
        logger.info(f"Validation result keys: {validation_result.keys() if validation_result else 'None'}")
        if 'validation_results' in validation_result:
            logger.info(f"Number of validation results: {len(validation_result['validation_results'])}")
        
        # Log the results
        logger.info("Validation completed successfully")
        logger.info("Returning validation results to client")
        
        # Return the validation results
        return validation_result
    
    except Exception as e:
        logger.error(f"Error during content validation: {str(e)}")
        # Return a structured error response
        error_response = {
            "summary": f"Error: {str(e)}",
            "validation_results": []
        }
        raise HTTPException(status_code=500, detail=json.dumps(error_response))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 