from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
import logging
from agent1 import get_medical_validation
from google.generativeai import GenerativeModel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Gemini 2.0 Flash model
gemini_model = GenerativeModel("gemini-2.0-flash")

# Store conversation history including chat and validation responses
conversation_history = []

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

@app.post("/summarize")
async def validate_content(request: ContentRequest):
    try:
        logger.info("Received content validation request")
        content = request.content
        metadata = content.get("metadata", {})

        title = content.get("title", "No title")
        url = content.get("url", "No URL")
        text = content.get("text", "")

        logger.info(f"Content info - Title: {title}, URL: {url}, Text length: {len(text)}")

        formatted_text = f"""
        Title: {title}
        URL: {url}

        Metadata:
        - Description: {metadata.get("description", "Not available")}
        - Keywords: {metadata.get("keywords", "Not available")}
        - Author: {metadata.get("author", "Not available")}
        - Open Graph Title: {metadata.get("ogTitle", "Not available")}
        - Open Graph Description: {metadata.get("ogDescription", "Not available")}

        Main Content:
        {text[:30000]}
        """

        logger.info(f"Processing Content for Validation - Source: {url}, Length: {len(formatted_text)}")

        logger.info("Calling get_medical_validation function")
        validation_result = get_medical_validation(formatted_text)

        logger.info(f"Validation result keys: {validation_result.keys() if validation_result else 'None'}")
        if "validation_results" in validation_result:
            logger.info(f"Number of validation results: {len(validation_result['validation_results'])}")

        logger.info("Validation completed successfully")
        logger.info("Returning validation results to client")

        # Store request and validation response in conversation history
        conversation_history.append({"role": "user", "message": f"Validation request: {formatted_text}"})
        conversation_history.append({"role": "validation", "message": f"Validation result: {json.dumps(validation_result)}"})

        return validation_result

    except Exception as e:
        logger.error(f"Error during content validation: {str(e)}")
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

        # Generate response in direct speech
        response = gemini_model.generate_content(f"{context}\nBot:(Instruction: (Keep it short and to the point))")
        bot_reply = response.text if response else "I'm sorry, I couldn't process your request."

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

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)