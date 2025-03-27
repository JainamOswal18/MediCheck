import os
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Pydantic Model for Structured Output
class ValidationResult(BaseModel):
    incorrect_text: str = Field(description="The original incorrect statement")
    correct_text: str = Field(description="The corrected and accurate statement")

class MedicalValidation(BaseModel):
    summary: str = Field(description="A concise summary of the key information")
    validation_results: List[ValidationResult] = Field(
        description="List of identified incorrect statements with their corrections"
    )

class MedicalFactChecker:
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.2):
        """
        Initialize the Medical Fact Checker with a Google Generative AI model
        
        Args:
            model_name (str): Name of the Google AI model to use
            temperature (float): Creativity/randomness of the model response
        """
        # Initialize the language model
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=temperature,
            convert_system_message_to_human=True
        )
        
        # Create an output parser
        self.output_parser = PydanticOutputParser(pydantic_object=MedicalValidation)
        
        # Create a prompt template
        self.prompt = PromptTemplate(
            template="""You are an expert medical fact-checker and information synthesizer.

For the given text, perform the following tasks:
1. Provide a concise summary of the key information
2. Identify and correct any medical or scientific inaccuracies
3. Ensure corrections are evidence-based and scientifically accurate

Text: {query}

{format_instructions}""",
            input_variables=["query"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

    def validate(self, query: str) -> MedicalValidation:
        """
        Validate medical information and return structured JSON output
        
        Args:
            query (str): The text to be fact-checked
        
        Returns:
            MedicalValidation: Structured validation results
        """
        try:
            # Combine prompt and language model
            chain = self.prompt | self.llm | self.output_parser
            
            # Generate the validation result
            result = chain.invoke({"query": query})
            
            return result
        
        except Exception as e:
            # Create a structured error response
            return MedicalValidation(
                summary="Error processing the query",
                validation_results=[
                    ValidationResult(
                        incorrect_text=str(e),
                        correct_text="Unable to validate the information due to an processing error"
                    )
                ]
            )

def get_medical_validation(query: str) -> dict:
    """
    Wrapper function to validate medical information
    
    Args:
        query (str): The text to be fact-checked
    
    Returns:
        dict: JSON-compatible validation results
    """
    checker = MedicalFactChecker()
    result = checker.validate(query)
    
    # Convert Pydantic model to dictionary
    return result.model_dump()

# Example usage
if __name__ == "__main__":
    test_query = """Cancer is caused by a virus. Drinking mango juice is good for health. Masks are not effective in preventing the spread of COVID-19."""
    
    validation_result = get_medical_validation(test_query)
   
    print(json.dumps(validation_result, indent=2))