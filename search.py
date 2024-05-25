import abc
import json
import logging
from duckduckgo_search import DDGS
from trafilatura import fetch_url, extract
from llama_cpp_agent import LlamaCppAgent, MessagesFormatterType
from llama_cpp_agent.providers.provider_base import LlmProvider


class WebCrawler(abc.ABC):
    @abc.abstractmethod
    def get_website_content_from_url(self, url: str):
        """Get the website content from an url."""
        pass


class WebSearchProvider(abc.ABC):
    @abc.abstractmethod
    def search_web(self, query: str):
        """Searches the web and returns a list of urls of the result"""
        pass


class DDGWebSearchProvider(WebSearchProvider):

    def search_web(self, search_query: str):
        results = DDGS().text(
            search_query, region="wt-wt", safesearch="off", max_results=4
        )
        return [res["href"] for res in results]


class TrafilaturaWebCrawler(WebCrawler):
    def get_website_content_from_url(self, url: str) -> str:
        """
        Get website content from a URL using Trafilatura for improved content extraction and filtering.

        Args:
            url (str): URL to get website content from.

        Returns:
            str: Extracted content including title, main text, and tables.
        """
        try:
            downloaded = fetch_url(url)
            result = extract(
                downloaded,
                include_formatting=True,
                include_links=True,
                output_format="json",
                url=url,
            )
            if result:
                result = json.loads(result)
                return f'=========== Website Title: {result["title"]} ===========\n\n=========== Website URL: {url} ===========\n\n=========== Website Content ===========\n\n{result["raw_text"]}\n\n=========== Website Content End ===========\n\n'
            else:
                return ""
        except Exception as e:
            logging.error(f"Error extracting content from {url}: {e}")
            return f"An error occurred: {str(e)}"


class WebSearchTool:

    def __init__(
        self,
        llm_provider: LlmProvider,
        message_formatter_type: MessagesFormatterType,
        web_crawler: WebCrawler = None,
        web_search_provider: WebSearchProvider = None,
    ):
        self.summarising_agent = LlamaCppAgent(
            llm_provider,
            debug_output=True,
            system_prompt="You are a text summarization and information extraction specialist and you are able to summarize and filter out information relevant to a specific query.",
            predefined_messages_formatter_type=message_formatter_type,
        )
        if web_crawler is None:
            self.web_crawler = TrafilaturaWebCrawler()
        else:
            self.web_crawler = web_crawler

        if web_search_provider is None:
            self.web_search_provider = DDGWebSearchProvider()
        else:
            self.web_search_provider = web_search_provider

    def search_web(self, search_query: str):
        """
        Search the web for information.
        Args:
            search_query (str): Search query to search for.
        """
        results = self.web_search_provider.search_web(search_query)
        result_string = ""
        for res in results:
            web_info = self.web_crawler.get_website_content_from_url(res)
            if web_info != "":
                web_info = self.summarising_agent.get_chat_response(
                    f"Please summarize the following Website content and extract relevant information to this query:'{search_query}'.\n\n"
                    + web_info,
                    add_response_to_chat_history=False,
                    add_message_to_chat_history=False,
                )
                result_string += web_info

        res = result_string.strip()
        return (
            "Based on the following results, answer the previous user query:\nResults:\n\n"
            + res
        )

    def get_tool(self):
        return self.search_web
