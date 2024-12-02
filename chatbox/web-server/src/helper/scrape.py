from typing import Callable, Dict, List, Literal, Optional, Any, cast
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from llama_index.langchain_helpers.text_splitter import TextSplitter
import unicodedata


def nfkc_normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


class ReadabilityWebPageReader(BaseReader):

    def __init__(
        self,
        proxy: Optional[str] = None,
        wait_until: Optional[
            Literal["commit", "domcontentloaded", "load", "networkidle"]
        ] = "domcontentloaded",
        text_splitter: Optional[TextSplitter] = None,
        normalize: Optional[Callable[[str], str]] = nfkc_normalize,
    ) -> None:
        self._launch_options = {
            "headless": True,
        }
        self._wait_until = wait_until
        if proxy:
            self._launch_options["proxy"] = {
                "server": proxy,
            }
        self._text_splitter = text_splitter
        self._normalize = normalize

    def load_data(self, url: str) -> List[Document]:
        """render and load data content from url.

        Args:
            url (str): URL to scrape.

        Returns:
            List[Document]: List of documents.

        """
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                **self._launch_options)

            article = self.scrape_page(
                browser,
                url,
            )

            browser.close()
            document = Document(text=article)
            document.metadata["website"] = url
            return [document]

    def scrape_page(
        self,
        browser: Any,
        url: str,
    ) -> Dict[str, str]:
        """Scrape a single article url.

        Args:
            browser (Any): a Playwright Chromium browser.
            url (str): URL of the article to scrape.

        """
        from playwright.sync_api._generated import Browser

        browser = cast(Browser, browser)
        page = browser.new_page(
            ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
        page.set_default_timeout(120000)

        page.goto(url)

        page.wait_for_load_state(state='load')

        scraped_content = page.content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(scraped_content, 'html.parser')
        page.close()

        return soup.get_text()
