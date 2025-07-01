import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langsmith import Client
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
print("Hello from hellochain!")
key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")

prompt_key = os.getenv("LANGSMITH_API_KEY")
prompt_base = os.getenv("LANGSMITH_ENDPOINT")
prompt_test = os.getenv("LANGSMITH_TEST")

print(f"KEY: {key}")
model = ChatDeepSeek(
    model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
    temperature=0,
    api_key=key,
    api_base=base
)

# res = model.invoke("introduce yourself in Chinese briefly")
# print(res)

print(f"Prompt Key: {prompt_key}")
client = Client(api_key=prompt_key)