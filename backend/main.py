from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

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
        content = request.content
        metadata = content.get('metadata', {})
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.0-pro')
        
        # Prepare the prompt with enhanced context
        prompt = f"""
        Please provide a comprehensive summary of the following webpage content:
        
        Title: {content['title']}
        URL: {content['url']}
        
        Metadata:
        - Description: {metadata.get('description', 'Not available')}
        - Keywords: {metadata.get('keywords', 'Not available')}
        - Author: {metadata.get('author', 'Not available')}
        - Open Graph Title: {metadata.get('ogTitle', 'Not available')}
        - Open Graph Description: {metadata.get('ogDescription', 'Not available')}
        
        Main Content:
        {content['text'][:30000]}  # Limit content length
        
        Please provide a well-structured summary that captures:
        1. The main topic and purpose of the page
        2. Key points and important information
        3. Any notable metadata or context
        4. The overall structure and organization of the content
        """
        
        # Generate summary
        response = model.generate_content(prompt)
        return {"summary": response.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 