from pydantic import BaseModel,Field,model_validator
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import BaseMessage
from langchain_redis import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory 
from langchain_core.output_parsers import StrOutputParser # 导⼊字符串输出解析器
import os

# 使⽤DeepSeek模型
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")

llm = ChatDeepSeek(
    model='deepseek-ai/DeepSeek-R1',
    temperature=0,
    api_key=key,
    api_base=base,
    timeout=60,#增加请求超时限制
)

class Project(BaseModel):
    name: str = Field(..., description="可能想要买的商品的名称，只用一个词描述想要的商品,可以带修饰词描述，如果商品有多个，请列出商品名并用|分隔")
    # description: str = Field(..., description="对于每个想要买的商品的描述，用|分隔")


class metamessage:
    def __init__(self, mestype:type, contents):
        self.type = mestype
        self.content = contents
def ai_get_history(session_id:str):
    history = RedisChatMessageHistory(
        redis_url = "redis://47.98.143.59:6379",# Redis 连接URL
        session_id = session_id, # 会话ID
    )
    meshistory=[]
    for message in history.messages:
        meshistory.append(metamessage(type(message), message.content))
    return meshistory

# test
# print("历史消息：") # 显示当前历史消息
# for i in ai_get_history("user_1"):
#     print("说话对象：", i.type,"交流内容：" , i.content) # 打印每条消息的类型和内容

 #redis转基类 
from typing import List

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """⼀个简单的内存聊天历史实现"""
    messages: List[BaseMessage] = Field(default_factory=list)  # 存储消息的列表
    def add_messages(self, messages: List[BaseMessage]) -> None:
        """添加⼀组消息到存储中"""
        self.messages.extend(messages)

    def clear(self) -> None:
        """清空所有消息"""
        self.messages = []
def ai_get_keywords(session_id:str, question: str):
    router_chain = (
        PromptTemplate.from_template("""根据下⾯的⽤户问题，将其分类为`1` 或 `0`,请只回复⼀个词作为答案。如果问题只是关于推荐几个商品，且不涉及商品性价比等的，请回复`1`，否则回复`0`。
            <question>
            {question}
            </question>
            分类结果：""") | llm | StrOutputParser()
    )
    result = router_chain.invoke({"question": question}) # 调用路由链，获取问题类型
    
    print("问题类型：", result) # 打印问题类型
    if int(result) == 0: # 如果问题类型不是关于商品推荐
        return([], False) # 返回空列表和False
    
    # 实例化解析器、提示词模板
    parser = PydanticOutputParser(pydantic_object=Project)
    # 注意，提示词模板中需要部分格式化解析器的格式要求format_instructions 
    prompt = PromptTemplate(
        template="{history}\n回答⽤户的查询，查询出的商品名是关于日常商品的，如果结果有多个请用|分隔,商品描述如果有多个也请用|分隔.\n{format_instructions}\n{question}",
        input_variables=["history","question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
     # 将提示模板与模型组合成⼀个处理链
    chain = prompt | llm | parser
    redis_history = RedisChatMessageHistory(
        redis_url = "redis://47.98.143.59:6379",# Redis 连接URL
        session_id = session_id, # 会话ID
    )
    # 转换函数
    def get_by_session_id(session_id:str) -> BaseChatMessageHistory:
        temp = InMemoryHistory()
        temp.add_messages(redis_history.messages)  # 将Redis消息添加到临时内存历史中
        return temp
    # 创建⼀个带有消息历史的可运⾏对象
    chain_with_history  = RunnableWithMessageHistory(
        chain,# 基础链
        get_by_session_id,
        input_messages_key="question",  # 指定输⼊消息的键为"question"
        history_messages_key="history", # 指定历史消息的键为"history"
    )
    res = chain_with_history.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}}  # 配置会话ID为"foo"
    )
    # # 向历史记录中添加消息
    redis_history.add_user_message(question)
    pro = res.name.split("|")
    ai_message = "我认为你可能需要的商品是"
    for i in pro:
        ai_message += i + "、"
    redis_history.add_ai_message(ai_message)
    # print("商品名称：",res.name.split("|"))
    # print("商品描述：",res.description.split("|"))
    return (pro, True)

def ai_delete_history(session_id:str):
    history = RedisChatMessageHistory(
        redis_url = "redis://47.98.143.59:6379",# Redis 连接URL
        session_id = session_id, # 会话ID
    )
    history.clear()  # 清除聊天历史


def ai_recommend(session_id:str, question:str):
    pass

#test函数
# def test():
#     ai_delete_history("user_1") # 清除历史记录
#     print("处理请求中。。。")
#     print(ai_get_keywords("user_1", "我想买个戴在手上的")) # 测试函数
#     print("按1继续")
#     if input() == "1":
#         print("处理请求中。。。")
#         print(ai_get_keywords("user_1", "最好是金包银的"))
#     print("按2继续")
#     if input() == "2":
#         print("处理请求中。。。")
#         print("历史消息：") # 显示当前历史消息
#         for i in ai_get_history("user_1"):
#             print("说话对象：", i.type,"交流内容：" , i.content) # 打印每条消息的类型和内容

# test() # 运行测试函数