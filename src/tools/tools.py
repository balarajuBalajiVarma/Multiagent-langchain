

# from langchain.tools import tool 
# import requests
# from dotenv import load_dotenv
# import os
# from tavily import TavilyClient
# from rich import print
# from bs4 import BeautifulSoup
# from readability import Document
# import trafilatura
# import re 


# load_dotenv()

# tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# @tool
# def web_Data_Collector(query : str) -> str:
#     """Search the web for recent and reliable information on a startup company . Returns Titles , URLs, Founders, Funding(How much and when), product (what they build), recent news.
#      Based on this informatio will decide to invest or not """
#     results = tavily.search(query=query,max_results=5)

#     out = []

#     for r in results['results']:
#         out.append(
#             f"Title: {r['title']}\nURL: {r['url']}\n"
#         )
    
#     return "\n----\n".join(out)

   
    

# @tool
# def scrape_url(url: str) -> str:
#     """
#     Scrape and extract clean readable content from a URL.
#     Uses multiple extraction strategies for better reliability.
#     """

#     headers = {
#         "User-Agent": (
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/124.0 Safari/537.36"
#         ),
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": "https://www.google.com/",
#     }

#     try:
#         # ── Fetch page ─────────────────────────────────────
#         response = requests.get(
#             url,
#             headers=headers,
#             timeout=15
#         )

#         response.raise_for_status()

#         html = response.text

#         # ──────────────────────────────────────────────────
#         # Strategy 1 → trafilatura (BEST for articles/blogs)
#         # ──────────────────────────────────────────────────
#         extracted = trafilatura.extract(
#             html,
#             include_comments=False,
#             include_tables=False
#         )

#         if extracted and len(extracted.strip()) > 200:
#             cleaned = re.sub(r'\s+', ' ', extracted)
#             return cleaned[:5000]

#         # ──────────────────────────────────────────────────
#         # Strategy 2 → readability
#         # ──────────────────────────────────────────────────
#         doc = Document(html)
#         clean_html = doc.summary()

#         soup = BeautifulSoup(clean_html, "html.parser")

#         for tag in soup([
#             "script",
#             "style",
#             "nav",
#             "footer",
#             "header",
#             "aside",
#             "form"
#         ]):
#             tag.decompose()

#         text = soup.get_text(separator=" ", strip=True)

#         if text and len(text.strip()) > 200:
#             cleaned = re.sub(r'\s+', ' ', text)
#             return cleaned[:5000]

#         # ──────────────────────────────────────────────────
#         # Strategy 3 → fallback full page extraction
#         # ──────────────────────────────────────────────────
#         soup = BeautifulSoup(html, "html.parser")

#         for tag in soup([
#             "script",
#             "style",
#             "nav",
#             "footer",
#             "header",
#             "aside",
#             "form"
#         ]):
#             tag.decompose()

#         text = soup.get_text(separator=" ", strip=True)

#         cleaned = re.sub(r'\s+', ' ', text)

#         if cleaned:
#             return cleaned[:5000]

#         return "Could not extract meaningful content from the page."

#     except requests.exceptions.Timeout:
#         return "Request timed out while scraping the URL."

#     except requests.exceptions.HTTPError as e:
#         return f"HTTP error occurred: {str(e)}"

#     except Exception as e:
#         return f"Could not scrape URL: {str(e)}"

from langchain_core.tools import tool
from tavily import TavilyClient
import trafilatura
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_Data_Collector(query: str) -> str:
    """Use this for Agent 1. Search startup company to get Website, Founders, Funding (how much & when), Product (what they build), Recent News. Input is startup name like 'Perplexity AI'."""
    
    # Step 1: Search for startup specific info
    search_queries = [
        f"{query} official website",
        f"{query} founders",
        f"{query} funding crunchbase",
        f"{query} product what they build",
        f"{query} recent news 2024 2025 2026"
    ]

    all_urls = []
    for q in search_queries:
        results = tavily.search(query=q, max_results=2, search_depth="advanced")
        for r in results['results']:
            all_urls.append(r['url'])
    
    # Remove duplicates
    all_urls = list(dict.fromkeys(all_urls))[:5]

    # Step 2: Scrape all urls in parallel
    def scrape(url):
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded) or ""
            return f"URL: {url}\nCONTENT: {text[:4000]}"
        except:
            return f"URL: {url}\nCONTENT: Failed"

    with ThreadPoolExecutor(max_workers=5) as executor:
        contents = list(executor.map(scrape, all_urls))

    # Step 3: Return structured format for Agent 1
    final_output = "\n----\n".join(contents)
    return f"""
    STARTUP: {query}
    
    RAW DATA:
    {final_output}
    
    INSTRUCTION: From    above raw data, extract and return in this format:
    - Website:
    - Founders:
    - Funding (How much & when):
    - Product (what they build):
    - Recent News:
    """

from langchain_core.tools import tool
from tavily import TavilyClient
import trafilatura
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def risk_finder(query: str) -> str:
    """This tool will take the startup company and identify the Competitors (who else is doing same), 
       Negative Reviews (what users hate), Lawsuits (any legal problems), Market Risks (why this startup can fail).
       This tool does NOT search for the startup again, it searches for risks FOR the same startup.
       Input: startup name like 'Perplexity AI' or startup info from Agent 1.
    """
    
    # Step 1: Search for RISKS only, not the startup info
    search_queries = [
        f"{query} competitors alternative",
        f"{query} negative reviews complaints",
        f"{query} lawsuits legal issues copyright",
        f"{query} market risks challenges why failing",
        f"{query} vs Google vs OpenAI comparison"
    ]
    
    all_urls = []
    for q in search_queries:
        results = tavily.search(query=q, max_results=2, search_depth="advanced")
        for r in results['results']:
            all_urls.append(r['url'])
    
    # Remove duplicates, keep top 5
    all_urls = list(dict.fromkeys(all_urls))[:5]

    # Step 2: Scrape all risk urls in parallel
    def scrape(url):
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded) or ""
            return f"URL: {url}\nCONTENT: {text[:4000]}"
        except:
            return f"URL: {url}\nCONTENT: Failed"

    with ThreadPoolExecutor(max_workers=5) as executor:
        contents = list(executor.map(scrape, all_urls))

    final_output = "\n----\n".join(contents)
    
    # Step 3: Return structured format for Agent 2
    return f"""
    STARTUP FOR RISK ANALYSIS: {query}

    RAW RISK DATA:
    {final_output}

    INSTRUCTION: From above raw data, extract and return in this format:
    - Competitors (who else is doing same):
    - Negative Reviews (what users hate):
    - Lawsuits (any legal problems):
    - Market Risks (why this startup can fail):
    """
