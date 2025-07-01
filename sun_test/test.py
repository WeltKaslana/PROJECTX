import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()
print("Hello from hellochain!")
key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")

prompt_key = os.getenv("LANGSMITH_API_KEY")
prompt_base = os.getenv("LANGSMITH_ENDPOINT")
prompt_test = os.getenv("LANGSMITH_TEST")

# print(f"KEY: {key}")
# model = ChatDeepSeek(
#     model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
#     temperature=0,
#     api_key=key,
#     api_base=base
# )
# res = model.invoke("introduce yourself in Chinese briefly")
# print(res)

from langsmith import Client
from langchain_core.messages import HumanMessage, AIMessage
print(f"Prompt Key: {prompt_key}")
client = Client(api_key=prompt_key)
# prompt1 = client.pull_prompt("test1")
prompt1 = client.pull_prompt("volcharachain/openai-movies-agent")
client.push_prompt("test2", object=prompt1)
print("Push Over!")
prompt1 = prompt1.invoke({
    "tool_names": "none",
    "input": "What is your favourite movie?",
    "chat_history": [HumanMessage(content="How are you?")],
    "agent_scratchpad": [HumanMessage(content="none")],
    })

print(f"Prompt Test: ")
print(prompt1)
