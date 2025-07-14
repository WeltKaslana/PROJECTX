# 引⼊JSON依赖包
from pydantic import BaseModel,Field,model_validator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_core.runnables import RunnableParallel
import os

# 使⽤DeepSeek模型
from dotenv import load_dotenv

load_dotenv()
# print("Hello from hellochain!")
key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")

llm = ChatDeepSeek(
    model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
    temperature=0,
    api_key=key,
    api_base=base,
    timeout=60,#增加请求超时限制
)
# 定义⼀个数据为Joke 的数据模型
# 必须要包含数据字段：铺垫（setup）、 抖包袱 punchline（ punchline）
class Joke(BaseModel):
    setup: str = Field(..., description="笑话中的铺垫问题，必须以？结尾")
    punchline: str = Field(..., description="笑话中回答铺垫问题的部分，通常是⼀种抖包袱⽅式回答铺垫问题，例如谐⾳、会错意等")
# 实例化解析器、提示词模板
parser = PydanticOutputParser(pydantic_object=Joke)
# 注意，提示词模板中需要部分格式化解析器的格式要求format_instructions 
prompt = PromptTemplate(
template="回答⽤户的查询.\n{format_instructions}\n{query}",
input_variables=["query"],
partial_variables={"format_instructions": parser.get_format_instructions()}
)
# print(parser.get_format_instructions())
# 使⽤LCEL语法组合⼀个简单的链
chain = prompt | llm | parser
# for str in chain.stream({"query": "给我讲个有关程序员的笑话"}):
#     print(str)
chain2 = prompt | llm | parser

ch = {"1": chain, "2": chain2}

# example
# ch = {}
# for i in ...:
#     ch[i.name] = chain

chain3 = RunnableParallel(**ch)
print(chain3.invoke({"query": "给我讲个有关程序员的笑话"}))