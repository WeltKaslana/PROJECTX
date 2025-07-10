import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek

load_dotenv()

key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")

llm = ChatDeepSeek(
    model='deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
    temperature=0.3,
    api_key=key,
    api_base=base,
    timeout=180,
)

router_chain = (
    PromptTemplate.from_template("""
        1.你和另一人一同完成商品推荐的工作
        2.假设你可以通过关键词进行商品搜索
        3.另一人对你搜索得到的商品通过商品的名字、价格、销量等进行筛选推荐
        请根据下面用户的问题，将用户的问题分类为'1'或'0'。
        若用户的问题需要你重新进行关键词搜索，则分类为'1'。
        若不需要你重新搜索，直接提交给另一人进行筛选推荐，则分类为'0'。
        只需要回复'0'或者'1'。
        <question>
        {question}
        </question>
        分类结果：""") | llm | StrOutputParser()
)
question= "有没有金色的"
result = router_chain.invoke({"question": question})
print(f"{question}\n问题类型：{result}")
