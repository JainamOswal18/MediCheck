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

class ChatRequest(BaseModel):
    message: str

# Initialize conversation history
conversation_history = []

# Initialize Gemini model for chat
from langchain_google_genai import ChatGoogleGenerativeAI
gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
    google_api_key=API_KEY,
    convert_system_message_to_human=True
)

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

        # Store request and validation response in conversation history
        conversation_history.append({"role": "user", "message": f"Validation request: {formatted_text}"})
        conversation_history.append({"role": "validation", "message": f"Validation result: {json.dumps(validation_result)}"})
        
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

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_input = request.message
        if not user_input:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        logger.info(f"Received chat query: {user_input}")

        # Append user message to history
        conversation_history.append({"role": "user", "message": user_input})

        # Limit history size (e.g., keep only last 15 exchanges)
        conversation_history[:] = conversation_history[-15:]

        # Format history as direct conversation
        context = "\n".join([f"{msg['role']}: {msg['message']}" for msg in conversation_history])

        # Generate response using LangChain's invoke method
        response = gemini_model.invoke(f"{context}\nBot:(Instruction: Keep it short and to the point)")
        bot_reply = response.content if response else "I'm sorry, I couldn't process your request."

        # Ensure bot responds naturally without third-person narration
        if "Response:" in bot_reply:
            bot_reply = bot_reply.split("Response:")[-1].strip()

        # Append bot response to history
        conversation_history.append({"role": "bot", "message": bot_reply})

        return {"response": bot_reply}

    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
# 
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 