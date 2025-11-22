import json
from mcp import Tool
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionUserMessageParam,
)
from llm.openai_cli import OpenAIClient
from mcp_cli import McpClient


class BaseAgent:
    def __init__(self):
        self.messages: list[ChatCompletionMessageParam] = []
        self.client = OpenAIClient()

    async def initialize(self, prompt: str | None):
        self.mcp_client = McpClient()
        await self.mcp_client.initialize()
        self.tool_list = await self.mcp_client.get_all_tool_list()
        if prompt is not None:
            include = {"name", "inputSchema", "description"}
            tool_list_str = json.dumps(
                [tool.model_dump_json(include=include) for tool in self.tool_list],
                ensure_ascii=False,
            )
            # print(f"tool_list_str: {tool_list_str}")
            self.messages.append(
                ChatCompletionSystemMessageParam(
                    role="system", content=f"{prompt}\n{tool_list_str}"
                )
            )

    async def input(self, input_str: str) -> str | None:
        self.messages.append(
            ChatCompletionUserMessageParam(role="user", content=input_str)
        )
        print(f"input_str:  {input_str}")
        result = await self.client.achat(self.messages)
        self.messages.append(
            ChatCompletionAssistantMessageParam(
                role="assistant", content=result.content
            )
        )
        print(f"result:  {result.content}")
        print("-------------------------------")
        # return result.content
        return await self.result_handle(result.content)

    async def result_handle(self, result: str | None):
        if result is None:
            return
        
        # 尝试从字符串中提取所有 JSON
        json_list = self._extract_all_json(result)
        if json_list:
            try:
                results = []
                # 处理所有提取到的 JSON
                for idx, json_str in enumerate(json_list, 1):
                    try:
                        payload = json.loads(json_str)
                        name = payload.get("name")
                        # 兼容 "input" 和 "arguments" 两种字段名
                        params = payload.get("input") or payload.get("arguments")
                        
                        if not name:
                            print(f"⚠️  第 {idx} 个工具调用缺少 name")
                            continue
                        
                        print(f"🔧 调用工具 [{idx}/{len(json_list)}]: {name}")
                        print(f"📝 参数: {params}")
                        mcp_result = await self.mcp_client.call_tool(name, params)
                        print(f"✅ 工具结果: {mcp_result}")
                        results.append(f"Tool {idx} ({name}): {mcp_result}")
                    except Exception as e:
                        print(f"❌ 第 {idx} 个工具调用失败: {e}")
                        results.append(f"Tool {idx} error: {e}")
                
                # 将所有工具结果返回给 LLM 继续处理
                if results:
                    combined_result = "\n\n".join(results)
                    return await self.input(f"tool results:\n{combined_result}")
                else:
                    return result
            except Exception as e:
                print(f"❌ 处理工具调用失败: {e}")
                return result
        else:
            # 没有找到 JSON，直接返回文本结果
            return result

    def _extract_all_json(self, text: str) -> list[str]:
        """从文本中提取所有 JSON 字符串，支持多种格式和任意嵌套层级"""
        import re
        
        json_list = []
        
        # 1. 提取所有 ```json ... ``` 格式
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        for block in json_blocks:
            try:
                json.loads(block)
                json_list.append(block)
            except:
                pass
        
        # 2. 提取所有 ``` ... ``` 格式（无 json 标记）
        if not json_list:
            code_blocks = re.findall(r'```\s*(.*?)\s*```', text, re.DOTALL)
            for block in code_blocks:
                try:
                    json.loads(block)
                    json_list.append(block)
                except:
                    pass
        
        # 3. 如果没有代码块，尝试提取所有裸 JSON（支持任意嵌套）
        if not json_list:
            json_list = self._extract_json_objects(text)
        
        # 4. 如果还是没有，尝试整个文本是否是 JSON
        if not json_list:
            try:
                json.loads(text.strip())
                json_list.append(text.strip())
            except:
                pass
        
        return json_list
    
    def _extract_json_objects(self, text: str) -> list[str]:
        """使用括号匹配算法提取所有完整的 JSON 对象"""
        json_list = []
        i = 0
        
        while i < len(text):
            # 找到下一个 {
            if text[i] == '{':
                # 使用栈来匹配括号
                stack = []
                start = i
                j = i
                in_string = False
                escape = False
                
                while j < len(text):
                    char = text[j]
                    
                    # 处理字符串内的内容（忽略字符串内的括号）
                    if char == '"' and not escape:
                        in_string = not in_string
                    elif char == '\\' and not escape:
                        escape = True
                        j += 1
                        continue
                    
                    if not in_string:
                        if char == '{':
                            stack.append('{')
                        elif char == '}':
                            if stack:
                                stack.pop()
                                # 栈为空说明找到了完整的 JSON 对象
                                if not stack:
                                    json_str = text[start:j+1]
                                    try:
                                        json.loads(json_str)
                                        json_list.append(json_str)
                                        i = j + 1
                                        break
                                    except:
                                        # 不是有效的 JSON，继续查找
                                        pass
                    
                    escape = False
                    j += 1
                
                # 如果没有找到匹配的 }，或者解析失败，移动到下一个字符
                if j >= len(text) or stack:
                    i += 1
            else:
                i += 1
        
        return json_list
    
    def _extract_json(self, text: str) -> str | None:
        """从文本中提取第一个 JSON 字符串（向后兼容）"""
        json_list = self._extract_all_json(text)
        return json_list[0] if json_list else None
    
    def _is_json(self, text: str) -> bool:
        try:
            json.loads(text.replace("```json", "").replace("```", ""))
            return True
        except ValueError:
            return False

    def parse_json(self, text: str) -> dict:
        return json.loads(text.replace("```json", "").replace("```", ""))
