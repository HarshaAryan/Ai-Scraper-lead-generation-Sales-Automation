"""Shared state definition for LangGraph agents"""
from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add
from datetime import datetime

class Lead(TypedDict):
    """Structure for a single lead"""
    company_name: str
    website: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    rating: Optional[float]
    source_url: str
    found_at: str
    notes: Optional[str]
    website_status: str  # "active", "missing", "404", "unknown"

class AgentState(TypedDict):
    """
    The shared state that flows through the LangGraph workflow.
    Each agent reads from and writes to this state.
    """
    # Input
    query: str                                    # Original user query
    query_type: Optional[str]                     # "local_business", "lead_gen", "website_audit"
    
    # Planning
    plan: Optional[List[str]]                     # Step-by-step plan from supervisor
    current_step: int                             # Which step we're on
    
    # Search Results
    search_results: List[Dict]                    # Raw search results
    urls_to_scrape: List[str]                     # URLs identified for scraping
    
    # Scraped Data
    scraped_pages: List[Dict]                     # Raw scraped content
    
    # Extracted Leads
    leads: Annotated[List[Lead], add]            # Final structured leads (accumulates)
    
    # Agent Communication
    messages: Annotated[List[str], add]          # Agent thoughts/logs (accumulates)
    
    # Control Flow
    next_agent: Optional[str]                     # Which agent to call next
    should_continue: bool                         # Whether to keep processing
    
    # Metadata
    started_at: str
    completed_at: Optional[str]
    error: Optional[str]

def create_initial_state(query: str) -> AgentState:
    """Create initial state from user query"""
    return AgentState(
        query=query,
        query_type=None,
        plan=None,
        current_step=0,
        search_results=[],
        urls_to_scrape=[],
        scraped_pages=[],
        leads=[],
        messages=[],
        next_agent="supervisor",
        should_continue=True,
        started_at=datetime.utcnow().isoformat(),
        completed_at=None,
        error=None
    )
