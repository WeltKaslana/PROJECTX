# 引⼊JSON依赖包
from pydantic import BaseModel,Field,model_validator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
import os

# 使⽤DeepSeek模型
from dotenv import load_dotenv

# load_dotenv()
# # print("Hello from hellochain!")
# key = os.getenv("SILICONFLOW_API_KEY")
# base = os.getenv("SILICONFLOW_API_BASE")

# llm = ChatDeepSeek(
#     model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
#     temperature=0,
#     api_key=key,
#     api_base=base,
#     timeout=60,#增加请求超时限制
# )

async def add():
    global docs, loader
    async for doc in loader.alazy_load ():
        docs.append(doc)
    assert len(docs) == 1

async def temp():
    await add()
 
# import bs4
# from langchain_community.document_loaders import WebBaseLoader
# page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"
# loader = WebBaseLoader(web_paths=[page_url])
# docs =[]
# import asyncio
# asyncio.run(temp())
# doc = docs[0]
# print(f"{doc.metadata}\n")
# print(doc.page_content[:500].strip())

# import bs4
# from langchain_community.document_loaders import WebBaseLoader

# page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"

# loader = WebBaseLoader(web_paths=[page_url])
# docs = []
# #async for doc in loader.alazy_load():
# for doc in loader.load():
#     docs.append(doc)

# assert len(docs) == 1
# doc = docs[0]

# print(f"{doc.metadata}\n")
# print(doc.page_content[:500].strip())

from langchain_unstructured import UnstructuredLoader

page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"
loader = UnstructuredLoader(web_url=page_url)

docs = []
print(1)
#async for doc in loader.alazy_load():
for doc in loader.load():
    docs.append(doc)
print(2)   
print(f"{doc.metadata}\n")
print(doc.page_content[:500])