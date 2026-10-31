from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from dotenv import load_dotenv
load_dotenv()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent)) # Adding the project root to the system path

from tools.calculator import calculate
from tools.exchange_rate import get_exchange_rate
from tools.weather import get_weather

@tool
def invoke_calculate(operation: str, a: float, b: float):
    """Performs basic arithmetic calculations (add, subtract, multiply, divide, mod and power) on two numbers."""
    return calculate(operation, a, b)

@tool
def invoke_exchange_rate(base: str, target: str):
    """Gets the live currency conversion or exchange rate between a base currency and a target currency."""
    return get_exchange_rate(base, target)

@tool
def invoke_weather(city: str):
    """Gets the current weather information for a specific city name."""
    return get_weather(city)


TOOL_MAP = {
    "invoke_calculate": invoke_calculate,
    "invoke_exchange_rate": invoke_exchange_rate,
    "invoke_weather": invoke_weather,
}

def get_response(query: str, api_key: str) -> dict:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=api_key
    )

    model_with_tools = model.bind_tools([invoke_calculate, invoke_exchange_rate, invoke_weather])

    response = model_with_tools.invoke(query)
    final_tool_call_result = None
    tool_results = []

    if response.tool_calls:
        result = None
        tool_invoke_conversation = []
        
        for tool_call in response.tool_calls:
            
            id = tool_call["id"]
            name = tool_call["name"]
            args = tool_call["args"]

            if name in TOOL_MAP:
                result = TOOL_MAP[name].invoke(args)
            else:
                result = f"Error: Tool {name} not found."

            if hasattr(result, "item"):
                result = result.item()
            
            tool_results.append({
                "id": id,
                "name": name,
                "arguments": args,
                "result": result
            })
            
            tool_invoke_conversation.append(
                ToolMessage(
                    content = str(result),
                    tool_call_id = id,
                    name = name
                )
            )
        
        tool_outputs_str = ", ".join(str(conv.content) for conv in tool_invoke_conversation)
        final_tool_call_result = model.invoke(f'{query}\nTool Call Result = {tool_outputs_str}. Form a structured answer for it.').content

    return dict({
        "content": final_tool_call_result if response.tool_calls else response.content,
        "tool_calls": response.tool_calls,
        "tool_results": tool_results
    })