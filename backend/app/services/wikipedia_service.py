"""
Service for fetching and parsing Wikipedia articles
"""
import wikipediaapi
import mwparserfromhell
from typing import Dict, List, Optional, Any
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class WikipediaService:
    def __init__(self, user_agent: Optional[str] = None, language: str = 'en'):
        """
        Initialize Wikipedia service
        
        Args:
            user_agent: Custom user agent (uses settings if not provided)
            language: Default language code
        """
        self.user_agent = user_agent or settings.WIKIPEDIA_USER_AGENT
        self.default_language = language
        
        # Initialize Wikipedia API clients for different formats
        self.wiki_text = wikipediaapi.Wikipedia(
            user_agent=self.user_agent,
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        
        self.wiki_html = wikipediaapi.Wikipedia(
            user_agent=self.user_agent,
            language=language,
            extract_format=wikipediaapi.ExtractFormat.HTML
        )
    
    def get_wiki_client(self, language: str, extract_format: str = 'wiki') -> wikipediaapi.Wikipedia:
        """
        Get Wikipedia client for specific language
        
        Args:
            language: Language code (e.g., 'en', 'sw', 'fr')
            extract_format: 'wiki' or 'html'
            
        Returns:
            Wikipedia API client
        """
        fmt = wikipediaapi.ExtractFormat.HTML if extract_format == 'html' else wikipediaapi.ExtractFormat.WIKI
        
        return wikipediaapi.Wikipedia(
            user_agent=self.user_agent,
            language=language,
            extract_format=fmt
        )
    
    async def fetch_article(self, title: str, languages: Optional[List[str]] = None) -> Dict:
        """
        Fetch comprehensive article data including content, sections, references, and translations
        
        Args:
            title: Article title
            languages: List of language codes for cross-language comparison (default: ['en'])
            
        Returns:
            Dictionary with article data
        """
        if languages is None:
            languages = ['en']
        
        # Get main article
        page = self.wiki_text.page(title)
        
        if not page.exists():
            raise ValueError(f"Article '{title}' not found")
        
        article_data = {
            'title': page.title,
            'content': page.text,
            'summary': page.summary,
            'sections': self._extract_sections(page),
            'references': self._extract_references(page),
            'links': self._extract_links(page),
            'categories': self._extract_categories(page),
            'cross_language': self._fetch_language_versions(page, languages),
            'metadata': {
                'page_id': page.pageid,
                'namespace': page.namespace,
                'url': page.fullurl,
                'canonical_url': page.canonicalurl,
                'word_count': len(page.text.split()),
                'section_count': len(list(page.sections)),
                'available_languages': list(page.langlinks.keys())
            }
        }
        
        return article_data
    
    def _extract_sections(self, page: wikipediaapi.WikipediaPage) -> List[Dict]:
        """
        Extract all sections recursively from the page
        
        Args:
            page: WikipediaPage object
            
        Returns:
            List of section dictionaries
        """
        sections = []
        
        def extract_recursive(sections_list, level=1):
            for section in sections_list:
                section_data = {
                    'title': section.title,
                    'text': section.text,
                    'level': level,
                    'full_text': section.full_text
                }
                sections.append(section_data)
                
                # Recursively extract subsections
                if section.sections:
                    extract_recursive(section.sections, level + 1)
        
        extract_recursive(page.sections)
        return sections
    
    def _extract_references(self, page: wikipediaapi.WikipediaPage) -> List[Dict]:
        """
        Extract references from page wikitext
        
        Args:
            page: WikipediaPage object
            
        Returns:
            List of reference dictionaries
        """
        references = []
        
        try:
            # Get HTML version to parse references
            html_page = self.wiki_html.page(page.title)
            wikicode = mwparserfromhell.parse(html_page.text)
            
            templates = wikicode.filter_templates()
            
            for template in templates:
                template_name = str(template.name).strip().lower()
                
                # Check if it's a citation template
                if any(cite_word in template_name for cite_word in ['cite', 'citation', 'ref']):
                    ref_data = self._parse_citation_template(template)
                    if ref_data:
                        references.append(ref_data)
        
        except Exception as e:
            logger.warning(f"Could not extract references: {e}")
        
        return references
    
    def _parse_citation_template(self, template) -> Optional[Dict]:
        """
        Parse a citation template into structured data
        
        Args:
            template: mwparserfromhell template object
            
        Returns:
            Dictionary with citation data or None
        """
        citation = {
            'type': str(template.name).strip(),
            'authors': [],
            'title': None,
            'publisher': None,
            'year': None,
            'url': None,
            'doi': None,
            'isbn': None,
            'pmid': None,
            'raw': str(template)
        }
        
        try:
            for param in template.params:
                key = str(param.name).strip().lower()
                value = str(param.value).strip()
                
                if not value:
                    continue
                
                # Extract authors
                if key in ['author', 'last', 'first', 'author1', 'last1', 'first1']:
                    citation['authors'].append(value)
                elif key.startswith('author') or key.startswith('last'):
                    citation['authors'].append(value)
                
                # Extract title
                elif key == 'title':
                    citation['title'] = value
                
                # Extract publisher/work/journal
                elif key in ['publisher', 'work', 'journal', 'newspaper', 'magazine']:
                    citation['publisher'] = value
                
                # Extract year/date
                elif key in ['year', 'date', 'publication-date']:
                    citation['year'] = self._extract_year(value)
                
                # Extract identifiers
                elif key == 'url':
                    citation['url'] = value
                elif key == 'doi':
                    citation['doi'] = value
                elif key == 'isbn':
                    citation['isbn'] = value
                elif key == 'pmid':
                    citation['pmid'] = value
        
        except Exception as e:
            logger.warning(f"Error parsing citation template: {e}")
            return None
        
        return citation
    
    def _extract_year(self, date_string: str) -> Optional[int]:
        """
        Extract year from date string
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            Year as integer or None
        """
        import re
        
        # Try to find a 4-digit year
        match = re.search(r'\b(19|20)\d{2}\b', date_string)
        if match:
            try:
                return int(match.group(0))
            except ValueError:
                pass
        
        return None
    
    def _extract_links(self, page: wikipediaapi.WikipediaPage) -> List[Dict]:
        """
        Extract links to other Wikipedia pages
        
        Args:
            page: WikipediaPage object
            
        Returns:
            List of link dictionaries
        """
        links = []
        
        for title, linked_page in page.links.items():
            links.append({
                'title': title,
                'page_id': linked_page.pageid if hasattr(linked_page, 'pageid') else None,
                'namespace': linked_page.ns if hasattr(linked_page, 'ns') else 0,
                'url': linked_page.fullurl if hasattr(linked_page, 'fullurl') else None
            })
        
        return links
    
    def _extract_categories(self, page: wikipediaapi.WikipediaPage) -> List[Dict]:
        """
        Extract categories the page belongs to
        
        Args:
            page: WikipediaPage object
            
        Returns:
            List of category dictionaries
        """
        categories = []
        
        for title, category in page.categories.items():
            categories.append({
                'title': title,
                'page_id': category.pageid if hasattr(category, 'pageid') else None,
                'namespace': category.ns if hasattr(category, 'ns') else 14
            })
        
        return categories
    
    def _fetch_language_versions(self, page: wikipediaapi.WikipediaPage, languages: List[str]) -> Dict[str, Dict]:
        """
        Fetch article versions in different languages
        
        Args:
            page: WikipediaPage object for the main article
            languages: List of language codes to fetch
            
        Returns:
            Dictionary mapping language codes to article data
        """
        language_versions = {}
        
        for lang_code in languages:
            if lang_code == self.default_language:
                continue
            
            try:
                if lang_code in page.langlinks:
                    lang_page = page.langlinks[lang_code]
                    
                    # Fetch full content for this language
                    wiki_lang = self.get_wiki_client(lang_code)
                    full_lang_page = wiki_lang.page(lang_page.title)
                    
                    if full_lang_page.exists():
                        language_versions[lang_code] = {
                            'title': full_lang_page.title,
                            'content': full_lang_page.text,
                            'summary': full_lang_page.summary,
                            'url': full_lang_page.fullurl,
                            'word_count': len(full_lang_page.text.split()),
                            'section_count': len(list(full_lang_page.sections))
                        }
            
            except Exception as e:
                logger.warning(f"Could not fetch {lang_code} version: {e}")
        
        return language_versions
    
    async def get_article_info(self, title: str) -> Dict:
        """
        Get basic article information
        
        Args:
            title: Article title
            
        Returns:
            Dictionary with basic article info
        """
        page = self.wiki_text.page(title)
        
        if not page.exists():
            raise ValueError(f"Article '{title}' not found")
        
        return {
            'title': page.title,
            'page_id': page.pageid,
            'namespace': page.namespace,
            'url': page.fullurl,
            'canonical_url': page.canonicalurl,
            'summary': page.summary,
            'word_count': len(page.text.split()),
            'section_count': len(list(page.sections)),
            'available_languages': list(page.langlinks.keys())
        }
    
    async def get_available_languages(self, title: str) -> List[str]:
        """
        Get available language versions for an article
        
        Args:
            title: Article title
            
        Returns:
            List of language codes
        """
        page = self.wiki_text.page(title)
        
        if not page.exists():
            raise ValueError(f"Article '{title}' not found")
        
        return list(page.langlinks.keys())
    
    async def get_page_categories(self, title: str, recursive: bool = False, max_depth: int = 1) -> List[Dict]:
        """
        Get categories for a page, optionally with recursive subcategories
        
        Args:
            title: Article title
            recursive: Whether to fetch subcategories recursively
            max_depth: Maximum depth for recursive fetching
            
        Returns:
            List of category dictionaries
        """
        page = self.wiki_text.page(title)
        
        if not page.exists():
            raise ValueError(f"Article '{title}' not found")
        
        categories = []
        
        for cat_title, category in page.categories.items():
            cat_data = {
                'title': cat_title,
                'page_id': category.pageid if hasattr(category, 'pageid') else None,
                'namespace': category.ns if hasattr(category, 'ns') else 14
            }
            
            if recursive and max_depth > 0:
                cat_data['subcategories'] = self._get_category_members(category, max_depth - 1)
            
            categories.append(cat_data)
        
        return categories
    
    def _get_category_members(self, category, max_depth: int, current_depth: int = 0) -> List[Dict]:
        """
        Recursively get category members
        
        Args:
            category: WikipediaPage category object
            max_depth: Maximum depth to recurse
            current_depth: Current recursion depth
            
        Returns:
            List of member dictionaries
        """
        if current_depth >= max_depth:
            return []
        
        members = []
        
        try:
            for member_title, member in category.categorymembers.items():
                member_data = {
                    'title': member_title,
                    'namespace': member.ns if hasattr(member, 'ns') else 0
                }
                
                # If it's a subcategory and we haven't reached max depth, recurse
                if member.ns == wikipediaapi.Namespace.CATEGORY and current_depth < max_depth:
                    member_data['members'] = self._get_category_members(member, max_depth, current_depth + 1)
                
                members.append(member_data)
        
        except Exception as e:
            logger.warning(f"Error getting category members: {e}")
        
        return members
    
    async def get_section_by_title(self, article_title: str, section_title: str) -> Optional[Dict]:
        """
        Get a specific section from an article by its title
        
        Args:
            article_title: Article title
            section_title: Section title to find
            
        Returns:
            Section dictionary or None if not found
        """
        page = self.wiki_text.page(article_title)
        
        if not page.exists():
            raise ValueError(f"Article '{article_title}' not found")
        
        section = page.section_by_title(section_title)
        
        if section:
            return {
                'title': section.title,
                'text': section.text,
                'full_text': section.full_text
            }
        
        return None
    
    async def search_articles(self, query: str, results: int = 10) -> List[str]:
        """
        Search for articles matching a query
        Note: This uses the page title search, not full-text search
        
        Args:
            query: Search query
            results: Maximum number of results
            
        Returns:
            List of article titles
        """
        # Wikipedia-API doesn't have built-in search, but we can use the API directly
        # For now, return empty list - would need to use requests to call search API
        logger.warning("Search functionality not yet fully implemented")
        return []
    
    def check_page_exists(self, title: str) -> bool:
        """
        Check if a Wikipedia page exists
        
        Args:
            title: Article title
            
        Returns:
            True if page exists, False otherwise
        """
        page = self.wiki_text.page(title)
        return page.exists()
