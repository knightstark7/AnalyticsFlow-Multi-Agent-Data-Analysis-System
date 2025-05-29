import os
from langchain_core.tools import tool
from langchain_community.document_loaders import WebBaseLoader, FireCrawlLoader
from typing import Annotated, List
from bs4 import BeautifulSoup
import requests
from logger import setup_logger
from load_cfg import FIRECRAWL_API_KEY, CHROMEDRIVER_PATH

# Try to import selenium with fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Set up logger
logger = setup_logger()

@tool
def google_search(query: Annotated[str, "The search query to use"]) -> str:
    """
    Perform a Google search based on the given query and return the top 5 results.
    
    This function tries multiple methods:
    1. Selenium with Chrome driver (if available)
    2. Simple requests-based search (fallback)
    3. DuckDuckGo search (alternative)

    Args:
    query (str): The search query to use.

    Returns:
    str: A string containing the search results.
    """
    try:
        logger.info(f"Performing search for query: {query}")
        
        # Method 1: Try Selenium if available and Chrome driver is configured
        if SELENIUM_AVAILABLE and CHROMEDRIVER_PATH and os.path.exists(CHROMEDRIVER_PATH):
            try:
                return _google_search_selenium(query)
            except Exception as selenium_error:
                logger.warning(f"Selenium search failed: {str(selenium_error)}. Trying fallback methods.")
        
        # Method 2: Try requests-based search
        try:
            return _google_search_requests(query)
        except Exception as requests_error:
            logger.warning(f"Requests-based search failed: {str(requests_error)}. Trying DuckDuckGo.")
        
        # Method 3: DuckDuckGo fallback
        try:
            return _duckduckgo_search(query)
        except Exception as ddg_error:
            logger.error(f"All search methods failed. DuckDuckGo error: {str(ddg_error)}")
            
        # Method 4: Return a helpful message if all fail
        return f"Search temporarily unavailable. Query was: {query}. Please try using manual research or check system configuration."
        
    except Exception as e:
        logger.error(f"Critical error during search: {str(e)}")
        return f'Search Error: {e}. Please check system configuration or try again later.'

def _google_search_selenium(query: str) -> str:
    """Perform Google search using Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(CHROMEDRIVER_PATH)

    with webdriver.Chrome(options=chrome_options, service=service) as driver:
        url = f"https://www.google.com/search?q={query}"
        logger.debug(f"Accessing URL: {url}")
        driver.get(url)
        html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.select('.g') 
    search = ""
    for result in search_results[:5]:
        title_element = result.select_one('h3')
        title = title_element.text if title_element else 'No Title'
        snippet_element = result.select_one('.VwiC3b')
        snippet = snippet_element.text if snippet_element else 'No Snippet'
        link_element = result.select_one('a')
        link = link_element['href'] if link_element else 'No Link'
        search += f"{title}\n{snippet}\n{link}\n\n"

    logger.info("Google search with Selenium completed successfully")
    return search

def _google_search_requests(query: str) -> str:
    """Perform search using requests (simplified)"""
    logger.info("Using requests-based search fallback")
    
    # This is a simplified search - in production you might want to use Google Custom Search API
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Note: This is a basic implementation. For production, use Google Custom Search API
        search_url = f"https://www.google.com/search?q={query}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Simple extraction - may need adjustment based on Google's current structure
            for g in soup.find_all('div', class_='g')[:5]:
                title_elem = g.find('h3')
                title = title_elem.text if title_elem else 'No title'
                
                link_elem = g.find('a')
                link = link_elem['href'] if link_elem else 'No link'
                
                results.append(f"{title}\n{link}\n")
            
            return "\n".join(results) if results else f"No results found for: {query}"
        else:
            raise Exception(f"HTTP {response.status_code}")
            
    except Exception as e:
        raise Exception(f"Requests search failed: {str(e)}")

def _duckduckgo_search(query: str) -> str:
    """Perform search using DuckDuckGo as fallback"""
    logger.info("Using DuckDuckGo search fallback")
    
    try:
        # Try to use duckduckgo-search if available
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                
            search_text = ""
            for result in results:
                search_text += f"{result.get('title', 'No Title')}\n"
                search_text += f"{result.get('body', 'No Description')}\n"
                search_text += f"{result.get('href', 'No Link')}\n\n"
            
            return search_text if search_text else f"No results found for: {query}"
            
        except ImportError:
            # If duckduckgo-search is not installed, provide alternative
            return f"Search functionality limited. Query: {query}. Please install 'duckduckgo-search' package for better search capabilities."
            
    except Exception as e:
        raise Exception(f"DuckDuckGo search failed: {str(e)}")

@tool
def scrape_webpages(urls: Annotated[List[str], "List of URLs to scrape"]) -> str:
    """
    Scrape the provided web pages for detailed information using WebBaseLoader.

    This function uses the WebBaseLoader to load and scrape the content of the provided URLs.

    Args:
    urls (List[str]): A list of URLs to scrape.

    Returns:
    str: A string containing the concatenated content of all scraped web pages.

    Raises:
    Exception: If there's an error during the scraping process.
    """
    try:
        logger.info(f"Scraping webpages: {urls}")
        loader = WebBaseLoader(urls)
        docs = loader.load()
        content = "\n\n".join([f'\n{doc.page_content}\n' for doc in docs])
        logger.info("Webpage scraping completed successfully")
        return content
    except Exception as e:
        logger.error(f"Error during webpage scraping: {str(e)}")
        raise  # Re-raise the exception to be caught by the calling function

@tool
def FireCrawl_scrape_webpages(urls: Annotated[List[str], "List of URLs to scrape"]) -> str:
    """
    Scrape the provided web pages for detailed information using FireCrawlLoader.

    This function uses the FireCrawlLoader to load and scrape the content of the provided URLs.

    Args:
    urls (List[str]): A list of URLs to scrape.

    Returns:
    Any: The result of the FireCrawlLoader's load operation.

    Raises:
    Exception: If there's an error during the scraping process or if the API key is not set.
    """
    if not FIRECRAWL_API_KEY:
        raise ValueError("FireCrawl API key is not set")

    try:
        logger.info(f"Scraping webpages using FireCrawl: {urls}")
        loader = FireCrawlLoader(
            api_key=FIRECRAWL_API_KEY,
            url=urls,
            mode="scrape"
        )
        result = loader.load()
        logger.info("FireCrawl scraping completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error during FireCrawl scraping: {str(e)}")
        raise  # Re-raise the exception to be caught by the calling function

@tool
def scrape_webpages_with_fallback(urls: Annotated[List[str], "List of URLs to scrape"]) -> str:
    """
    Attempt to scrape webpages using FireCrawl, falling back to WebBaseLoader if unsuccessful.

    Args:
    urls (List[str]): A list of URLs to scrape.

    Returns:
    str: The scraped content from either FireCrawl or WebBaseLoader.
    """
    try:
        return FireCrawl_scrape_webpages(urls)
    except Exception as e:
        logger.warning(f"FireCrawl scraping failed: {str(e)}. Falling back to WebBaseLoader.")
        try:
            return scrape_webpages(urls)
        except Exception as e:
            logger.error(f"Both scraping methods failed. Error: {str(e)}")
            return f"Error: Unable to scrape webpages using both methods. {str(e)}"

logger.info("Web scraping tools initialized")