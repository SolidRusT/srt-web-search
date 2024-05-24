from duckduckgo_search import DDGS
from utils import get_website_content_from_url
from model import model_selected, get_context_by_model

def search_web(search_query: str):
    """
    Search the web for information.
    Args:
        search_query (str): Search query to search for.
    """
    results = DDGS().text(search_query, region='wt-wt', safesearch='off', timelimit='y', max_results=3)
    result_string = ''
    for res in results:
        web_info = get_website_content_from_url(res['href'])
        if web_info != "":
            result_string += web_info

    res = result_string.strip()
    return "Based on the following results, Summarize and answer the previous user query:\nResults:\n\n" + res[:get_context_by_model(model_selected)]