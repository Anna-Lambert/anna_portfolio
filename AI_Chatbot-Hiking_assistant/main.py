from langgraph.graph import StateGraph, MessagesState, START
from langchain.chat_models import init_chat_model
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage,  HumanMessage

from dotenv import load_dotenv
import json
import requests
import os

from .prompt import return_instructions
from .weather_tools import  get_current_temperature, get_weather_alerts, get_next_rain, get_next_wind 
from .hiking_tools import search_hiking_spots
from .fwi_tools import get_fire_weather_forecast
from utils.logger import get_logger

import sys
sys.path.append('../../05_src/')

_logs = get_logger(__name__)
load_dotenv(".env")
load_dotenv(".secrets")


chat_agent = init_chat_model("gpt-4o-mini", 
                      model_provider="openai",
                      base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
                      default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')},
                      )


tools = [
    search_hiking_spots,
    get_fire_weather_forecast,
    get_current_temperature,
    get_weather_alerts,
    get_next_rain,
    get_next_wind
]

instructions = return_instructions()



# @traceable(run_type="llm")
def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    response = chat_agent.bind_tools(tools).invoke( [SystemMessage(content=instructions)] + state["messages"])
    return {
        "messages": [response]
    }

def get_graph():
    
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    graph = builder.compile()
    return graph
