"""
Supervisor Agent - The "Router" that analyzes queries and orchestrates other agents
"""
from typing import Dict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.base import BaseLanguageModel
from .state import AgentState
from config import settings
import json
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from google.api_core.exceptions import ResourceExhausted

# Configure Gemini API
genai.configure(api_key=settings.google_api_key)

class GeminiWrapper:
    """Wrapper around google.generativeai that mimics LangChain interface"""
    
    def __init__(self, model="gemini-pro", temperature=0.1):
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

class SupervisorAgent:
    """
    The Supervisor analyzes the user's query and decides:
    1. What type of query is this? (local business, lead gen, website audit)
    2. What tools do we need?
    3. What's the step-by-step plan?
    """
    
    def __init__(self):
        self.llm = GeminiWrapper(
            model="gemini-2.0-flash",
            temperature=0.1
        )
    
    def __call__(self, state: AgentState) -> Dict:
        """Main supervisor logic"""
        
        query = state["query"]
        
        # If we already have a plan, update progress
        if state.get("plan"):
            return self._monitor_progress(state)
        
        # Otherwise, create a plan
        return self._create_plan(state)
    
    def _create_plan(self, state: AgentState) -> Dict:
        """Analyze query and create execution plan"""
        
        system_prompt = """You are a supervisor agent that analyzes user queries for web scraping and lead generation.

Your job is to:
1. Understand what the user wants
2. Classify the query type
3. Create a step-by-step plan
4. Decide which tools to use

Available tools:
- google_maps_search: Search for local businesses on Google Maps
- web_search: General internet search (news, companies, etc.)
- scrape_website: Extract content from a specific URL
- validate_website: Check if a website is active
- extract_emails: Find contact information from a page

Query types:
- local_business: Finding businesses in a specific location (gyms, restaurants, etc.)
- lead_gen: Finding companies/people based on criteria (funded startups, hiring managers)
- website_audit: Checking websites for issues or missing features

Examples:
Query: "Find gyms in Austin without websites"
Type: local_business
Plan: ["Use google_maps_search for 'gyms in Austin'", "For each result, check if website field exists", "If no website, use web_search to verify", "Compile leads"]

Query: "Find companies that just got Series A funding"
Type: lead_gen
Plan: ["Use web_search for 'Series A funding 2026'", "Extract company names from results", "Use web_search to find each company's hiring page", "Extract contact emails"]

Respond in JSON format:
{
    "query_type": "local_business|lead_gen|website_audit",
    "reasoning": "Why you classified it this way",
    "plan": ["step 1", "step 2", ...],
    "tools_needed": ["tool1", "tool2"],
    "estimated_results": 20
}
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze this query: {state['query']}")
        ]
        
        print(f"DEBUG: [Supervisor] Creating plan for query: {state['query']}")
        
        try:
            response = self.llm.invoke(messages)
            analysis = json.loads(response.content)
        except (RetryError, ResourceExhausted) as e:
            print(f"DEBUG: [Supervisor] API Rate Limit hit: {e}")
            return {
                "query_type": "error",
                "plan": [],
                "messages": ["❌ Supervisor: API Rate Limit Exceeded (429). Please try again in 60 seconds."],
                "next_agent": "END",
                "current_step": 0
            }
        except json.JSONDecodeError:
            print(f"DEBUG: [Supervisor] JSON Decode Error. Raw response: {response.content[:200]}...")
            # Fallback if LLM doesn't return valid JSON
            analysis = {
                "query_type": "local_business",
                "reasoning": "Could not parse response",
                "plan": ["Use web_search to find relevant results"],
                "tools_needed": ["web_search"],
                "estimated_results": 10
            }
            
        print(f"DEBUG: [Supervisor] Plan created. Query type: {analysis['query_type']}")
        return {
            "query_type": analysis["query_type"],
            "plan": analysis["plan"],
            "messages": [f"🧠 Supervisor: {analysis['reasoning']}"],
            "next_agent": self._decide_next_agent(analysis["query_type"]),
            "current_step": 0
        }
    
    def _monitor_progress(self, state: AgentState) -> Dict:
        """Check progress and decide next step"""
        
        plan = state["plan"]
        current_step = state["current_step"]
        
        # If we've completed all steps
        if current_step >= len(plan):
            return {
                "next_agent": "END",
                "should_continue": False,
                "messages": ["✅ Supervisor: All steps completed!"]
            }
        
        # Move to next step
        next_step = plan[current_step]
        
        return {
            "messages": [f"📋 Supervisor: Step {current_step + 1}/{len(plan)}: {next_step}"],
            "current_step": current_step + 1
        }
    
    def _decide_next_agent(self, query_type: str) -> str:
        """Decide which agent to call based on query type"""
        
        if query_type == "local_business":
            return "maps_searcher"
        elif query_type == "lead_gen":
            return "web_searcher"
        elif query_type == "website_audit":
            return "scraper"
        else:
            return "web_searcher"  # Default

def supervisor_node(state: AgentState) -> AgentState:
    """LangGraph node wrapper"""
    # Ensure API key is configured before creating agent
    genai.configure(api_key=settings.google_api_key)
    supervisor = SupervisorAgent()
    updates = supervisor(state)
    return {**state, **updates}
