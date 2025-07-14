# 链的⾼级应⽤：使⽤LCEL来⾃定义路由链
# 导⼊所需的库
from langchain_core.output_parsers import StrOutputParser # 导⼊字符串输出解析器
from langchain_core.prompts import PromptTemplate # 导⼊提示模板
from langchain_deepseek import ChatDeepSeek # 导⼊DeepSeek聊天模型
from langchain_core.runnables import RunnableLambda # 导⼊可运⾏的Lambda函数
import os

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

#  创建分类链  - ⽤于确定问题类型
chain = (
 PromptTemplate.from_template("""根据下⾯的⽤户问题，将其分类为`LangChain`、`Anthropic` 或 `Other`,请只回复⼀个词作为答案。
    <question>
    {question}
    </question>
    分类结果：""") | llm | StrOutputParser()
 )
 # 创建Langchain 专家链 - 模拟Harrison Chase(LangChain 创始⼈)的回答⻛格
langchain_chain = PromptTemplate.from_template("""你将扮演以为`LangChain`专家，请以他的视⻆回答问题。\你的回答必须以“正如Harrison Chase 告诉我的”开头，否则你会收到惩罚。\
                                               请回答以下问题：
                                               问题：{question}
                                               回答：
""") | llm  # 将提示发送给DeepSeek模型
# 创建Anthropic 专家链 - 模拟Dario Amodei(Anthropic创始⼈)的回答⻛格
anthropic_chain = PromptTemplate.from_template("""
                                               你将扮演以为`Anthropic`专家，请以他的视⻆回
答问题。\
你的回答必须以“正如Dario Amodei 告诉我的”开头，否则你会收到惩罚。\
                                               请回答以下问题：
                                               问题：{question}
                                               回答：   """) | llm  # 将提示发送给DeepSeek模型
# 创建通⽤回答链 - ⽤于处理其他类型的问题
generic_chain = PromptTemplate.from_template("""
                                               你将扮演⼀位通⽤专家，请回答以下问题：\
                                               问题：{question}
                                               回答：""") | llm  # 将提示发送给DeepSeek模型
# ⾃定义路由函数 - 根据问题类型选择不同的回答链
def router(info):
    print(info)
    if "anthropic" in info["topic"].lower(): # 如果问题类型包含"anthropic"，则使⽤Anthropic专家链
        print("claude")
        return anthropic_chain
    elif "langchain" in info["topic"].lower():
        print("langchain")
        return langchain_chain # 如果问题类型包含"langchain"，则使⽤LangChain专家链
    # 其他类型的问题
    else:
        print("generic")
        return generic_chain # 使⽤通⽤回答链
    
# 创建完整的处理链
# 1 . ⾸先将问题分类并保留原始问题
# 2. 然后根据分类结果路由到相应的专家处理链处理
full_chain = {"topic": chain, "question": lambda x:x["question"]}| RunnableLambda(router) # 使⽤RunnableLambda包装路由函数
# 调⽤完整的处理链，输⼊问题
print(full_chain.invoke({"question": "我该如何使⽤openai？回答字数不超过100字。"}))