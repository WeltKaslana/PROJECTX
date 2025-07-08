# 引⼊JSON依赖包
from pydantic import BaseModel,Field,model_validator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import BaseMessage, AIMessage # 导⼊消息基类和AI消息类
from typing import List
import os

 # 这⾥我们使⽤全局变量来存储聊天消息历
# 这样可以更容易地检查它以查看底层结果。
store = {} # 创建空字典⽤于存储不同会话的历史记录
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """⼀个简单的内存聊天历史实现"""
    messages: List[BaseMessage] = Field(default_factory=list)  # 存储消息的列表
    def add_messages(self, messages: List[BaseMessage]) -> None:
        """添加⼀组消息到存储中"""
        self.messages.extend(messages)

    def clear(self) -> None:
        """清空所有消息"""
        self.messages = []

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    """根据会话ID获取对应的聊天历史,如果不存在则创建新的聊天历史"""
    if session_id not in store:
        store[session_id] = InMemoryHistory()  # 如果会话ID不存在，则创建新的聊天历史
    return store[session_id]  # 返回对应会话ID的聊天历史

# 使⽤DeepSeek模型
from dotenv import load_dotenv

load_dotenv()
# print("Hello from hellochain!")
key = os.getenv("SILICONFLOW_API_KEY")
base = os.getenv("SILICONFLOW_API_BASE")
llm = ChatDeepSeek(
    model='deepseek-ai/DeepSeek-R1',
    temperature=0,
    api_key=key,
    api_base=base,
    timeout=60,#增加请求超时限制
)
# 创建⼀个聊天提示模板，包含消息占位符
prompt = ChatPromptTemplate.from_messages(
  [
    ("system", "你是⼀个擅⻓{ability}的助⼿"),# 系统⻆⾊提示，使⽤ability 变量定义助⼿专⻓
    MessagesPlaceholder(variable_name="history"),  # 添加消息历史占位符
    ("human", "{question}"),  # ⼈类⻆⾊提示，使⽤question变量
  ]
 )
 # 将提示模板与模型组合成⼀个处理链
chain = prompt | llm
 # 创建⼀个带有消息历史的可运⾏对象
chain_with_history  = RunnableWithMessageHistory(
    chain,# 基础链
    get_by_session_id,
    input_messages_key="question",  # 指定输⼊消息的键为"question"
    history_messages_key="history", # 指定历史消息的键为"history"
)
 # ⾸次调⽤链，询问余弦的含义
print(chain_with_history.invoke(
    {"ability": "math", "question": "余弦函数是什么？"},# 输⼊参数
    config={"configurable": {"session_id": "foo"}} # 配置会话ID为"foo"
 ))
# 打印存储中的历史记录
# 此时包含第⼀次对话的问题和回答
print(store)

 # 第⼆次调⽤链，询问余弦函数的反函数
# 由于使⽤相同的会话ID "foo"，模型会记住之前的对话历史
chain_with_history.invoke(
    {"ability": "math", "question": "之前的对话内容是什么？"},
    config={"configurable": {"session_id": "foo"}},
)
print(store)