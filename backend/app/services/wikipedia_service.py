"""
Service for fetching and parsing Wikipedia articles
"""
import wikipediaapi
import mwparserfromhell
from typing import Dict, List, Optional
from app.core.config import settings


class WikipediaService:
    def __init__(self):
        self.wiki_en = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent=settings.WIKIPEDIA_USER_AGENT
        )
    
    async def fetch_article(self, title: str, languages: List[str]) -> Dict:
        """
        Fetch article content, references, and cross-language versions
        """
        article_data = {
            'title': title,
            'content': '',
            'sections': [],
            'references': [],
            'cross_language': {},
            'metadata': {}
        }
        
        # Implementation will be added
        # This is a placeholder structure
        
        return article_data
    
    async def get_article_info(self, title: str) -> Dict:
        """
        Get basic article information
        """
        page = self.wiki_en.page(title)
        
        if not page.exists():
            raise ValueError(f"Article '{title}' not found")
        
        return {
            'title': page.title,
            'page_id': page.pageid,
            'url': page.fullurl,
            'summary': page.summary,
            'word_count': len(page.text.split()),
            'available_languages': list(page.langlinks.keys())
        }
    
    async def get_available_languages(self, title: str) -> List[str]:
        """
        Get available language versions
        """
        page = self.wiki_en.page(title)
        
        if not page.exists():
            raise ValueError(f"Article '{title}' not found")
        
        return list(page.langlinks.keys())
