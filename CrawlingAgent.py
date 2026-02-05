import requests
from bs4 import BeautifulSoup
from agno.agent import Agent
from agno.tools import tool
from AgentTools.crawlertools import read_webpage_content
from DB.db import insert_article
# ================================================================================
# AGNO TOOL WRAPPERS (THIS IS WHAT AGNO NEEDS)
# ================================================================================


from agno.models.ollama.chat import Ollama

from Instructions.crawlingAgentInstruction import crawler_instructions
from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools

import json
import httpx

from agno.agent import Agent

def get_top_hackernews_stories(num_stories: int = 10) -> str:
    """
    Use this function to get top stories from Hacker News.

    Args:
        num_stories (int): Number of stories to return. Defaults to 10.

    Returns:
        str: JSON string of top stories.
    """

    # Fetch top story IDs
    response = httpx.get('https://hacker-news.firebaseio.com/v0/topstories.json')
    story_ids = response.json()

    # Fetch story details
    stories = []
    for story_id in story_ids[:num_stories]:
        story_response = httpx.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
        story = story_response.json()
        if "text" in story:
            story.pop("text", None)
        stories.append(story)
    return json.dumps(stories)

ANTHROPIC_API_KEY = "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"
from agno.models.anthropic import  Claude

anthropic_model = Claude(
    id="claude-3-haiku-20240307",
    api_key=ANTHROPIC_API_KEY,
    max_tokens=3000
)

ollama_model = Ollama(
    id="qwen2.5:7b-instruct",
    host="http://localhost:11434"
)



agent = Agent(
    model= ollama_model ,#anthropic_model,
    tools=[read_webpage_content],
    instructions="""
    You are a Crawling Agent that fetches and processes web content. use the tools to get the html tags , 
    you must obey al the steps mentioned below
    Do not analyze anything.
    mandatory steps
    1. You must call read_webpage_content and wait for its result then only go to the next step. 
    2. for the webpage extract news articles with title , full text content , snippet (first 200 characters of the content) , publication date in ISO format.
    3.Identify the industry  of the article based on the content. The industries are banking and finance ,Retail ,healthcare,manufacturing,Automotive , and Others.
    4. create a json structure for response  with the following format 
    
    {
        "url": "https://example.com/article1",
        "source": "example.com",
        "title": "Article Title ",
        "content": "Full text content of the article..."
        "snippet": "First 200 characters of the article content..."
        "industry": "Industry category of the article like banking and finance ,Retail ,healthcare,manufacturing,Automotive , and Others..."
        "published_at": "Publication date in ISO format",
        "created_at": "Current date in ISO format",
    },
    5. return stricly only the json structure as response.
    """,
    markdown=True,
)
res = agent.print_response("read the webpage  https://www.indiatoday.in/cities/story/ghaziabad-suicide-horror-jump-off-building-korean-gaming-app-addiction-2862740-2026-02-04 and extract the news  ", stream=True)
print("&" *100)
print(res)