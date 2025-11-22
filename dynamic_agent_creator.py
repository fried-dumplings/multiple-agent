"""
动态 Agent 创建器示例
演示如何让 LLM 根据任务需求动态创建和使用专门的 Agent
"""
import asyncio
from typing import List, Dict, Any
from agno.agent import Agent
from agno.team import Team
from agno.models.google.gemini import Gemini
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.calculator import CalculatorTools
from c_email_tools import CEmailTools


# ============= 方案 1: 主 Agent 使用自定义 Tool 动态创建子 Agent =============
class DynamicAgentCreator:
    """动态 Agent 创建器，可以根据任务需求创建专门的 Agent"""
    
    def __init__(self, model):
        self.model = model
        self.created_agents: Dict[str, Agent] = {}
        
    def create_agent_for_task(
        self, 
        task_type: str,
        agent_name: str,
        role: str,
        instructions: List[str] = None
    ) -> Agent:
        """
        根据任务类型动态创建 Agent
        
        Args:
            task_type: 任务类型 (research/calculation/email/writing)
            agent_name: Agent 名称
            role: Agent 角色描述
            instructions: 自定义指令列表
        """
        # 根据任务类型选择合适的工具
        tools_map = {
            "research": [DuckDuckGoTools(), ReasoningTools()],
            "calculation": [CalculatorTools(), ReasoningTools()],
            "email": [
                CEmailTools(
                    sender_smtp_server="smtp.qq.com",
                    sender_smtp_port=587,
                    sender_name="zhao112077@foxmail.com",
                    sender_email="zhao112077@foxmail.com",
                    sender_passkey="zjrlzjydadnkbfge",
                    receiver_email="zhaojiankan@gmail.com",
                )
            ],
            "writing": [ReasoningTools()],
            "general": [DuckDuckGoTools(), ReasoningTools(), CalculatorTools()],
        }
        
        # 创建新 Agent
        agent = Agent(
            name=agent_name,
            model=self.model,
            role=role,
            instructions=instructions or [
                "认真分析任务需求",
                "使用合适的工具完成任务",
                "提供清晰、完整的结果"
            ],
            tools=tools_map.get(task_type, tools_map["general"]),
            add_datetime_to_context=True,
            markdown=True,
        )
        
        # 保存创建的 Agent
        self.created_agents[agent_name] = agent
        print(f"✅ 已创建 Agent: {agent_name} (类型: {task_type})")
        
        return agent
    
    async def execute_with_agent(self, agent_name: str, task: str) -> str:
        """使用指定的 Agent 执行任务"""
        if agent_name not in self.created_agents:
            return f"❌ Agent '{agent_name}' 不存在"
        
        agent = self.created_agents[agent_name]
        response = await agent.arun(task)
        return response.content


# ============= 方案 2: 使用 Team 架构，主 Agent 协调多个动态子 Agent =============
async def demo_dynamic_agent_with_team():
    """演示使用 Team 架构动态创建和协调多个 Agent"""
    
    model = Gemini(id="gemini-2.5-flash", api_key="AIzaSyDesxyb0ruLlkHSo7e0OjVy83kPZM9eXd4")
    
    # 创建动态 Agent 创建器
    creator = DynamicAgentCreator(model)
    
    # 根据任务需求动态创建专门的 Agent
    research_agent = creator.create_agent_for_task(
        task_type="research",
        agent_name="研究员",
        role="负责在网络上搜索和研究信息",
        instructions=[
            "使用 DuckDuckGo 搜索相关信息",
            "分析搜索结果的可靠性",
            "提供详细的研究报告"
        ]
    )
    
    calc_agent = creator.create_agent_for_task(
        task_type="calculation",
        agent_name="计算专家",
        role="负责执行数学计算和数据分析",
        instructions=[
            "使用计算器工具执行精确计算",
            "展示计算步骤",
            "验证计算结果"
        ]
    )
    
    writer_agent = creator.create_agent_for_task(
        task_type="writing",
        agent_name="文案专家",
        role="负责撰写和整理内容",
        instructions=[
            "组织信息结构",
            "使用清晰的语言",
            "确保内容完整性"
        ]
    )
    
    # 创建 Team，让主 Agent 协调这些动态创建的子 Agent
    dynamic_team = Team(
        name="动态任务团队",
        model=model,
        members=[research_agent, calc_agent, writer_agent],
        instructions=[
            "分析用户任务，确定需要哪些专门的 Agent",
            "将任务分配给合适的团队成员",
            "研究员负责信息搜索",
            "计算专家负责数学计算",
            "文案专家负责内容整理和报告撰写",
            "整合所有结果，提供完整的答案"
        ],
        markdown=True,
        show_members_responses=True,
        debug_mode=True,
    )
    
    # 执行复杂任务
    task = """
    请帮我完成以下任务：
    1. 搜索 "2024年人工智能发展趋势"
    2. 计算如果投资10万元，年化收益率15%，5年后是多少钱
    3. 将以上信息整理成一份简短的报告
    """
    
    print("=" * 60)
    print("📋 任务:", task)
    print("=" * 60)
    
    response = dynamic_team.print_response(task)
    return response


