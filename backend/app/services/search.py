import logging
import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from readability import Document
from backend.app.models.schemas import Source

log = logging.getLogger(__name__)

class SearchService:
    def search(self, query: str, max_results: int = 5) -> list[Source]:
        try:
            with DDGS() as ddgs:
                rows = list(ddgs.text(query, max_results=max_results))
            return [Source(title=r.get("title", ""), url=r.get("href", ""), snippet=r.get("body", "")) for r in rows]
        except Exception as exc:
            log.exception("Search failed: %s", exc)
            return []

    async def fetch_page_text(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "AI Voice Assistant/1.0"})
            response.raise_for_status()
        doc = Document(response.text)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        return " ".join(soup.get_text(" ", strip=True).split())[:12000]
