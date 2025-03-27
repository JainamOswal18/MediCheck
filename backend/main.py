from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

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
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class ContentRequest(BaseModel):
    content: dict

@app.post("/summarize")
async def summarize_content(request: ContentRequest):
    try:
        content = request.content
        metadata = content.get('metadata', {})
        
        # # Create timestamp for logging
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # # Log to console
        # print("\n" + "="*50)
        # print(f"New request received at {timestamp}")
        # print(f"URL: {content.get('url', 'No URL')}")
        # print(f"Title: {content.get('title', 'No title')}")
        # print(f"Content length: {len(content.get('text', ''))} characters")
        # print("Metadata:", json.dumps(metadata, indent=2))
        # print("="*50 + "\n")
        
        # # Create logs directory if it doesn't exist
        # os.makedirs('logs', exist_ok=True)
        
        # # Save metadata and text content to JSON file
        # log_data = {
        #     "timestamp": timestamp,
        #     "url": content.get('url'),
        #     "title": content.get('title'),
        #     "content_length": len(content.get('text', '')),
        #     "metadata": metadata,
        #     "text_preview": content.get('text', '')[:500] + '...' if len(content.get('text', '')) > 500 else content.get('text', '')
        # }
        
        # # Save to JSON file
        # log_filename = f"logs/scraped_data_{timestamp.replace(' ', '_').replace(':', '-')}.json"
        # with open(log_filename, 'w', encoding='utf-8') as f:
        #     json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare the prompt with enhanced context
        prompt = f"""
        Please provide a short summary of the following webpage content:
        
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
        
        # Log the summary
        print("\nGenerated Summary:")
        print("-"*50)
        print(response.text)
        print("-"*50 + "\n")
        
        return {"summary": response.text}
    
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\nStarting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 