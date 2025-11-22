import asyncio
import datetime
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.models.google.gemini import Gemini
# from agno.models.ollama.chat import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from agno.tools.email import EmailTools

from c_email_tools import CEmailTools

receiver_email = "<receiver_email>"
sender_email = "<sender_email>"
sender_name = "<sender_name>"
sender_passkey = "<sender_passkey>"

# ************* Create Agent *************
agno_agent = Agent(
    name="Agno Agent",
    
    # 方法1: 使用 system_message 直接设置完整的系统消息（推荐）
    # system_message=prompt,

    
    # 方法2: 使用结构化参数（会自动构建系统消息）
    # description="你是一个智能助手",  # Agent 描述，添加到系统消息开头
    instructions=[  # 指令列表
        "仔细分析用户问题",
        "逐步推理",
        "使用中文回答"
    ],
    # expected_output="清晰、完整、逻辑性强的回答",  # 期望的输出格式
    # additional_context="当前时间信息会自动添加",  # 额外上下文
    
    model=Gemini(id="gemini-2.5-flash", api_key="AIzaSyDesxyb0ruLlkHSo7e0OjVy83kPZM9eXd4"),
    # model=Claude(id="claude-sonnet-4-5"),
    
    # Add a database to the Agent
    # db=SqliteDb(db_file="agno.db"),
    
    # Add the Agno MCP server to the Agent
    tools=[
        # MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")
        # HackerNewsTools()
        ReasoningTools(),
        CEmailTools(
            sender_smtp_server="smtp.qq.com",
            sender_smtp_port=587,
            sender_name="zhao112077@foxmail.com",
            sender_email="zhao112077@foxmail.com",
            sender_passkey="zjrlzjydadnkbfge",
            receiver_email="zhaojiankan@gmail.com",
        ),
        DuckDuckGoTools(),
        #  EmailTools(
        #                 receiver_email=receiver_email,
        #     sender_email=sender_email,
        #     sender_name=sender_name,
        #     sender_passkey=sender_passkey,
        #     enable_email_user=True,
        #  ),
    ],
    
    # 上下文增强选项
    add_datetime_to_context=True,  # 自动添加当前时间到上下文
    # add_location_to_context=True,  # 添加位置信息
    # timezone_identifier="Asia/Shanghai",  # 设置时区
    
    # Add the previous session history to the context
    # add_history_to_context=True,
    # markdown=True,  # 启用 Markdown 格式化
    debug_mode=True,
)

# ************* 交互式问答 *************
# 方法1: 使用 Agno 内置的异步 CLI (推荐，支持 MCP 工具)
async def main():
    """使用 Agno 内置的交互式 CLI"""
    await agno_agent.acli_app(
        stream=True,        # 是否流式输出
        markdown=True,      # 是否使用 markdown 格式
        exit_on=["exit", "quit", "bye", "退出"]  # 退出命令
    )

if __name__ == "__main__":
    asyncio.run(main())


# 方法2: 如果不使用 MCP 工具，可以用同步版本
# if __name__ == "__main__":
#     agno_agent.cli_app(
#         user="你",
#         emoji="🧑", 
#         stream=True,
#         markdown=True,
#         exit_on=["exit", "quit", "bye", "退出"]
#     )


# ************* Create AgentOS (备用方案) *************
# agent_os = AgentOS(agents=[agno_agent])
# # Get the FastAPI app for the AgentOS
# app = agent_os.get_app()

# ************* Run AgentOS *************
# if __name__ == "__main__":
#     agent_os.serve(app="agno_main:app", reload=True)