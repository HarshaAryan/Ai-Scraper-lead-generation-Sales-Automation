"""Web search tool using Tavily API"""
from typing import List, Dict, Optional
from tavily import TavilyClient
from config import settings

class WebSearchTool:
    """
    General-purpose web search using Tavily
    Great for: news, company info, funding announcements, etc.
    """
    
    def __init__(self):
        self.api_key = settings.tavily_api_key
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.client = TavilyClient(api_key=self.api_key)
    
    def search(
        self, 
        query: str, 
        max_results: int = 10,
        search_depth: str = "advanced"
    ) -> List[Dict]:
        """
        Search the web for relevant content
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_depth: "basic" or "advanced"
        
        Returns:
            List of search results with title, url, content
        """
        
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_raw_content=False
            )
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0)
                })
            
            return results
            
        except Exception as e:
            print(f"Error performing web search: {e}")
            return []
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for recent news articles"""
        news_query = f"{query} news 2026"
        return self.search(news_query, max_results=max_results)

# Singleton instance
web_search_tool = WebSearchTool() if settings.tavily_api_key else None
