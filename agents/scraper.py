"""
Scraper Agent - Handles web scraping and data extraction
"""
from typing import Dict, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .state import AgentState, Lead
from tools.scraper import web_scraper_tool
from tools.validator import website_validator
from tools.maps_search import maps_search_tool
from config import settings
import json
from datetime import datetime
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

# Configure Gemini API
genai.configure(api_key=settings.google_api_key)

class GeminiWrapper:
    """Wrapper around google.generativeai that mimics LangChain interface"""
    
    def __init__(self, model="gemini-2.0-flash", temperature=0):
        self.model = genai.GenerativeModel(model)
        self.temperature = temperature
    
    def invoke(self, messages):
        """Convert LangChain messages to Gemini format and get response"""
        # Convert messages to text
        prompt_parts = []
        for msg in messages:
            if isinstance(msg, (SystemMessage, HumanMessage)):
                prompt_parts.append(msg.content)
            elif isinstance(msg, AIMessage):
                prompt_parts.append(f"Assistant: {msg.content}")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Generate response with retry
        @retry(
            retry=retry_if_exception_type(ResourceExhausted),
            wait=wait_exponential(multiplier=2, min=5, max=60),
            stop=stop_after_attempt(5)
        )
        def generate_with_retry():
            return self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature
                )
            )
            
        try:
            response = generate_with_retry()
        except Exception as e:
            print(f"Error generating content after retries: {e}")
            raise e
        
        # Return as AIMessage-like object
        class Response:
            def __init__(self, text):
                self.content = text
        
        return Response(response.text)

class ScraperAgent:
    """
    The Scraper Agent handles:
    1. Taking URLs from the state
    2. Scraping each website
    3. Extracting structured data using LLM
    4. Converting to Lead format
    """
    
    def __init__(self):
        self.llm = GeminiWrapper(
            model="gemini-2.0-flash",
            temperature=0
        )
    
    def __call__(self, state: AgentState) -> Dict:
        """Main scraper logic"""
        
        # Check if we have URLs to scrape
        urls_to_scrape = state.get("urls_to_scrape", [])
        search_results = state.get("search_results", [])
        
        if not urls_to_scrape and not search_results:
            return {
                "messages": ["⚠️ Scraper: No URLs to scrape"],
                "next_agent": "supervisor"
            }
        
        # If we have search results from Maps, process them differently
        if search_results and state.get("query_type") == "local_business":
            return self._process_map_results(state)
        
        # Otherwise, scrape URLs
        return self._scrape_urls(state)
    
    def _process_map_results(self, state: AgentState) -> Dict:
        """Process Google Maps search results"""
        
        search_results = state["search_results"]
        query = state["query"]
        
        leads = []
        messages = [f"🔍 Scraper: Processing {len(search_results)} businesses from Google Maps"]
        
        for result in search_results:
            # Convert map result to Lead
            lead = Lead(
                company_name=result.get("name", "Unknown"),
                website=result.get("website"),
                phone=result.get("phone"),
                email=None,  # Not available from Maps
                address=result.get("address"),
                rating=result.get("rating"),
                source_url=result.get("source_url", ""),
                found_at=datetime.utcnow().isoformat(),
                notes=f"Found via Google Maps. {result.get('reviews', 0)} reviews",
                website_status=self._check_website_status(result.get("website"))
            )
            leads.append(lead)
        
        # Filter based on query intent (e.g., "without websites")
        if "without website" in query.lower() or "no website" in query.lower():
            leads = [l for l in leads if l["website_status"] in ["missing", "404", "unreachable"]]
            messages.append(f"✅ Filtered to {len(leads)} businesses without active websites")
        
        return {
            "leads": leads,
            "messages": messages,
            "next_agent": "supervisor",
            "scraped_pages": [{"source": "google_maps", "count": len(search_results)}]
        }
    
    def _scrape_urls(self, state: AgentState) -> Dict:
        """Scrape a list of URLs and extract structured data"""
        
        urls = state["urls_to_scrape"][:10]  # Limit to 10 for now
        query = state["query"]
        
        print(f"DEBUG: [ScraperAgent] Starting processing of {len(urls)} URLs")
        
        messages = [f"🌐 Scraper: Scraping {len(urls)} websites"]
        scraped_pages = []
        leads = []
        
        for url in urls:
            messages.append(f"📄 Scraping: {url}")
            
            # Scrape the page
            result = web_scraper_tool.scrape(url)
            
            if not result.get("success"):
                messages.append(f"❌ Failed to scrape {url}")
                continue
            
            scraped_pages.append(result)
            
            # Extract structured data using LLM
            print(f"DEBUG: [ScraperAgent] Extracting data from {url}...")
            lead_data = self._extract_lead_from_page(result, query)
            print(f"DEBUG: [ScraperAgent] Data extraction success: {bool(lead_data)}")
            
            if lead_data:
                lead = Lead(
                    company_name=lead_data.get("company_name", "Unknown"),
                    website=url,
                    phone=lead_data.get("phone"),
                    email=lead_data.get("email"),
                    address=lead_data.get("address"),
                    rating=None,
                    source_url=url,
                    found_at=datetime.utcnow().isoformat(),
                    notes=lead_data.get("notes", ""),
                    website_status="active"
                )
                leads.append(lead)
                messages.append(f"✅ Extracted lead: {lead['company_name']}")
        
        return {
            "leads": leads,
            "messages": messages,
            "scraped_pages": scraped_pages,
            "next_agent": "supervisor"
        }
    
    def _extract_lead_from_page(self, scraped_result: Dict, query: str) -> Dict:
        """Use LLM to extract structured data from scraped content"""
        
        markdown = scraped_result.get("markdown", "")[:3000]  # Limit tokens
        
        system_prompt = f"""You are a data extraction expert. Extract relevant information from this webpage based on the user's query.

User Query: {query}

Extract the following fields if available:
- company_name
- phone
- email
- address
- notes (any other relevant info)

Return as JSON. If a field is not found, use null."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Page content:\n\n{markdown}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            return json.loads(response.content)
        except Exception as e:
            print(f"DEBUG: [ScraperAgent] Error in LLM extraction: {e}")
            return {}
    
    def _check_website_status(self, url: str) -> str:
        """Check if a website is active"""
        if not url:
            return "missing"
        
        result = website_validator.check_url(url)
        return result.get("status", "unknown")

def scraper_node(state: AgentState) -> AgentState:
    """LangGraph node wrapper"""
    # Ensure API key is configured before creating agent
    genai.configure(api_key=settings.google_api_key)
    scraper = ScraperAgent()
    updates = scraper(state)
    return {**state, **updates}
