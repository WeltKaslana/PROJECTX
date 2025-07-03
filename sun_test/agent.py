# 引⼊JSON依赖包
from pydantic import BaseModel,Field,model_validator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
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

class Project(BaseModel):
    name: str = Field(..., description="可能想要买的商品的名称，只用一个词描述想要的商品，如果商品有多个，请列出商品名并用|分隔")
    description: str = Field(..., description="对于每个想要买的商品的描述，用|分隔")

# 实例化解析器、提示词模板
parser = PydanticOutputParser(pydantic_object=Project)
# 注意，提示词模板中需要部分格式化解析器的格式要求format_instructions 
prompt = PromptTemplate(
    template="回答⽤户的查询，查询出的商品名是关于日常商品的，如果结果有多个请用|分隔,商品描述如果有多个也请用|分隔.\n{format_instructions}\n{query}",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
chain = prompt | llm | parser
res = chain.invoke({"query": "我心情不好"})
pro = res.name.split("|")
print("商品名称：",res.name.split("|"))
print("商品描述：",res.description.split("|"))

# for name in pro:
#     print(llm.invoke(f"你能浏览淘宝的网页吗？请帮我在淘宝上搜索{name}，并告诉我它的链接。"))