import os
import logging
from typing import Optional
from dotenv import load_dotenv

import langchain
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# Configuration and Logging Setup
load_dotenv()
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set USER_AGENT to resolve the warning
os.environ['USER_AGENT'] = 'MediCheck-Agent/1.0'

class EnhancedMedicalAgentSystem:
    def __init__(self, model: str = "gemini-2.0-flash", temperature: float = 0.2):
        # Centralized tool initialization
        self.tools = self._initialize_tools()
        
        self.llm = ChatGoogleGenerativeAI(
            model=model, 
            temperature=temperature, 
            convert_system_message_to_human=True
        )
        
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = self._create_agent()
        
        # New attribute to store the last answer
        self.last_answer: Optional[str] = None

    def _initialize_tools(self) -> list:
        """Centralized tool initialization method."""
        # Add any specific tools here if needed
        return []

    def _create_agent(self):
        """Create and configure the agent with a more modular approach."""
        custom_prompt = """
        You are a helpful medical information assistant. 
        Analyze the query, select appropriate tools, and synthesize accurate information.
        
        Query: {input}
        Context: {chat_history}

        Instruction: Provide evidence-based, clear information.
        """
        
        return initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=False,
            max_iterations=3,
            early_stopping_method="generate",
            prompt=PromptTemplate(
                input_variables=["input", "chat_history"], 
                template=custom_prompt
            )
        )

    def run(self, query: str) -> str:
        """
        Process the query and store the answer.
        
        Args:
            query (str): The medical query to process
        
        Returns:
            str: The processed answer
        """
        try:
            # Run the agent and capture the response
            answer = self.agent.run(query)
            
            # Store the answer as an instance attribute
            self.last_answer = answer
            
            return answer
        except Exception as e:
            error_msg = f"An error occurred: {e}. Please try rephrasing your query."
            self.last_answer = error_msg
            logger.error(f"Query processing error: {e}")
            return error_msg

def getValidation():
    # Create the medical agent
    agent = EnhancedMedicalAgentSystem()

    print("\nMedical Info Assistant - Type 'exit' to quit.")
    while True:
        try:
            # Get user input
            query = input("Your medical query: ").strip()
            
            # Check for exit conditions
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            # Run the query and print the response
            response = agent.run(query)
            print("\nAssistant:", response)
            
            # Demonstrate storing and accessing the last answer
            print("\nStored Answer:", agent.last_answer)
            return agent.last_answer
        
        except KeyboardInterrupt:
            print("\nOperation cancelled. Type 'exit' to quit.")