import os
import re
import logging
import requests
import wikipedia
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv

import langchain
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_community.document_loaders import WebBaseLoader
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

class EnhancedBaseTool(BaseTool):
    name: str = Field(default="base_tool", description="Base tool name")
    description: str = Field(default="A base tool for medical information retrieval", description="Tool description")
    
    def _safe_run(self, func, *args, **kwargs) -> str:
        """Wrapper for safe tool execution with logging."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}")
            return f"Error in {self.name}: {str(e)}"

class WHONewsroomTool(EnhancedBaseTool):
    name: str = Field(default="who_newsroom_tool", description="WHO Newsroom search tool")
    description: str = Field(default="Search the latest news and articles from WHO on health topics", description="Tool description")
    
    def _run(self, query: str) -> str:
        def _fetch_who_results():
            url = f"https://www.who.int/news-room/search-results?indexCatalogue=genericsearchindex&searchQuery={quote_plus(query.strip())}"
            return f"WHO Newsroom Search Results for '{query}':\nVisit: {url}"
        
        return self._safe_run(_fetch_who_results)

class WHODataTool(EnhancedBaseTool):
    name: str = Field(default="who_data_tool", description="WHO Health Data search tool")
    description: str = Field(default="Search official health data from WHO", description="Tool description")
    
    def _run(self, query: str) -> str:
        def _fetch_who_data():
            url = f"https://www.who.int/data/gho/data/indicators?query={quote_plus(query.strip())}"
            return f"WHO Data Results for '{query}':\nVisit: {url}"
        
        return self._safe_run(_fetch_who_data)

class WikipediaMedicalTool(EnhancedBaseTool):
    name: str = Field(default="wikipedia_medical_tool", description="Wikipedia Medical Information search tool")
    description: str = Field(default="Search medical information from Wikipedia", description="Tool description")
    
    def _run(self, query: str) -> str:
        def _fetch_wikipedia_info():
            try:
                search_results = wikipedia.search(f"medical {query}")
                if not search_results:
                    return f"No Wikipedia articles found for '{query}'"
                
                page_title = search_results[0]
                page = wikipedia.page(page_title, auto_suggest=False)
                summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
                
                return f"Wikipedia Medical Information for '{page_title}':\n\n{summary}\n\nFull Article: {page.url}"
            except Exception as e:
                return f"Error fetching Wikipedia information: {str(e)}"
        
        return self._safe_run(_fetch_wikipedia_info)

class MedicalWebSearchTool(EnhancedBaseTool):
    name: str = Field(default="medical_web_search_tool", description="Medical Web Search tool")
    description: str = Field(default="Search the web for medical information", description="Tool description")
    
    def _run(self, query: str) -> str:
        def _perform_web_search():
            search_url = f"https://www.google.com/search?q={quote_plus('medical site:gov site:edu site:org ' + query)}"
            return f"Medical Web Search Results for '{query}':\nSearch URL: {search_url}"
        
        return self._safe_run(_perform_web_search)

class PubMedSearchTool(EnhancedBaseTool):
    name: str = Field(default="pubmed_search_tool", description="PubMed Research Article search tool")
    description: str = Field(default="Search peer-reviewed medical research articles", description="Tool description")
    
    def _run(self, query: str) -> str:
        def _search_pubmed():
            base_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={quote_plus(query)}"
            return f"PubMed Search Results for '{query}':\nVisit: {base_url}"
        
        return self._safe_run(_search_pubmed)

class EnhancedMedicalAgentSystem:
    def __init__(self, model: str = "gemini-2.0-flash", temperature: float = 0.2):
        # Initialize specific tools
        self.who_newsroom_tool = WHONewsroomTool()
        self.who_data_tool = WHODataTool()
        self.wikipedia_tool = WikipediaMedicalTool()
        self.web_search_tool = MedicalWebSearchTool()
        self.pubmed_tool = PubMedSearchTool()
        
        # Convert tools to Langchain Tool format
        self.tools = [
            Tool(
                name=tool.__class__.__name__.replace('Tool', ''), 
                func=tool._run, 
                description=tool.description
            ) for tool in [
                self.who_newsroom_tool, 
                self.who_data_tool, 
                self.wikipedia_tool, 
                self.web_search_tool, 
                self.pubmed_tool
            ]
        ]
        
        self.llm = ChatGoogleGenerativeAI(
            model=model, 
            temperature=temperature, 
            convert_system_message_to_human=True
        )
        
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = self._create_agent()
        
        # Attribute to store comprehensive search results
        self.search_results: Dict[str, str] = {}

    def _create_agent(self):
        """Create and configure the agent with a comprehensive approach."""
        custom_prompt = """
        You are an advanced medical information assistant. 
        Use multiple sources to provide comprehensive, accurate medical information.
        
        Query: {input}
        Context: {chat_history}

        Instruction: Synthesize information from various reliable sources.
        """
        
        return initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=False,
            max_iterations=5,
            early_stopping_method="generate",
            prompt=PromptTemplate(
                input_variables=["input", "chat_history"], 
                template=custom_prompt
            )
        )

    def comprehensive_search(self, query: str) -> Dict[str, str]:
        """
        Perform a comprehensive search across multiple sources.
        
        Args:
            query (str): The medical query to search
        
        Returns:
            Dict[str, str]: Dictionary of search results from different sources
        """
        # Reset previous search results
        self.search_results = {}
        
        # Perform searches across different tools
        search_methods = [
            ("WHO Newsroom", self.who_newsroom_tool._run),
            ("WHO Data", self.who_data_tool._run),
            ("Wikipedia", self.wikipedia_tool._run),
            ("Web Search", self.web_search_tool._run),
            ("PubMed", self.pubmed_tool._run)
        ]
        
        for source_name, search_method in search_methods:
            try:
                result = search_method(query)
                self.search_results[source_name] = result
            except Exception as e:
                self.search_results[source_name] = f"Error searching {source_name}: {str(e)}"
        
        return self.search_results

    def run(self, query: str) -> str:
        """
        Process the query and retrieve comprehensive information.
        
        Args:
            query (str): The medical query to process
        
        Returns:
            str: Synthesized medical information
        """
        try:
            # First, perform comprehensive search
            search_results = self.comprehensive_search(query)
            
            # Combine and synthesize results
            synthesized_response = self.agent.run(query)
            
            # Combine search results with agent's response
            full_response = f"Comprehensive Medical Information for '{query}':\n\n"
            full_response += "Synthesized Response:\n" + synthesized_response + "\n\n"
            full_response += "Search Results from Different Sources:\n"
            for source, result in search_results.items():
                full_response += f"\n{source}:\n{result}\n"
            
            return full_response
        except Exception as e:
            error_msg = f"An error occurred: {e}. Please try rephrasing your query."
            logger.error(f"Query processing error: {e}")
            return error_msg

def getValidation(query: str): # This function returns the validated response with important source links if any
    # Create the medical agent
    agent = EnhancedMedicalAgentSystem()

    try:    
        # Run the comprehensive search and get the response
        response = agent.run(query)
        print("\nAssistant:", response)
        return response
        
    except KeyboardInterrupt:
        print("\nOperation cancelled. Type 'exit' to quit.")