"""Website validator - checks if URLs are active"""
import httpx
import validators
from typing import Dict
import asyncio

class WebsiteValidator:
    """
    Validates websites and checks their status
    """
    
    def __init__(self):
        self.timeout = 10  # seconds
    
    async def check_url_async(self, url: str) -> Dict:
        """Asynchronously check if a URL is reachable"""
        
        if not validators.url(url):
            return {
                "url": url,
                "status": "invalid",
                "status_code": None,
                "reachable": False
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                
                return {
                    "url": url,
                    "status": "active" if response.status_code == 200 else "error",
                    "status_code": response.status_code,
                    "reachable": True,
                    "final_url": str(response.url)
                }
        
        except httpx.TimeoutException:
            return {
                "url": url,
                "status": "timeout",
                "status_code": None,
                "reachable": False
            }
        
        except Exception as e:
            return {
                "url": url,
                "status": "unreachable",
                "status_code": None,
                "reachable": False,
                "error": str(e)
            }
    
    def check_url(self, url: str) -> Dict:
        """Synchronous wrapper for async check"""
        return asyncio.run(self.check_url_async(url))
    
    async def check_multiple_urls(self, urls: list) -> list:
        """Check multiple URLs concurrently"""
        tasks = [self.check_url_async(url) for url in urls]
        return await asyncio.gather(*tasks)

# Singleton instance
website_validator = WebsiteValidator()
