from typing import Optional

from agno.agent import Agent
from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openai import OpenAIChat
from agno.tools.calculator import CalculatorTools
from agno.models.google.gemini import Gemini

model = Gemini(id="gemini-2.5-flash", api_key="AIzaSyDesxyb0ruLlkHSo7e0OjVy83kPZM9eXd4")

evaluation = AccuracyEval(
    name="Calculator Evaluation",
    model=model,
    agent=Agent(
        model=model,
        tools=[CalculatorTools()],
    ),
    input="What is 10*5 then to the power of 2? do it step by step",
    expected_output="2500",
    additional_guidelines="Agent output should include the steps and the final answer.",
    num_iterations=3,
)

result: Optional[AccuracyResult] = evaluation.run(print_results=True)
assert result is not None and result.avg_score >= 8