import json
import asyncio
from mcp import ClientSession, StdioServerParameters, Tool
from mcp.client.stdio import stdio_client


class McpClient:
    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}
        self._pending = 0
        self._ready = asyncio.Event()
        self.tool_list: dict[str, list[Tool]] = {}

    async def initialize(self):
        with open("mcp.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        self._pending = len(servers)

        for name, cfg in servers.items():
            cmd, args = cfg.get("command"), cfg.get("args", [])
            print(f"🔌 连接 MCP server: {name} → {cmd} {' '.join(args)}")
            asyncio.create_task(
                self._connect_loop(name, StdioServerParameters(command=cmd, args=args))
            )

        await self._ready.wait()
        print("✅ 所有 MCP Server 已准备就绪")

    async def _connect_loop(self, name: str, config: StdioServerParameters):
        while True:
            try:
                async with stdio_client(config) as (reader, writer):
                    async with ClientSession(reader, writer) as session:
                        await session.initialize()
                        self.sessions[name] = session
                        tool_list = (await session.list_tools()).tools
                        self.tool_list[name] = tool_list
                        print(f"🔧 {name}: {[tool.name for tool in tool_list]}")
                        if self._pending > 0:
                            self._pending -= 1
                            if self._pending == 0:
                                self._ready.set()
                        try:
                            await asyncio.Future()
                        except asyncio.CancelledError:
                            print(f"MCP session {name} cancelled")
                            break
                        finally:
                            print(f"MCP session {name} finally")
                            self.sessions.pop(name, None)
            except Exception as e:
                print(f"⚠️ MCP session {name} error: {e}")
                await asyncio.sleep(1)

    async def get_all_tool_list(self):
        tool_list: list[Tool] = []
        for session in self.sessions.values():
            if session:
                try:
                    tools = await session.list_tools()
                    tool_list.extend(tools.tools)
                except Exception as e:
                    print(f"获取工具列表失败: {e}")
        return tool_list

    async def call_tool(self, tool_name: str, params: dict):
        for name, session in self.sessions.items():
            try:
                for tool in self.tool_list[name]:
                    if tool.name == tool_name:
                        return await session.call_tool(tool_name, params)
            except Exception as e:
                print(f"调用工具 {tool_name} 失败: {e}")
                return f"call tool {tool_name} error: {e}"
        else:
            print(f"工具 {tool_name} 不存在")
            return f"tool {tool_name} not found"
