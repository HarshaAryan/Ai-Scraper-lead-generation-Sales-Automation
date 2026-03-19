"""
Search Agents - Handles Google Maps and Web searches
"""
from typing import Dict
from .state import AgentState
from tools.maps_search import maps_search_tool
from tools.web_search import web_search_tool
from config import settings
import re

class MapsSearchAgent:
    """Agent for searching Google Maps"""
    
    def __call__(self, state: AgentState) -> Dict:
        """Search Google Maps based on query"""
        
        query = state["query"]
        
        # Extract location and search term from query
        location, search_term = self._parse_query(query)
        
        messages = [f"🗺️ Maps Search: Looking for '{search_term}' in '{location}'"]
        
        if not maps_search_tool:
            return {
                "messages": ["❌ Maps Search: SerpAPI key not configured"],
                "next_agent": "supervisor"
            }
        
        # Search Google Maps
        results = maps_search_tool.search(
            query=search_term,
            location=location,
            max_results=50
        )
        
        messages.append(f"✅ Found {len(results)} businesses on Google Maps")
        
        return {
            "search_results": results,
            "messages": messages,
            "next_agent": "scraper"
        }
    
    def _parse_query(self, query: str) -> tuple:
        """Extract location and search term from natural language query"""
        
        # Simple pattern matching (can be improved with LLM)
        location_patterns = [
            r"in ([A-Za-z\s,]+?)(?:\s+within|\s+that|\s+without|\s*$)",
            r"near ([A-Za-z\s,]+?)(?:\s+that|\s+without|\s*$)",
            r"around ([A-Za-z\s,]+?)(?:\s+that|\s+without|\s*$)",
        ]
        
        location = None
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                break
        
        if not location:
            location = "United States"  # Default
        
        # Extract business type
        business_patterns = [
            r"(gyms?|restaurants?|cafes?|hotels?|spas?|salons?|businesses?)",
            r"types?\s+business\s+related\s+to\s+(\w+)",
        ]
        
        search_term = None
        for pattern in business_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                search_term = match.group(1).strip()
                break
        
        if not search_term:
            search_term = query.split()[0]  # Fallback: first word
        
        return location, search_term

class WebSearchAgent:
    """Agent for general web searches"""
    
    def __call__(self, state: AgentState) -> Dict:
        """Search the web based on query"""
        
        query = state["query"]
        
        messages = [f"🔎 Web Search: Searching for '{query}'"]
        
        if not web_search_tool:
            return {
                "messages": ["❌ Web Search: Tavily API key not configured"],
                "next_agent": "supervisor"
            }
        
        # Perform search
        results = web_search_tool.search(query, max_results=20)
        
        # Extract URLs
        urls = [r["url"] for r in results]
        
        messages.append(f"✅ Found {len(results)} relevant pages")
        
        return {
            "search_results": results,
            "urls_to_scrape": urls,
            "messages": messages,
            "next_agent": "scraper"
        }

def maps_search_node(state: AgentState) -> AgentState:
    """LangGraph node wrapper for Maps Search"""
    agent = MapsSearchAgent()
    updates = agent(state)
    return {**state, **updates}

def web_search_node(state: AgentState) -> AgentState:
    """LangGraph node wrapper for Web Search"""
    agent = WebSearchAgent()
    updates = agent(state)
    return {**state, **updates}
