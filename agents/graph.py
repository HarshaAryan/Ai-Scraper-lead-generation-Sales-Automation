"""
LangGraph workflow definition - connects all agents
"""
from langgraph.graph import StateGraph, END
from .state import AgentState, create_initial_state
from .supervisor import supervisor_node
from .scraper import scraper_node
from .search_agents import maps_search_node, web_search_node
from config import settings

# Try to import SqliteSaver, but make it optional
try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.checkpoint.sqlite import SqliteSaver
    CHECKPOINTING_AVAILABLE = True
except ImportError:
    CHECKPOINTING_AVAILABLE = False
    print("Warning: SqliteSaver not available. Running without checkpointing.")

def create_workflow():
    """
    Create the LangGraph workflow
    
    Flow:
    1. User query -> Supervisor (analyzes and plans)
    2. Supervisor -> Maps/Web Search (based on query type)
    3. Search -> Scraper (extracts data from results)
    4. Scraper -> Supervisor (reports back)
    5. Supervisor -> END (when plan complete)
    """
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("maps_searcher", maps_search_node)
    workflow.add_node("web_searcher", web_search_node)
    workflow.add_node("scraper", scraper_node)
    
    # Define routing logic
    def route_from_supervisor(state: AgentState) -> str:
        """Decide where to go from supervisor"""
        next_agent = state.get("next_agent", "END")
        
        if next_agent == "END" or not state.get("should_continue", True):
            return END
        
        return next_agent
    
    # Add edges
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "maps_searcher": "maps_searcher",
            "web_searcher": "web_searcher",
            "scraper": "scraper",
            END: END
        }
    )
    
    # Search agents go to scraper
    workflow.add_edge("maps_searcher", "scraper")
    workflow.add_edge("web_searcher", "scraper")
    
    # Scraper goes back to supervisor
    workflow.add_edge("scraper", "supervisor")
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Compile workflow (with or without checkpointing)
    if CHECKPOINTING_AVAILABLE:
        try:
            import sqlite3
            conn = sqlite3.connect(
                f"{settings.data_dir}/checkpoints.db",
                check_same_thread=False
            )
            memory = SqliteSaver(conn)
            app = workflow.compile(checkpointer=memory)
            print("Checkpointing enabled")
        except Exception as e:
            print(f"Warning: Could not enable checkpointing: {e}")
            memory = MemorySaver()
            app = workflow.compile(checkpointer=memory)
    else:
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
    
    return app

# Create the global workflow instance
graph = create_workflow()