# ============= 方案 3: 主 Agent 通过推理决定何时创建新 Agent =============
async def demo_agent_with_dynamic_creation():
    """演示单个主 Agent 根据需要动态创建和使用子 Agent"""
    
    model = Gemini(id="gemini-2.5-flash", api_key="AIzaSyDesxyb0ruLlkHSo7e0OjVy83kPZM9eXd4")
    
    # 创建主 Agent，具备创建其他 Agent 的能力
    master_agent = Agent(
        name="主控 Agent",
        model=model,
        description="我是一个智能任务协调器，能够根据任务需求动态创建和管理专门的子 Agent",
        instructions=[
            "仔细分析用户的任务需求",
            "判断是否需要创建专门的 Agent 来处理特定任务",
            "如需要，创建具有合适工具和指令的子 Agent",
            "协调子 Agent 完成任务",
            "整合结果并返回给用户",
            "使用中文回答"
        ],
        tools=[
            ReasoningTools(),  # 用于推理和决策
            DuckDuckGoTools(),
            CalculatorTools(),
        ],
        add_datetime_to_context=True,
        markdown=True,
        # debug_mode=True,
    )
    
    # 创建 Agent 创建器作为主 Agent 的辅助工具
    creator = DynamicAgentCreator(model)
    
    # 场景：用户提出复杂任务
    task = "我需要研究量子计算的最新进展，并计算如果量子计算提升效率100倍，对当前算力需求的影响"
    
    print("\n" + "=" * 60)
    print("📋 用户任务:", task)
    print("=" * 60)
    
    # 主 Agent 分析任务
    analysis_prompt = f"""
    任务: {task}
    
    请分析这个任务需要：
    1. 哪些专门的子 Agent（研究/计算/写作等）
    2. 每个 Agent 的具体职责
    3. 任务执行顺序
    
    根据分析，我将动态创建需要的 Agent。
    """
    
    response = await master_agent.arun(analysis_prompt)
    print("\n🤔 主 Agent 分析:\n", response.content)
    
    # 基于分析，动态创建需要的 Agent
    print("\n" + "=" * 60)
    print("🔧 开始动态创建专门的 Agent...")
    print("=" * 60)
    
    quantum_researcher = creator.create_agent_for_task(
        task_type="research",
        agent_name="量子计算研究员",
        role="专门研究量子计算相关信息",
        instructions=[
            "搜索量子计算的最新进展",
            "关注技术突破和应用场景",
            "提供详细的研究结果"
        ]
    )
    
    impact_calculator = creator.create_agent_for_task(
        task_type="calculation",
        agent_name="影响力计算专家",
        role="计算技术提升带来的影响",
        instructions=[
            "基于给定的数据进行计算",
            "分析效率提升的影响",
            "提供量化的结果"
        ]
    )
    
    # 执行任务
    print("\n" + "=" * 60)
    print("🚀 执行任务...")
    print("=" * 60)
    
    # 第一步：研究
    print("\n📚 步骤 1: 量子计算研究")
    research_result = await quantum_researcher.arun("搜索并总结量子计算在2024年的最新进展")
    print(research_result.content)
    
    # 第二步：计算
    print("\n🔢 步骤 2: 影响力计算")
    calc_result = await impact_calculator.arun(
        "假设当前全球AI训练需要100万GPU小时，如果量子计算提升效率100倍，计算所需的算力"
    )
    print(calc_result.content)
    
    # 第三步：主 Agent 整合结果
    print("\n📝 步骤 3: 结果整合")
    final_prompt = f"""
    请整合以下信息，给用户一个完整的答案：
    
    研究结果：
    {research_result.content}
    
    计算结果：
    {calc_result.content}
    """
    
    final_response = await master_agent.arun(final_prompt)
    print("\n" + "=" * 60)
    print("✅ 最终结果:")
    print("=" * 60)
    print(final_response.content)


