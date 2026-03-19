"""Web scraper using BeautifulSoup and httpx"""
from typing import Dict, Optional
import httpx
from bs4 import BeautifulSoup
from config import settings
import validators
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class WebScraperTool:
    """
    Web scraper that fetches HTML and uses AI to extract structured data
    Uses BeautifulSoup for HTML parsing and Gemini for extraction
    """
    
    def __init__(self):
        if settings.google_api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                convert_system_message_to_human=True
            )
        else:
            self.llm = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def scrape(
        self, 
        url: str, 
        extraction_prompt: Optional[str] = None
    ) -> Dict:
        """
        Scrape a website and extract structured data
        
        Args:
            url: URL to scrape
            extraction_prompt: Optional LLM prompt for structured extraction
        
        Returns:
            Dictionary with scraped content
        """
        
        # Validate URL
        if not validators.url(url):
            print(f"DEBUG: [WebScraperTool] Invalid URL: {url}")
            return {"error": f"Invalid URL: {url}", "success": False}
        
        print(f"DEBUG: [WebScraperTool] Starting scrape for: {url}")
        try:
            # Fetch the webpage
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
            print(f"DEBUG: [WebScraperTool] Successfully fetched {url} (Status: {response.status_code})")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            print(f"DEBUG: [WebScraperTool] Extracted text length: {len(text_content)} chars")
            
            # Get metadata
            title = soup.find('title')
            title_text = title.string if title else ""
            
            description = soup.find('meta', attrs={'name': 'description'})
            description_text = description.get('content', '') if description else ""
            
            # Basic scraping (return text)
            if not extraction_prompt:
                return {
                    "url": url,
                    "success": True,
                    "markdown": text_content[:5000],  # First 5000 chars
                    "html": response.text[:5000],
                    "metadata": {
                        "title": title_text,
                        "description": description_text
                    }
                }
            
            # Advanced scraping with LLM extraction
            else:
                if not self.llm:
                    return {"error": "Google API key not configured", "success": False}
                
                prompt = f"{extraction_prompt}\n\nWebpage content:\n{text_content[:3000]}"
                response = self.llm.invoke([HumanMessage(content=prompt)])
                
                return {
                    "url": url,
                    "success": True,
                    "extracted_data": response.content,
                    "markdown": text_content[:1000],
                }
        
        except Exception as e:
            print(f"DEBUG: [WebScraperTool] Error scraping {url}: {e}")
            return {
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    def scrape_contact_info(self, url: str) -> Dict:
        """Specialized scraping for contact information"""
        
        prompt = """
        Extract contact information from this page:
        - Email addresses
        - Phone numbers
        - Physical address
        - Contact form URL
        - Social media links (LinkedIn, Twitter, Facebook)
        
        Return as JSON.
        """
        
        return self.scrape(url, extraction_prompt=prompt)

# Lazy initialization - only create when needed
_web_scraper_tool = None

def get_web_scraper_tool():
    """Get or create the web scraper tool singleton"""
    global _web_scraper_tool
    if _web_scraper_tool is None:
        _web_scraper_tool = WebScraperTool()
    return _web_scraper_tool

# For backward compatibility
class _WebScraperProxy:
    def __getattr__(self, name):
        return getattr(get_web_scraper_tool(), name)

web_scraper_tool = _WebScraperProxy()
