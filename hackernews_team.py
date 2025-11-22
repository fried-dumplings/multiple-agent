from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper4k import Newspaper4kTools
from pydantic import BaseModel
from agno.models.google.gemini import Gemini

model = Gemini(id="gemini-2.5-flash", api_key="AIzaSyDesxyb0ruLlkHSo7e0OjVy83kPZM9eXd4")

class Article(BaseModel):
    title: str
    summary: str
    reference_links: List[str]

hn_researcher = Agent(
    name="HackerNews 研究员",
    model=model,
    role="从 hackernews 获取热门故事。",
    tools=[HackerNewsTools()],
)

web_searcher = Agent(
    name="网络搜索员",
    model=model,
    role="在网络上搜索有关主题的信息",
    tools=[DuckDuckGoTools()],
    add_datetime_to_context=True,
)

article_reader = Agent(
    name="文章阅读器",
    role="从 URL 读取文章。",
    tools=[Newspaper4kTools()],
)


hn_team = Team(
    name="HackerNews Team",
    model=model,
    members=[hn_researcher, web_searcher, article_reader],
    instructions=[
        "首先，在 hackernews 上搜索用户询问的内容。",
        "然后，让文章阅读器读取这些故事的链接以获取更多信息。",
        "重要提示：你必须向文章阅读器提供要阅读的链接。",
        "接下来，让网络搜索器搜索每个故事以获取更多信息。",
        "最后，按以下格式提供一个深思熟虑且引人入胜的摘要：",
        "- 标题：[文章标题]",
        "- 摘要：[详细摘要]",
        "- 参考链接：[URL 列表]",
    ],
    # ❌ Gemini 不支持在使用工具时同时使用 output_schema
    # output_schema=Article,
    markdown=True,
    show_members_responses=True,
    debug_mode=True,
)

hn_team.print_response("写一篇关于 hackernews 上前 2 个热门故事的文章")