# ============= 方案 4: 使用配置驱动的动态 Agent 工厂 =============
class AgentFactory:
    """Agent 工厂，支持基于配置动态创建 Agent"""
    
    @staticmethod
    def create_from_config(config: Dict[str, Any], model) -> Agent:
        """
        从配置字典创建 Agent
        
        Args:
            config: Agent 配置，包含 name, role, tools, instructions 等
            model: 使用的 LLM 模型
        """
        # 解析工具配置
        tools = []
        for tool_name in config.get("tools", []):
            if tool_name == "search":
                tools.append(DuckDuckGoTools())
            elif tool_name == "calculator":
                tools.append(CalculatorTools())
            elif tool_name == "reasoning":
                tools.append(ReasoningTools())
            # 可以继续添加更多工具...
        
        return Agent(
            name=config.get("name", "Dynamic Agent"),
            model=model,
            role=config.get("role", ""),
            instructions=config.get("instructions", []),
            tools=tools,
            add_datetime_to_context=config.get("add_datetime", True),
            markdown=config.get("markdown", True),
        )


async def demo_factory_pattern():
    """演示使用工厂模式动态创建 Agent"""
    
    model = Gemini(id="gemini-2.5-flash", api_key="AIzaSyDesxyb0ruLlkHSo7e0OjVy83kPZM9eXd4")
    
    # 定义不同任务的 Agent 配置
    agent_configs = [
        {
            "name": "数据分析师",
            "role": "分析数据并提供见解",
            "tools": ["calculator", "reasoning"],
            "instructions": [
                "仔细分析数据",
                "使用计算器进行精确计算",
                "提供数据驱动的见解"
            ]
        },
        {
            "name": "信息收集员",
            "role": "从网络收集最新信息",
            "tools": ["search", "reasoning"],
            "instructions": [
                "使用搜索引擎查找相关信息",
                "评估信息的可靠性",
                "整理和总结搜索结果"
            ]
        }
    ]
    
    # 动态创建 Agent
    agents = []
    for config in agent_configs:
        agent = AgentFactory.create_from_config(config, model)
        agents.append(agent)
        print(f"✅ 创建 Agent: {agent.name}")
    
    # 使用创建的 Agent
    task = "搜索并分析 Python 3.12 的新特性"
    print(f"\n📋 任务: {task}")
    
    # 信息收集
    search_result = await agents[1].arun(task)
    print(f"\n{agents[1].name} 的结果:")
    print(search_result.content)


# ============= 主函数 =============
async def main():
    """主函数：演示不同的动态 Agent 创建方案"""
    
    print("\n" + "=" * 60)
    print("🎯 Agno 框架 - 动态 Agent 创建演示")
    print("=" * 60)
    
    # 选择要演示的方案
    print("\n请选择演示方案:")
    print("1. Team 架构 - 动态创建多个协作 Agent")
    print("2. 主从架构 - 主 Agent 动态创建和管理子 Agent")
    print("3. 工厂模式 - 基于配置动态创建 Agent")
    print("4. 全部演示")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == "1":
        await demo_dynamic_agent_with_team()
    elif choice == "2":
        await demo_agent_with_dynamic_creation()
    elif choice == "3":
        await demo_factory_pattern()
    elif choice == "4":
        print("\n" + "=" * 60)
        print("方案 1: Team 架构")
        print("=" * 60)
        await demo_dynamic_agent_with_team()
        
        print("\n" + "=" * 60)
        print("方案 2: 主从架构")
        print("=" * 60)
        await demo_agent_with_dynamic_creation()
        
        print("\n" + "=" * 60)
        print("方案 3: 工厂模式")
        print("=" * 60)
        await demo_factory_pattern()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(main())

