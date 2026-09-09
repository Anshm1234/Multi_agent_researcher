from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str)->str:
    """Search the web for recent and reliable information on a topic .Retunrs Titles,Url's and Snippets"""
    results=tavily.search(query=query,max_results=5)

    out=[]

    for r in results['results']:
        out.append(
            f"'Title' : {r['title']}\n\nURL: {r['url']}\n\nSnippet: {r['content'][:300]}\n\n"
        )
    return"\n---------------------\n".join(out)


@tool
def extract_content(url: str)->str:
    "Scrape and retusn clean text contetn from a given url for deeper reading"
    try:
        resp=requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup=BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()
        return soup.get_text(separator=" ",strip=True)[:3000]
    except Exception as e:
        return f"could not scrape url: {str(e)}"